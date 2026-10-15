---
id: sched-multicore-topology-queues
title: Hardware topology, cache affinity and run queues
level: advanced
minutes: 3
sourceLesson: sched-multicore
summary: Logical CPUs can share core resources and caches, so thread count is not physical-core capacity.
---

Everything so far assumed one CPU. Servers may expose many logical CPUs, arranged in hardware-dependent hierarchies of SMT threads, cores, caches and memory nodes. The scheduler now answers two questions: *which* thread runs next, and *where*. Getting "where" wrong costs cache misses, remote memory accesses, and, inside containers, whole periods of enforced idleness.
## The hardware the scheduler sees

```
Socket / NUMA node 0        node 1
+-----------------------+   +-------
| L3 (shared)           |   | L3 ...
| core0     core1  ...  |   |
| [t0 t1]   [t2 t3]     |   |
| L1/L2     L1/L2       |   |
+--------local DRAM-----+   +-------
```

- **SMT siblings** (hyper-threads) share one core's execution units and L1/L2 caches. Resource contention can make two busy siblings slower than using separate physical cores; the effect depends on the workloads.
- **Cores in one CPU socket** may form several cache-sharing groups, especially across chiplets. Many designs share an L3 within a group; the exact layout is hardware-specific.
- **NUMA nodes** each have their own memory. Reaching another node's memory goes over an interconnect and is slower.

A thread that has been running on a CPU has a **warm cache** there: its working set is in L1, L2 and L3. Move it, and it pays to reload that state. This is **cache affinity**, and it is the central tension of multicore scheduling: keep threads where their data is, but don't leave CPUs idle while work waits elsewhere.
## One queue or many?

OSTEP frames the two basic designs:

| Design | Pros | Cons |
|---|---|---|
| Single shared queue | Simple, balanced by construction | Lock contention, poor affinity |
| Per-CPU queues | Scalable, natural affinity | Load imbalance |

In a simple global-queue design, scheduling decisions contend for one lock and may move tasks between CPUs. The scaling limit and cache cost depend on implementation and workload; a global queue can also incorporate affinity heuristics.

With **per-CPU run queues**, each CPU normally uses its own queue lock rather than one lock shared by every CPU, and threads tend to stay put. The cost is **load imbalance**: CPU 0 might have four runnable threads while CPU 1 is idle. The fix is **task migration**, moving threads between queues, typically by **work stealing**: an idle or lightly loaded CPU pulls work from a busier one.

Linux has used per-CPU run queues since the O(1) scheduler in 2.6.0. Go's runtime, Java's ForkJoinPool and Tokio use the same per-worker-queue-plus-stealing idea in user space.

## Key takeaways
- Logical CPUs can share core resources and caches, so thread count is not physical-core capacity.
- Per-CPU queues reduce shared contention and preserve locality but can become imbalanced.
- Migration balances work at the cost of moving away from warm data.

## Further reading
- [Multiprocessor Scheduling (Advanced) — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-sched-multi.pdf)
- [Scheduler Domains — Linux kernel docs](https://docs.kernel.org/scheduler/sched-domains.html)
- [CFS Bandwidth Control — Linux kernel docs](https://docs.kernel.org/scheduler/sched-bwc.html)
- [Control Group v2 — Linux kernel docs](https://docs.kernel.org/admin-guide/cgroup-v2.html)
- [sched_setaffinity(2) — Linux manual page](https://man7.org/linux/man-pages/man2/sched_setaffinity.2.html)
- [numa(7) — Linux manual page](https://man7.org/linux/man-pages/man7/numa.7.html)
- [Non-uniform memory access — Wikipedia](https://en.wikipedia.org/wiki/Non-uniform_memory_access)
- [Go 1.25 release notes (container-aware GOMAXPROCS)](https://go.dev/doc/go1.25)
