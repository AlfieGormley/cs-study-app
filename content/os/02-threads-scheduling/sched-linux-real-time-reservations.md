---
id: sched-linux-real-time-reservations
title: Real-time priorities and deadline admission
level: advanced
minutes: 4
sourceLesson: sched-linux
summary: FIFO has no quantum; RR rotates tasks only within equal RT priorities.
---

## Real-time classes

For audio, industrial control and low-latency trading, fairness is the wrong goal. The `rt` class gives **strict priorities** from 1 to 99 (higher wins):

- **SCHED_FIFO**: runs until it blocks, yields or is preempted by a higher RT priority. No time slice at all.
- **SCHED_RR**: the same, but threads at *equal* priority rotate with a time slice (100 ms by default, `sched_rr_timeslice_ms`).

```python
import os

# Needs CAP_SYS_NICE or
# sufficient RLIMIT_RTPRIO
os.sched_setscheduler(
    0, os.SCHED_FIFO, os.sched_param(50))

# Confirm this thread’s policy if permitted.
print(os.sched_getscheduler(0)
      == os.SCHED_FIFO)  # True on success
```

From the shell: `chrt -f 50 ./audio-engine`, and `chrt -p <pid>` to inspect.

> [!warning] A runaway FIFO thread
> A `SCHED_FIFO` thread stuck in a busy loop never yields, so nothing below it runs on that CPU: not your shell, not `kill`. Linux guards against this. RT throttling commonly limits RT work to 950 ms per 1 s (`sched_rt_runtime_us` / `sched_rt_period_us`). Linux 6.12 also introduced a deadline-class fair server that can supply CPU to fair tasks. These are distinct mechanisms; behaviour depends on kernel version, configuration and tunables.
## SCHED_DEADLINE

Since Linux 3.14, the top policy is **SCHED_DEADLINE**. Instead of a priority, a task declares three numbers:

- **Runtime parameter**: CPU time budget for the reservation per period;
- **Deadline parameter**: by when the job should finish, relative to its release;
- **Period parameter**: the reservation’s nominal repeating interval.

```
chrt -d --sched-runtime  5000000 \
        --sched-deadline 10000000 \
        --sched-period  16666666 0 ./render
```

That says "5 ms of CPU every 16.7 ms frame, finished within 10 ms". The kernel schedules deadline tasks by **Earliest Deadline First**, and uses the Constant Bandwidth Server to stop any task exceeding its runtime. It also performs **admission control**. Each task's **utilisation** is the fraction of one CPU it reserves, and the kernel refuses a new task if the total would go over the permitted limit:

```formula
U = t_run / T
U = 5 ms / 16.7 ms ≈ 0.30
U_1 + U_2 + … + U_n ≤ 0.95M
where
U: one task's utilisation, the fraction of a CPU it reserves (0.30 means 30 %)
t_run: the task's runtime per period, in milliseconds (ms)
T: the task's period, in ms
U_1, U_2, U_n: the utilisations of all n deadline tasks, including the new one
n: the number of deadline tasks
…: "and so on"
M: the number of CPUs in the group of CPUs being checked (its root domain); on chips mixing big and little cores the kernel sums the CPUs' relative capacities instead
0.95: the default limit per CPU, from sched_rt_runtime_us / sched_rt_period_us = 950000 / 1000000
≤: less than or equal to
≈: approximately equal to
ms: milliseconds, thousandths of a second
In words: the render task reserves about 30 % of a CPU, and all deadline tasks together may reserve at most 95 % of each CPU by default.
```

If the new task does not fit, `sched_setattr()` fails with `EBUSY`. From Linux 6.12 the fair server described above is itself a deadline reservation (by default 50 ms in every 1 s, 5 % of each CPU) counted in the same total, so in the checked 6.12 source ordinary deadline tasks can reserve only about 90 % of each CPU unless the fair server is reconfigured. Admission checks reserve bandwidth; acceptance alone is not a universal proof that application deadlines will be met. Worst-case execution time, blocking, deadline versus period, CPU topology and scheduling assumptions still matter. The kernel documentation distinguishes schedulability tests from the simpler utilization admission test.

## Key takeaways
- FIFO has no quantum; RR rotates tasks only within equal RT priorities.
- Deadline scheduling reserves runtime, deadline and period parameters and rejects excess bandwidth reservations.
- Admission alone is not a proof of all application deadlines; blocking, execution bounds and topology still matter.

## Further reading
- [CFS Scheduler — Linux kernel docs](https://docs.kernel.org/scheduler/sched-design-CFS.html)
- [EEVDF Scheduler — Linux kernel docs](https://docs.kernel.org/scheduler/sched-eevdf.html)
- [An EEVDF CPU scheduler for Linux — LWN](https://lwn.net/Articles/925371/)
- [Completing the EEVDF scheduler — LWN](https://lwn.net/Articles/969062/)
- [Deadline Task Scheduling — Linux kernel docs](https://docs.kernel.org/scheduler/sched-deadline.html)
- [Real-Time group scheduling — Linux kernel docs](https://docs.kernel.org/scheduler/sched-rt-group.html)
- [sched(7) — Linux manual page](https://man7.org/linux/man-pages/man7/sched.7.html)
