---
id: virt-pod-memory-oom
title: Memory charges, tmpfs and OOM evidence
level: advanced
minutes: 3
sourceLesson: virt-k8s-os-view
summary: Clean cache can be reclaimed, while retained tmpfs and anonymous pages need other relief.
---

This unit focuses on memory charges, tmpfs and OOM evidence. It builds on the earlier virtualisation units in this module.

## Memory limit → memory.max and the OOM killer

Memory allocation can be throttled/reclaimed, for example through memory.high; that differs from periodically pausing runnable CPU work. When usage in the container's cgroup hits `memory.max`, the kernel first tries to reclaim memory, mostly page cache. If that fails, the **cgroup OOM killer** kills a process inside that cgroup. If the container's process is killed and the runtime identifies OOM, termination commonly appears as OOMKilled with exit code 137. That number follows the shell convention for a process killed by a signal:

```formula
E = 128 + s
E = 128 + 9 = 137
where
E: the exit code reported for a process killed by a signal
s: the signal number; SIGKILL, which the OOM killer sends, is 9
In words: when this convention reports a known signal death, SIGKILL becomes 137. A program can also explicitly exit with 137, so the number alone does not establish signal termination or OOM.
```
 A killed child need not terminate the entire container, and exit 137 alone does not prove OOM.

As a useful shorthand, CPU quotas throttle and unrecoverable memory pressure can kill; allocation failures, reclaim and configuration create exceptions. Page cache counts towards the limit, so a container streaming large files can approach `memory.max` while its heap is small. That memory is reclaimable, though, so it is usually reclaimed rather than causing a kill. An `emptyDir` with `medium: Memory` is tmpfs, and its pages are charged to the writing container's cgroup. They cannot be discarded like clean disk cache; swap availability/configuration can allow shmem pages to leave RAM.

Memory requests don't set a cgroup limit by default. The scheduler uses them to place pods, and the kubelet uses them for node-pressure eviction and OOM ranking. MemoryQoS can configure protection/throttling according to the Kubernetes version and kubelet settings; inspect the actual memory.min, memory.low and memory.high values.

## Key takeaways

- Clean cache can be reclaimed, while retained tmpfs and anonymous pages need other relief.
- Exit 137 reports a signal convention and cannot establish OOM by itself.

## Further reading

- [Pods — Kubernetes docs](https://kubernetes.io/docs/concepts/workloads/pods/)
- [Resource management for pods and containers — Kubernetes docs](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [About cgroup v2 — Kubernetes docs](https://kubernetes.io/docs/concepts/architecture/cgroups/)
- [Pod Quality of Service classes — Kubernetes docs](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/)
- [Node-pressure eviction — Kubernetes docs](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/)
- [Pod Security Standards — Kubernetes docs](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [Runtime Class — Kubernetes docs](https://kubernetes.io/docs/concepts/containers/runtime-class/)
