---
id: mem-container-budgets
sourceLesson: mem-in-practice
title: Container kills and runtime memory budgets
level: advanced
minutes: 2
summary: OOMKilled and code 137 need event evidence to identify the actual failure scope.
---

### Kubernetes

A container's `resources.limits.memory` becomes its cgroup's `memory.max`. `requests.memory` is used by the scheduler to place pods (and, with the optional MemoryQoS feature, to set protection).

A limit-related OOM can kill a container process, commonly reported as **OOMKilled** with code **137**, following the usual shell convention for a process killed by a signal:

```formula
c = 128 + s
c = 128 + 9 = 137
where
c: the exit code reported for a process killed by a signal
s: the signal number; SIGKILL is 9 and SIGTERM is 15 (giving 143)
In words: in the stated signal-reporting convention, SIGKILL corresponds to 137. A program can also exit explicitly with that code, so the number alone does not establish the cause.
```

 Code 137 alone does not prove OOM, and OOMKilled alone does not prove the container's own limit was the cause: node/global OOM is possible. **Kubelet eviction** is separate; memory-pressure ranking considers whether usage exceeds requests, Pod Priority, and usage relative to requests.

### Runtimes in containers

Managed runtimes must size themselves to the cgroup, not the host:

- **JVM**: supported HotSpot versions can use container limits in heap ergonomics, but cgroup-version support, vendor/version and flags matter. MaxRAMPercentage commonly defaults to 25, with small-memory and other ergonomics affecting actual heap sizing. Metaspace, stacks, JIT, GC structures and native/direct buffers need additional room. Verify the running JVM's detected limit and flags.
- **Go**: `GOMEMLIMIT` (Go 1.19+) sets a soft budget for memory managed by the Go runtime; it excludes some external memory and may be exceeded to avoid excessive GC.
- **Node.js**: `--max-old-space-size` limits V8 old-space, not the entire heap or total process RSS.

Budget measured non-heap peaks, cache and allocation spikes below the container limit. A fixed 20–30% margin is not a guarantee for every runtime or workload.

## Key takeaways
- OOMKilled and code 137 need event evidence to identify the actual failure scope.
- Kubelet eviction differs from kernel cgroup OOM.
- A managed-heap limit leaves native memory, stacks, cache and runtime overhead to budget.

## Further reading
- [Overcommit accounting — Linux kernel docs](https://www.kernel.org/doc/html/latest/mm/overcommit-accounting.html)
- [Control Group v2 (memory controller) — Linux kernel docs](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html)
- [proc_pid_smaps(5) — Linux manual page](https://man7.org/linux/man-pages/man5/proc_pid_smaps.5.html)
- [Taming the OOM killer — LWN.net](https://lwn.net/Articles/317814/)
- [Resource management for pods and containers — Kubernetes docs](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [Redis administration (overcommit advice) — Redis docs](https://redis.io/docs/latest/operate/oss_and_stack/management/admin/)
- [AddressSanitizer — Clang docs](https://clang.llvm.org/docs/AddressSanitizer.html)
- [tracemalloc — Python docs](https://docs.python.org/3/library/tracemalloc.html)
