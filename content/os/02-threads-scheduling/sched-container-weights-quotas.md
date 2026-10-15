---
id: sched-container-weights-quotas
title: Separate CPU shares from CPU quota
level: advanced
minutes: 2
sourceLesson: sched-multicore
summary: Weight sets relative shares only when groups compete.
---

## Containers: shares versus quotas

Containers use cgroups to control CPU in two very different ways.

| Control | cgroup v2 file | Behaviour |
|---|---|---|
| Weight | `cpu.weight` | Share *under contention* |
| Quota | `cpu.max` | Hard cap, even when idle CPUs exist |

**Weight** (default 100) is proportional sharing between groups, just like nice between threads. If the machine is otherwise idle, a low-weight container can still use every CPU. It's *work-conserving*.

A **CPU quota** is set through CFS bandwidth control. `cpu.max` holds two numbers, "quota period", in microseconds. Dividing one by the other tells you how many CPUs' worth of time the group may use:

```formula
N_eff = Q / P
N_eff = 200000 µs / 100000 µs = 2
where
N_eff: the group's quota-to-period capacity ceiling in CPUs' worth of service; it can be fractional and is not an affinity mask
Q: the quota, the CPU time the whole group may use in each period, in microseconds (µs); 200000 µs = 200 ms here
P: the period, the length of each accounting window, in µs; 100000 µs = 100 ms here
µs: microseconds, millionths of a second
In words: 200 ms of CPU time in every 100 ms window is the same as keeping two CPUs fully busy.
```

So `200000 100000` means 200 ms of CPU time per 100 ms period, 2 CPUs' worth. Fair-class CPU time is charged across the group. Exhausted local bandwidth allocations cause throttling even with idle CPUs. Ancestor quotas, per-CPU runtime accounting and configured burst credit also affect the exact timeline.

In Kubernetes, a pod's CPU **request** becomes its cgroup weight, and its CPU **limit** becomes its `cpu.max` quota (with the default 100 ms period).

## Key takeaways
- Weight sets relative shares only when groups compete.
- Quota limits aggregate CPU time per period, even when unused host CPUs exist.
- The quota-to-period ratio expresses a capacity ceiling; ancestor limits and accounting details also apply.

## Further reading
- [Multiprocessor Scheduling (Advanced) — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-sched-multi.pdf)
- [Scheduler Domains — Linux kernel docs](https://docs.kernel.org/scheduler/sched-domains.html)
- [CFS Bandwidth Control — Linux kernel docs](https://docs.kernel.org/scheduler/sched-bwc.html)
- [Control Group v2 — Linux kernel docs](https://docs.kernel.org/admin-guide/cgroup-v2.html)
- [sched_setaffinity(2) — Linux manual page](https://man7.org/linux/man-pages/man2/sched_setaffinity.2.html)
- [numa(7) — Linux manual page](https://man7.org/linux/man-pages/man7/numa.7.html)
- [Non-uniform memory access — Wikipedia](https://en.wikipedia.org/wiki/Non-uniform_memory_access)
- [Go 1.25 release notes (container-aware GOMAXPROCS)](https://go.dev/doc/go1.25)
