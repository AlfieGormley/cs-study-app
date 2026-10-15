---
id: sched-linux-cfs-sleep-slices
title: Classic CFS sleeper placement and slices
level: advanced
minutes: 3
sourceLesson: sched-linux
summary: Classic CFS bounds a returning sleeper’s credit rather than replaying all missed service.
---

## Sleepers and new tasks

A task that sleeps for a minute would wake with a tiny vruntime and monopolise the CPU while it "caught up". CFS prevents this with `min_vruntime`, a monotonic floor tracking the smallest vruntime in the queue. A waking task's vruntime is raised to roughly `min_vruntime` minus a small bonus (half a latency period), so interactive tasks get a modest head start, not a minute's worth:

```formula
v_wake = max(v_old, v_min − L / 2)
where
v_wake: the sleeper's vruntime when it wakes, in milliseconds (ms) here (nanoseconds in the kernel)
max(a, b): the larger of the two values a and b
v_old: the vruntime the task had when it went to sleep
v_min: min_vruntime, the smallest vruntime in the run queue (it only ever increases)
L: the classic CFS target latency, in milliseconds (ms); 24 ms with default logarithmic scaling at eight or more online CPUs
ms: milliseconds, thousandths of a second
In words: a task that slept briefly keeps its own vruntime; one that slept a long time is moved up to half a target latency below the queue's minimum vruntime, so it gets a small head start and nothing more.
```

This was classic CFS behaviour, in kernels before 6.6, with its default `GENTLE_FAIR_SLEEPERS` setting, which halves the bonus (without it the bonus was a whole target latency). EEVDF, from 6.6, handles sleepers through lag instead. New tasks start near `min_vruntime` too.
## Latency and slices

CFS had no fixed quantum. It aimed to run every runnable task once within a **target latency**, with a **minimum slice** so that hundreds of tasks wouldn't each get microseconds. Both defaults grow a little on machines with more CPUs, because more CPUs share the load:

```formula
k = 1 + ⌊log_2(min(N_cpu, 8))⌋
L = 6 ms × k
g = 0.75 ms × k
k = 1 + ⌊log_2(8)⌋ = 1 + 3 = 4
L = 24 ms,  g = 3 ms
where
k: the scaling factor, from 1 (one CPU) to 4 (8 or more CPUs)
⌊x⌋: floor: round x down to a whole number
log_2(x): the base-2 logarithm of x, the power you raise 2 to in order to get x (log_2(8) = 3)
min(a, b): the smaller of the two values a and b
N_cpu: the number of CPUs online; counting stops at 8
L: the target latency, in milliseconds (ms)
g: the minimum slice (sched_min_granularity), in ms
ms: milliseconds, thousandths of a second
In words: start from 6 ms and 0.75 ms and multiply both by a factor that grows by one each time the CPU count doubles, up to 8 CPUs.
```

On a 4-CPU machine, for example, the factor is 3, giving 18 ms and 2.25 ms.

That worked, but latency was a side effect of fairness. There was no way to say "this task wants short, frequent slices", so CFS grew wake-up heuristics to keep desktops snappy, and these were hard to reason about.

## Key takeaways
- Classic CFS bounds a returning sleeper’s credit rather than replaying all missed service.
- Target latency and minimum granularity were scaled CFS tunables, not universal application latency guarantees.
- The historical CFS sleeper rule differs from EEVDF lag handling.

## Further reading
- [CFS Scheduler — Linux kernel docs](https://docs.kernel.org/scheduler/sched-design-CFS.html)
- [EEVDF Scheduler — Linux kernel docs](https://docs.kernel.org/scheduler/sched-eevdf.html)
- [An EEVDF CPU scheduler for Linux — LWN](https://lwn.net/Articles/925371/)
- [Completing the EEVDF scheduler — LWN](https://lwn.net/Articles/969062/)
- [Deadline Task Scheduling — Linux kernel docs](https://docs.kernel.org/scheduler/sched-deadline.html)
- [Real-Time group scheduling — Linux kernel docs](https://docs.kernel.org/scheduler/sched-rt-group.html)
- [sched(7) — Linux manual page](https://man7.org/linux/man-pages/man7/sched.7.html)
- [Classic CFS placement and tunables — Linux 6.5 source](https://raw.githubusercontent.com/torvalds/linux/v6.5/kernel/sched/fair.c)
