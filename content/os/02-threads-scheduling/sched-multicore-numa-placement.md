---
id: sched-multicore-numa-placement
title: Place memory near the threads that use it
level: advanced
minutes: 3
sourceLesson: sched-multicore
summary: New private anonymous pages commonly follow the first write under local policy, subject to allocation and migration rules.
---

## NUMA: memory has an address *and* a location

On a multi-socket server, each node's memory is local to its cores. Remote memory access cost and interconnect bandwidth depend on the machine and workload.

> [!note] Content gap
> No reproducible machine-specific NUMA measurements accompany this lesson, so no universal remote/local latency multiplier is provided. `numactl --hardware` shows the nodes and a distance table (10 means local; remote nodes are larger, commonly around 20).

Linux normally prefers local allocation. For new private anonymous memory, the first write fault commonly allocates a page near the executing CPU. Explicit policies, cpusets, fallback under memory pressure, huge pages and later migration can change placement. That causes a classic bug:

> [!example] The single-threaded initialiser
> A program allocates and zeroes a 64 GiB array in its main thread on node 0, then starts 32 worker threads spread across both nodes. Assume the main thread stays on node 0, local memory is sufficient, writes fault in new pages and no policy or migration changes placement. The pages then start on node 0. Half the workers make every access remotely, and node 0's memory bandwidth is shared by everyone. Fix: initialise each slice from the thread that will use it, or interleave.

Tools and policies:

- `numactl --cpunodebind=0 --membind=0 ./db` runs a process on node 0's CPUs with node 0's memory.
- `numactl --interleave=all` spreads pages round robin across nodes: distributed allocation rather than guaranteed per-thread locality. It can reduce concentration on one node, but does not guarantee removal of all hot spots. Often a good choice for large shared caches, such as a database buffer pool.
- **Automatic NUMA balancing** (since Linux 3.8, `kernel.numa_balancing`): the kernel periodically unmaps pages to sample which node touches them through "hinting faults", then migrates pages towards their users, or tasks towards their memory. It helps long-running, well-partitioned workloads, at the cost of some overhead.
- `numastat -p <pid>` shows where a process's memory actually lives.

The scheduler is NUMA-aware: its top-level scheduling domain balances reluctantly across nodes, because moving a thread can turn accesses to its existing memory into remote accesses; cache hits and pages already elsewhere are exceptions.

## Key takeaways
- New private anonymous pages commonly follow the first write under local policy, subject to allocation and migration rules.
- Initialising each worker’s slice can preserve locality; interleaving distributes allocation instead.
- Remote/local cost depends on hardware and workload; use NUMA tools rather than a universal multiplier.

## Further reading
- [Multiprocessor Scheduling (Advanced) — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-sched-multi.pdf)
- [Scheduler Domains — Linux kernel docs](https://docs.kernel.org/scheduler/sched-domains.html)
- [CFS Bandwidth Control — Linux kernel docs](https://docs.kernel.org/scheduler/sched-bwc.html)
- [Control Group v2 — Linux kernel docs](https://docs.kernel.org/admin-guide/cgroup-v2.html)
- [sched_setaffinity(2) — Linux manual page](https://man7.org/linux/man-pages/man2/sched_setaffinity.2.html)
- [numa(7) — Linux manual page](https://man7.org/linux/man-pages/man7/numa.7.html)
- [Non-uniform memory access — Wikipedia](https://en.wikipedia.org/wiki/Non-uniform_memory_access)
- [Go 1.25 release notes (container-aware GOMAXPROCS)](https://go.dev/doc/go1.25)
- [NUMA memory policy — Linux kernel documentation](https://docs.kernel.org/admin-guide/mm/numa_memory_policy.html)
