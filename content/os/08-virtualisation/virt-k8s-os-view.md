---
id: virt-k8s-os-view
title: Kubernetes through the OS lens
level: advanced
minutes: 14
summary: What a pod really is on a Linux node, how requests and limits become cgroup files, why CPU limits throttle and memory limits kill, and how securityContext and RuntimeClass map onto the isolation tools from earlier lessons.
---

Kubernetes looks like a world of its own, with pods, QoS classes and security contexts. On a Linux node, many workload mechanisms use primitives from this module: namespaces, cgroups, overlayfs, capabilities, seccomp and, sometimes, a microVM.

If you can read a pod spec and predict the files under `/sys/fs/cgroup` and the namespaces in `/proc/<pid>/ns`, you can reason about an important subset of node resource and isolation problems. That's the goal of this lesson.

## From YAML to processes

When the scheduler assigns a pod to a node, that node's **kubelet** drives the container runtime over **CRI** (gRPC):

```
kubelet
 | RunPodSandbox  -> pause container,
 |                   netns, cgroup
 | (CNI plugin)   -> veth + pod IP
 | PullImage      -> layers, snapshots
 | CreateContainer, StartContainer
 v
containerd -> shim -> runc
                       |
                 your process
```

1. **RunPodSandbox.** In a common containerd/runc Linux setup, a sandbox process holds shared namespaces. The kubelet/runtime coordinate pod cgroups. Pause can also handle signals and reap children when used as namespace init; host namespaces and VM-backed sandboxes differ.
2. **CNI.** The runtime calls a CNI plugin (Calico, Cilium, the AWS VPC CNI and so on). It typically creates a **veth pair**, moves one end into the pod's network namespace as `eth0`, assigns the pod IP and sets up routes.
3. **Containers.** For each container, the runtime creates the requested mount/rootfs and PID isolation, and **joins** the sandbox's network, IPC and UTS namespaces with `setns()`.

### What a pod shares

| Namespace | Shared in pod? |
|---|---|
| net | Shared stack; localhost and pod IP(s) |
| ipc | SysV IPC and POSIX queues; /dev/shm is a mount |
| uts | Yes: one hostname |
| mnt | No: own root fs; volumes shared |
| pid | No, unless `shareProcessNamespace` |
| user | Host's, unless `hostUsers: false` |
| cgroup | Runtime-dependent namespace view |

For this native Linux example, shared namespaces and a parent cgroup help implement the pod's coordinated workload abstraction. They are not a complete cross-platform definition of a pod. A sidecar proxy can intercept a container's traffic because they share one network stack. An Istio init-container interception setup needs network-administration privileges; Istio CNI can instead arrange interception outside that init container.

With `shareProcessNamespace: true`, all containers share one PID namespace and the pause container becomes PID 1, reaping zombies. `kubectl exec` is CRI `Exec`, which becomes `runc exec`: a runtime helper configures namespace membership (including a fork for PID namespace entry), root, cgroup and process security before executing the command.

## Requests and limits become cgroup files

In the conventional kubelet-managed native Linux layout, a pod has a parent cgroup with container cgroups underneath. With the systemd cgroup driver (the recommended setting, and it must match between kubelet and runtime), the tree looks like this:

```
/sys/fs/cgroup/kubepods.slice/
  kubepods-pod<uid>.slice/   (Guaranteed)
  kubepods-burstable.slice/
    kubepods-burstable-pod<uid>.slice/
      cri-containerd-<id>.scope
  kubepods-besteffort.slice/
```

For the following container-level example, assume cgroup v2, CPU quota enforcement, a 100 ms quota period and no pod-level resource override:

```
resources:
  requests: {cpu: 250m, memory: 256Mi}
  limits:   {cpu: 500m, memory: 512Mi}
```

| Spec | cgroup v2 file | Value |
|---|---|---|
| cpu limit 500m | `cpu.max` | `50000 100000` |
| cpu request 250m | `cpu.weight` | relative share |
| memory limit | `memory.max` | `536870912` |
| memory request | scheduling/priority; optional protection | configuration dependent |

### CPU request → weight

A CPU request is converted to cgroup v1–style **shares** (`millicores × 1024 / 1000`, so 250m gives 256) and then to `cpu.weight` (range 1–10,000, default 100). Weights matter only under **contention**. A sufficiently parallel container may exceed its request when allowed by limits, affinity and ancestors. Eligible competing sibling cgroups receive relative weight-based service; this is not a flat global split of every container on the node.

The shares-to-weight formula has changed over time. Older runc used a linear mapping where 1 CPU (1024 shares) became weight 39. The current upstream opencontainers/cgroups implementation uses a curve mapping 1024 shares to 100; the deployed runc/library version determines whether that mapping is used. The curve preserves selected endpoints/defaults, not every ratio: actual weights and contention shares can change across implementations. Inspect cpu.weight on the deployed runtime instead of assuming a 2:1 request always becomes exactly a 2:1 weight.

### CPU limit → quota and throttling

A CPU limit becomes CFS bandwidth control. `cpu.max = "50000 100000"` means 50 ms of CPU time per 100 ms period, summed across **all threads** in the cgroup. Runnable fair-class tasks are throttled when the applicable budget is exhausted. Periods, runtime slices, burst configuration and ancestor quotas affect observed timing.

One possible latency cause is quota exhaustion. In an idealised case with four continuously running threads on four available CPUs, no burst credit and no tighter ancestor limit:

```
period = 100 ms, quota = 50 ms
4 threads busy in parallel:
  50 ms / 4 = 12.5 ms wall to use quota
  then throttled for 87.5 ms
```

A request arriving just after the quota runs out waits up to 87.5 ms, even when its average over a longer, partly idle measurement interval is below the limit. `cpu.stat` exposes this as `nr_throttled` and `throttled_usec`. The usual fixes are to raise or remove CPU limits (keeping requests), or to size thread pools to the limit. Runtime parallelism settings and container-aware resource detection can help avoid excessive runnable work; their purpose and behavior extend beyond quota throttling.

A simplified model of the ordinary quota/share conversion (integer millicores; excludes feature flags, pod budgets and special policies):

```
PERIOD = 100_000  # microseconds

def cpu_max(limit_m):
    if limit_m is None:
        return f"max {PERIOD}"
    if limit_m <= 0:
        raise ValueError("positive limit")
    quota = max(1000,
                limit_m * PERIOD // 1000)
    return f"{quota} {PERIOD}"

def shares(request_m):
    if request_m < 0:
        raise ValueError("negative request")
    return min(262144,
        max(2, request_m * 1024 // 1000))

print(cpu_max(500))    # 50000 100000
print(cpu_max(2000))   # 200000 100000
print(cpu_max(None))   # max 100000
print(shares(250))     # 256
```

Note that a 2-CPU limit gives a quota (200 ms) larger than the period. That's allowed, because the quota is summed across CPUs.

### Memory limit → memory.max and the OOM killer

Memory allocation can be throttled/reclaimed, for example through memory.high; that differs from periodically pausing runnable CPU work. When usage in the container's cgroup hits `memory.max`, the kernel first tries to reclaim memory, mostly page cache. If that fails, the **cgroup OOM killer** kills a process inside that cgroup. If the container's process is killed and the runtime identifies OOM, termination commonly appears as OOMKilled with exit code 137. A killed child need not terminate the entire container, and exit 137 alone does not prove OOM.

As a useful shorthand, CPU quotas throttle and unrecoverable memory pressure can kill; allocation failures, reclaim and configuration create exceptions. Page cache counts towards the limit, so a container streaming large files can approach `memory.max` while its heap is small. That memory is reclaimable, though, so it is usually reclaimed rather than causing a kill. An `emptyDir` with `medium: Memory` is tmpfs, and its pages are charged to the writing container's cgroup. They cannot be discarded like clean disk cache; swap availability/configuration can allow shmem pages to leave RAM.

Memory requests don't set a cgroup limit by default. The scheduler uses them to place pods, and the kubelet uses them for eviction and OOM ranking. MemoryQoS can configure protection/throttling according to the Kubernetes version and kubelet settings; inspect the actual memory.min, memory.low and memory.high values.

## QoS classes and who dies first

For ordinary Linux pods using container-level CPU/memory resources, the following summary applies. Pod-level resource specifications and critical-pod exceptions require additional rules:

| Class | Rule | `oom_score_adj` |
|---|---|---|
| Guaranteed | requests = limits, CPU and memory, every container | −997 |
| Burstable | anything in between | 2 to 999 |
| BestEffort | no CPU/memory requests or limits | 1000 |

For a non-critical Burstable container without pod-level resource adjustments, the score is `1000 − 1000 × memoryRequest / nodeMemory`, clamped to the range 2–999. A container requesting a quarter of node memory capacity gets 750, and one requesting 1% gets 990.

Two separate mechanisms use these values:

1. **Node-pressure eviction** (kubelet). When `memory.available` drops below the hard threshold (100Mi by default on Linux), the kubelet evicts pods. It ranks them first by whether their usage exceeds their requests, then by Pod priority, then by how far usage exceeds requests. Hard-pressure eviction uses no termination grace period. A controller may create a replacement pod; the original pod is not moved or rescheduled as the same object. Soft-threshold grace settings differ.
2. **Kernel OOM killer** (node-wide). If memory runs out before the kubelet reacts, the kernel picks a victim by usage plus `oom_score_adj`. These adjustments bias victim selection; actual memory use, eligible scope and other factors matter. QoS class alone is not a strict universal kill ordering or a promise that a Guaranteed workload survives.

## securityContext is the last lesson in YAML

This is a container-level securityContext fragment; hostUsers belongs at pod spec level, while some fields can also be inherited from pod-level securityContext.

```
securityContext:
  runAsNonRoot: true
  runAsUser: 10001
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities: {drop: ["ALL"]}
  seccompProfile: {type: RuntimeDefault}
```

| Field | Kernel mechanism |
|---|---|
| `runAsUser` | `setuid()` before exec |
| `allowPrivilegeEscalation: false` | `no_new_privs` |
| `capabilities.drop` | runtime capability-set configuration |
| `seccompProfile` | seccomp-bpf filter |
| `readOnlyRootFilesystem` | root mounted read-only |
| `privileged: true` | broad runtime privilege relaxation |
| pod `spec.hostUsers: false` | user namespace |

Writing this into every pod is error-prone, so Kubernetes has **Pod Security Admission**. You label a namespace with `pod-security.kubernetes.io/enforce=restricted`, and the API server rejects pods that do not meet the **restricted** Pod Security Standard. For ordinary Linux host-user-namespace pods, the selected Restricted policy version requires running as non-root, dropping ALL capabilities (only `NET_BIND_SERVICE` may be added back), `allowPrivilegeEscalation: false` and a RuntimeDefault or Localhost seccomp profile. The **baseline** standard blocks the worst options, such as privileged mode, host namespaces and `hostPath`.

## RuntimeClass: choosing the boundary per pod

Sometimes the shared kernel is not enough. A **RuntimeClass** maps a name to a CRI runtime handler configured in containerd:

```
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata: {name: gvisor}
handler: runsc
---
spec:
  runtimeClassName: gvisor
```

With the handler installed, configured and supported on the selected node, the pod can use a gVisor sandbox (`runsc`) or a Kata microVM (`kata`) instead of runc. The pod model survives, because in Kata the "pod sandbox" *is* the VM and the containers run inside it. RuntimeClass can also declare `overhead`, so the scheduler accounts for the VM's extra memory and CPU.

## Pitfalls

- **CPU limits on latency-sensitive services** cause throttling at low average utilisation. Watch `nr_throttled`.
- **No container memory limit** can allow growth until other constraints apply. Pod/ancestor limits, admission defaults and node policy may still constrain it; inspect the effective configuration rather than predicting a guaranteed failure.
- **Mismatched cgroup drivers** (kubelet on systemd, runtime on cgroupfs) give two managers of one tree and unstable nodes.
- **Thinking `localhost` is private.** Every container in a pod shares one network namespace, so any of them can reach the others' ports.
- **`hostPath`, `hostNetwork` and `hostPID`** expose selected host resources or share specific namespaces; they do not remove every namespace or security control. Reserve them for node agents.

## Key takeaways

- A typical native Linux pod sandbox anchors shared namespaces; host settings, process sharing and alternative runtimes change the details.
- kubelet → CRI → containerd → shim → runc; CNI wires a veth into the pod's network namespace.
- CPU requests become relative `cpu.weight`; CPU limits become `cpu.max` quota per 100 ms and cause throttling, even at low average use.
- Memory limits drive accounting/reclaim/OOM behavior; exit 137 alone does not prove OOM. QoS influences OOM adjustments, while kubelet eviction uses its own pressure ranking.
- Security settings configure credentials and kernel restrictions. Admission checks selected policy rules; RuntimeClass selects a preconfigured supported runtime handler.

> [!note] Deployment gaps
> This lesson was source-checked and its arithmetic model executed, but no Kubernetes cluster was created. Runtime-specific namespace layouts, admission exceptions, QoS feature gates and cgroup files must be checked on the deployed version. Exact latency and OOM outcomes are not guaranteed by the examples.

## Further reading

- [Pods — Kubernetes docs](https://kubernetes.io/docs/concepts/workloads/pods/)
- [Resource management for pods and containers — Kubernetes docs](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [About cgroup v2 — Kubernetes docs](https://kubernetes.io/docs/concepts/architecture/cgroups/)
- [Pod Quality of Service classes — Kubernetes docs](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/)
- [Node-pressure eviction — Kubernetes docs](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/)
- [Pod Security Standards — Kubernetes docs](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [Runtime Class — Kubernetes docs](https://kubernetes.io/docs/concepts/containers/runtime-class/)
