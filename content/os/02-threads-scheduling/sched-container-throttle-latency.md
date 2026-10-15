---
id: sched-container-throttle-latency
title: Trace throttling and its effect on request latency
level: advanced
minutes: 3
sourceLesson: sched-multicore
summary: Several runnable threads can consume an aggregate CPU budget before the period ends.
---

## How throttling wrecks tail latency

**Worked example: two CPUs of quota, eight busy threads.** A container has `cpu.max = 200000 100000` and a server with 8 worker threads, on a 32-core host. In an idealised model, all 8 run simultaneously from the period boundary, with no other contention, overhead, burst credit or carried local runtime. Eight threads on eight CPUs burn 8 ms of CPU time for every millisecond of wall-clock time, so:

```formula
t_run = Q / n = 200 ms / 8 = 25 ms
t_thr = P − t_run = 100 ms − 25 ms
t_thr = 75 ms
t_lat = (P − t_a) + t_cpu
t_lat = (100 − 26) ms + 5 ms = 79 ms
where
t_run: how long into each period the quota lasts, in milliseconds (ms)
Q: the quota per period, 200 ms of CPU time
n: the number of threads running at once, 8
t_thr: how long the whole container is throttled (stopped) for in each period, in ms
P: the period, 100 ms
t_lat: the latency of a request that arrives while the container is throttled, in ms
t_a: when the request arrives, measured from the start of the period: 26 ms here
t_cpu: the CPU time the request needs, 5 ms here
ms: milliseconds, thousandths of a second
In words: eight threads use up a two-CPU budget in a quarter of the period, then everything stops for the other three quarters, and a request that arrives during the stop waits for the next period.
```

So for the remaining **75 ms** of each period nothing in the container runs, and a request arriving 26 ms into the period has a latency of at least 79 ms; queueing behind existing work can add more. Average usage is "2 CPUs, within limit", so dashboards look fine.

The symptom is p99 latency far above p50 while CPU usage looks modest. Check `cpu.stat`:

```
nr_periods 36000
nr_throttled 9100
throttled_usec 412000000
```

The fraction of periods that ended in throttling is one counter divided by the other:

```formula
f_thr = nr_throttled / nr_periods
f_thr = 9100 / 36000 ≈ 0.25
where
f_thr: the fraction of enforcement periods in which the group ran out of quota
nr_throttled: the number of periods in which the group was throttled
nr_periods: the number of periods in which the group had runnable work
≈: approximately equal to (rounded)
In words: about one period in four ended with the group out of quota.
```

Here a quarter of periods were throttled. Ways out:

- **Size thread pools to the quota, not the host.** Eight threads chewing through two CPUs' quota in a quarter of the period is worse than two threads using it smoothly.
- **Remove CPU limits** for latency-sensitive services and rely on requests (weights) for fairness. The trade-off is weaker isolation from competing workloads; inherited parent quotas can still throttle the group.
- **Allow bursting**: `cpu.max.burst` (Linux 5.14+) lets a group bank unused quota for short spikes.
- **Use exclusive CPUs** (eligible Guaranteed containers under Kubernetes static CPU management; whole cores require appropriate policy options) when you need both isolation and predictability.

## Key takeaways
- Several runnable threads can consume an aggregate CPU budget before the period ends.
- Requests arriving during throttling wait for service to resume and may also queue behind other work.
- Compare throttled periods with enforcement periods and test concurrency, quotas and isolation changes.

## Further reading
- [Multiprocessor Scheduling (Advanced) — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-sched-multi.pdf)
- [Scheduler Domains — Linux kernel docs](https://docs.kernel.org/scheduler/sched-domains.html)
- [CFS Bandwidth Control — Linux kernel docs](https://docs.kernel.org/scheduler/sched-bwc.html)
- [Control Group v2 — Linux kernel docs](https://docs.kernel.org/admin-guide/cgroup-v2.html)
- [sched_setaffinity(2) — Linux manual page](https://man7.org/linux/man-pages/man2/sched_setaffinity.2.html)
- [numa(7) — Linux manual page](https://man7.org/linux/man-pages/man7/numa.7.html)
- [Non-uniform memory access — Wikipedia](https://en.wikipedia.org/wiki/Non-uniform_memory_access)
- [Go 1.25 release notes (container-aware GOMAXPROCS)](https://go.dev/doc/go1.25)
