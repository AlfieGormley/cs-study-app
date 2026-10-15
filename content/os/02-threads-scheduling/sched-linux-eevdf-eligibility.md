---
id: sched-linux-eevdf-eligibility
title: EEVDF: eligibility before virtual deadline
level: advanced
minutes: 5
sourceLesson: sched-linux
summary: Eligibility excludes tasks already ahead of their fair service.
---

## EEVDF: fairness plus deadlines

**Earliest Eligible Virtual Deadline First** comes from a 1995 paper by Ion Stoica and Hussein Abdel-Wahab. Peter Zijlstra's implementation became the fair-class scheduler in Linux 6.6. Weights, nice and the red-black tree stay; the *picking rule* changes.

The following equations explain an idealised single-run-queue model. Actual kernels also apply feature settings, clamping, preemption protection and hierarchical group accounting.

Two ideas:

1. **Lag.** Compare the service a task should have received on the ideal CPU with what it actually got. Positive lag means it is owed CPU; negative means it has had more than its share. In practice the kernel computes the weighted average vruntime of the queue, and a task is **eligible** if its vruntime is no more than that average (lag of zero or more):

```formula
V = (w_1 v_1 + … + w_n v_n) / W
W = w_1 + … + w_n
lag_i = w_i(V − v_i)
lag_i ≥ 0  when  v_i ≤ V
where
V: the weighted average vruntime of the run queue, in nanoseconds (ns)
w_1, w_n, w_i: the weights of the tasks, from their nice values
v_1, v_n, v_i: the vruntimes of the tasks, in ns
n: the number of runnable tasks in the queue
…: "and so on" for every task in between
W: the total weight of the queue
lag_i: a weight-scaled service-lag measure, in weight-scaled nanoseconds; its sign indicates owed service or over-service. With the reference weight 1024 used for these virtual clocks, divide this measure by 1024 to express service in real CPU-time nanoseconds
ns: nanoseconds, billionths of a second
≥, ≤: greater than or equal to, less than or equal to
In words: a task whose vruntime is at or behind the queue's average has had no more than its fair share, so it may be picked.
```

2. **Virtual deadline.** Each task requests a slice (by default the base slice). Its deadline is its vruntime plus that slice scaled by weight:

```formula
d_i = v_i + (1024r_i) / w_i
where
d_i: task i's virtual deadline, in nanoseconds (ns)
v_i: task i's vruntime, in ns
r_i: the slice task i asks for, in ns
w_i: task i's weight; 1024 for nice 0
ns: nanoseconds, billionths of a second
In words: a task's deadline is where its vruntime would be after one full slice; a shorter slice puts that deadline earlier.
```

The rule: **among eligible tasks, run the one with the earliest virtual deadline.**

Eligibility keeps it fair: nobody who is ahead of their share gets picked. Deadlines add latency control: a task asking for a **shorter slice** gets an earlier deadline, so it runs sooner, though in smaller pieces. Over time it gets the same total share.

**Worked example: short slice, same weight.** A and B are both nice 0 (weight 1024) with vruntime 0. A uses a 3 ms slice; B asks for 1 ms. Both are eligible, because both vruntimes equal the average, 0.

```formula
d_A = 0 ms + 3 ms × 1024 / 1024
d_A = 3 ms
d_B = 0 ms + 1 ms × 1024 / 1024
d_B = 1 ms
v_B = 0 ms + 1 ms = 1 ms
d_B = 1 ms + 1 ms = 2 ms
where
d_A, d_B: the virtual deadlines of A and B, in milliseconds (ms)
v_B: B's vruntime after it has run for 1 ms
ms: milliseconds, thousandths of a second
In words: B's deadline is earlier, so B runs first, for 1 ms; its next deadline is then 2 ms.
```

B now waits for A to catch up before it is eligible again, so neither gets more than its half. B simply gets its half in smaller, more frequent pieces.

In the checked Linux 6.12 source the unscaled base slice is 0.75 ms; the default logarithmic scaling gives 3 ms at eight or more CPUs. Tunables and later kernels can differ. Since Linux 6.12 a normal task can request its own slice, between 0.1 ms and 100 ms, through the `sched_runtime` field of `sched_setattr()`.

Lag also needs care for sleepers. A task that sleeps with negative lag shouldn't wipe out its debt by sleeping briefly. Linux 6.12 introduced deferred dequeue: an over-served sleeping task can remain represented on the run queue in a "deferred dequeue" state so its lag decays, rather than simply resetting it.

> [!note] Is CFS gone?
> The name lingers: the fair class still lives in `kernel/sched/fair.c`, and many docs and tools still say CFS. Weights, nice, vruntime, group scheduling and CFS bandwidth control all carried over. What changed is how the next task is chosen and how preemption is decided.

## Key takeaways
- Eligibility excludes tasks already ahead of their fair service.
- Among eligible tasks, the earliest virtual deadline wins; a shorter requested slice changes service timing.
- Virtual deadlines are fairness coordinates, not application wall-clock deadlines; weight still controls long-run share.

## Further reading
- [CFS Scheduler — Linux kernel docs](https://docs.kernel.org/scheduler/sched-design-CFS.html)
- [EEVDF Scheduler — Linux kernel docs](https://docs.kernel.org/scheduler/sched-eevdf.html)
- [An EEVDF CPU scheduler for Linux — LWN](https://lwn.net/Articles/925371/)
- [Completing the EEVDF scheduler — LWN](https://lwn.net/Articles/969062/)
- [Deadline Task Scheduling — Linux kernel docs](https://docs.kernel.org/scheduler/sched-deadline.html)
- [Real-Time group scheduling — Linux kernel docs](https://docs.kernel.org/scheduler/sched-rt-group.html)
- [sched(7) — Linux manual page](https://man7.org/linux/man-pages/man7/sched.7.html)
- [EEVDF selection and lag — Linux 6.12 source](https://raw.githubusercontent.com/torvalds/linux/v6.12/kernel/sched/fair.c)
