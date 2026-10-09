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

The memory value is just the limit in bytes. Kubernetes' `Mi` suffix is a power-of-two unit:

```formula
M_max = 512 Mi
M_max = 512 × 1024 × 1024 B
M_max = 536870912 B
where
M_max: the memory limit as written into memory.max
Mi: mebibyte (MiB), 1024 × 1024 = 1,048,576 bytes; Kubernetes writes it Mi
B: byte, eight bits
In words: 512Mi is 512 binary megabytes, which is 536,870,912 bytes.
```

### CPU request → weight

A CPU request is first converted to cgroup v1–style **CPU shares**, where 1024 shares meant one whole CPU:

```formula
S = floor(R_m × 1024 / 1000)
S = floor(250 × 1024 / 1000) = 256
where
S: the CPU shares value, clamped to the range 2–262,144 (no unit)
R_m: the CPU request in millicores (m); 1000m = 1 CPU, so 250m is a quarter of a CPU
floor: round down to a whole number
In words: shares are the request scaled so that one full CPU is worth 1024; a 250m request gives 256 shares.
```

The shares are then converted to `cpu.weight` (range 1–10,000, default 100). Weights matter only under **CPU contention**. A sufficiently parallel container may exceed its request when allowed by limits, affinity and ancestors. Eligible competing sibling cgroups receive relative weight-based service; this is not a flat global split of every container on the node.

The shares-to-weight formula has changed over time. Older runc used a linear mapping that stretches the shares range 2–262,144 onto the weight range 1–10,000:

```formula
W_old = 1 + floor((S − 2) × 9999 / 262142)
W_old = 1 + floor(1022 × 9999 / 262142)
W_old = 1 + 38 = 39
where
W_old: the cpu.weight the older linear mapping writes (no unit)
S: the CPU shares value, here 1024 (one CPU)
floor: round down to a whole number
In words: the linear mapping turns one CPU's worth of shares into weight 39, well below the default weight of 100.
```

The current upstream opencontainers/cgroups implementation uses a curve instead, chosen so that the minimum, default and maximum line up:

```formula
x = log_2(S)
y = (x^2 + 125 × x) / 612 − 7 / 34
W_new = ⌈10^y⌉
where
x: the base-2 logarithm of the shares value
S: the CPU shares value (2 to 262,144)
log_2: logarithm base 2: the power you raise 2 to in order to get the number; log_2(1024) = 10
y: an intermediate exponent (no unit)
W_new: the cpu.weight the curve writes (no unit)
⌈ ⌉: ceiling: round up to the next whole number
In words: the curve maps 2 shares to weight 1, 1024 shares (one CPU) to the default weight 100, and 262,144 shares to the maximum 10,000.
```

For one CPU (1024 shares):

```formula
x = log_2(1024) = 10
y = (100 + 1250) / 612 − 7 / 34 = 2
W_new = ⌈10^2⌉ = 100
where
x: the base-2 logarithm of 1024 shares
log_2: logarithm base 2; 2^10 = 1024
y: the exponent, here exactly 2
W_new: the resulting cpu.weight
⌈ ⌉: ceiling: round up to a whole number
In words: one CPU's worth of shares lands exactly on the default weight of 100 under the curve.
```

The deployed runc/library version determines whether that mapping is used. The curve preserves selected endpoints/defaults, not every ratio: actual weights and CPU-contention shares can change across implementations. Inspect cpu.weight on the deployed runtime instead of assuming a 2:1 request always becomes exactly a 2:1 weight.

### CPU limit → quota and throttling

A CPU limit becomes CFS bandwidth control. `cpu.max = "50000 100000"` means 50 ms of CPU time per 100 ms period, summed across **all threads** in the cgroup. Runnable fair-class tasks are throttled when the applicable budget is exhausted. Periods, runtime slices, burst configuration and ancestor quotas affect observed timing.

One possible latency cause is quota exhaustion. In an idealised case with four continuously running threads on four available CPUs, no burst credit and no tighter ancestor limit:

```formula
t_wall = Q / N
t_wall = 50 ms / 4 = 12.5 ms
t_thr = P − t_wall
t_thr = 100 ms − 12.5 ms = 87.5 ms
where
t_wall: wall-clock time from the start of a period until the quota is used up, in milliseconds (ms)
Q: the quota: CPU time the cgroup may use per period, here 50 ms (a 500m limit)
N: threads busy at the same time, each on its own CPU, here 4
t_thr: how long the whole cgroup is then throttled, in ms
P: the quota period, here 100 ms
ms: millisecond, one thousandth of a second
In words: four threads burn a 50 ms budget in 12.5 ms of real time, then every thread in the cgroup waits 87.5 ms for the next period.
```

A request arriving just after the quota runs out waits up to 87.5 ms, even when its average over a longer, partly idle measurement interval is below the limit. `cpu.stat` exposes this as `nr_throttled` and `throttled_usec`. The usual fixes are to raise or remove CPU limits (keeping requests), or to size thread pools to the limit. Runtime parallelism settings and container-aware resource detection can help avoid excessive runnable work; their purpose and behavior extend beyond quota throttling.

The quota itself comes from the limit in the same way the shares come from the request. Kubernetes writes a minimum quota of 1 ms:

```formula
Q = max(1000, floor(L_m × P / 1000))
Q = floor(500 × 100000 / 1000) µs
Q = 50000 µs
where
Q: the quota written as the first number of cpu.max, in microseconds (µs)
L_m: the CPU limit in millicores (m); 500m is half a CPU
P: the quota period, here 100000 µs (100 ms)
max: the larger of its two inputs; here it enforces a 1000 µs (1 ms) minimum
floor: round down to a whole number
µs: microsecond, one millionth of a second
In words: the quota is the limit's fraction of a CPU times the period, so a 500m limit allows 50 ms of CPU time in every 100 ms period.
```

A simplified model of the ordinary quota/share conversion as code (integer millicores; excludes feature flags, pod budgets and special policies):

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

Note that a 2-CPU limit (2000m) gives a quota of 2000 × 100000 / 1000 = 200,000 µs (200 ms), larger than the 100 ms period. That's allowed, because the quota is summed across CPUs.

### Memory limit → memory.max and the OOM killer

Memory allocation can be throttled/reclaimed, for example through memory.high; that differs from periodically pausing runnable CPU work. When usage in the container's cgroup hits `memory.max`, the kernel first tries to reclaim memory, mostly page cache. If that fails, the **cgroup OOM killer** kills a process inside that cgroup. If the container's process is killed and the runtime identifies OOM, termination commonly appears as OOMKilled with exit code 137. That number follows the shell convention for a process killed by a signal:

```formula
E = 128 + s
E = 128 + 9 = 137
where
E: the exit code reported for a process killed by a signal
s: the signal number; SIGKILL, which the OOM killer sends, is 9
In words: an exit code above 128 means "killed by signal (code minus 128)", so 137 means killed by SIGKILL.
```
 A killed child need not terminate the entire container, and exit 137 alone does not prove OOM.

As a useful shorthand, CPU quotas throttle and unrecoverable memory pressure can kill; allocation failures, reclaim and configuration create exceptions. Page cache counts towards the limit, so a container streaming large files can approach `memory.max` while its heap is small. That memory is reclaimable, though, so it is usually reclaimed rather than causing a kill. An `emptyDir` with `medium: Memory` is tmpfs, and its pages are charged to the writing container's cgroup. They cannot be discarded like clean disk cache; swap availability/configuration can allow shmem pages to leave RAM.

Memory requests don't set a cgroup limit by default. The scheduler uses them to place pods, and the kubelet uses them for node-pressure eviction and OOM ranking. MemoryQoS can configure protection/throttling according to the Kubernetes version and kubelet settings; inspect the actual memory.min, memory.low and memory.high values.

## QoS classes and who dies first

For ordinary Linux pods using container-level CPU/memory resources, the following summary applies. Pod-level resource specifications and critical-pod exceptions require additional rules:

| Class | Rule | `oom_score_adj` |
|---|---|---|
| Guaranteed | requests equal limits, CPU and memory, every container | −997 |
| Burstable | anything in between | 3 to 999 |
| BestEffort | no CPU/memory requests or limits | 1000 |

For a non-critical Burstable container without pod-level resource adjustments, the kubelet sets the adjustment from the share of node memory the container requests. The more memory it reserves, the lower (safer) its score:

```formula
A = 1000 − 1000 × M_req / M_node
A_set = min(max(3, A), 999)
where
A: the raw oom_score_adj before clamping (no unit); the kernel's range is −1000 to 1000
M_req: the container's memory request, in bytes (or any unit, as long as both use the same one)
M_node: the node's memory capacity, in the same unit
A_set: the value actually written, clamped to 3–999; the kubelet computes the floor as 1000 + (−997) = 3
max: the larger of its inputs
min: the smaller of its inputs
In words: subtract the requested fraction of node memory, scaled to 1000, from 1000, then keep the result between 3 and 999 so a Burstable container always ranks between Guaranteed and BestEffort.
```

A container requesting a quarter of node memory capacity gets 1000 − 1000 × 0.25 = 750, and one requesting 1% gets 1000 − 10 = 990. The kubelet computes 1000 × M_req / M_node with integer division (rounding down) before subtracting. The Kubernetes documentation writes the lower clamp as 2, but the kubelet source (`pkg/kubelet/qos/policy.go`) returns 3 for anything below 3.

Two separate mechanisms use these values:

1. **Node-pressure eviction** (kubelet). When `memory.available` drops below the hard threshold (100Mi by default on Linux), the kubelet terminates pods to reclaim memory. It ranks them first by whether their usage exceeds their requests, then by Pod priority, then by how far usage exceeds requests. Hard-pressure eviction uses no termination grace period. A controller may create a replacement pod; the original pod is not moved or rescheduled as the same object. Soft-threshold grace settings differ.
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

Writing this into every pod is error-prone, so Kubernetes has **Pod Security Admission**. You label a Kubernetes namespace with `pod-security.kubernetes.io/enforce=restricted`, and the API server rejects pods that do not meet the **restricted** Pod Security Standard. For ordinary Linux host-user-namespace pods, the selected Restricted policy version requires running as non-root, dropping ALL capabilities (only `NET_BIND_SERVICE` may be added back), `allowPrivilegeEscalation: false` and a RuntimeDefault or Localhost seccomp profile. The **baseline** standard blocks the worst options, such as privileged containers, host namespaces and `hostPath`.

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
