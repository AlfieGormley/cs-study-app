---
id: virt-pod-processes
title: How a native Linux pod becomes processes
level: advanced
minutes: 3
sourceLesson: virt-k8s-os-view
summary: A native Linux sandbox commonly anchors shared namespaces before application containers start.
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

## Key takeaways

- A native Linux sandbox commonly anchors shared namespaces before application containers start.
- A pod shares network visibility; exec helpers also configure root, credentials and resource/security settings.

## Further reading

- [Pods — Kubernetes docs](https://kubernetes.io/docs/concepts/workloads/pods/)
- [Resource management for pods and containers — Kubernetes docs](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [About cgroup v2 — Kubernetes docs](https://kubernetes.io/docs/concepts/architecture/cgroups/)
- [Pod Quality of Service classes — Kubernetes docs](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/)
- [Node-pressure eviction — Kubernetes docs](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/)
- [Pod Security Standards — Kubernetes docs](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [Runtime Class — Kubernetes docs](https://kubernetes.io/docs/concepts/containers/runtime-class/)
