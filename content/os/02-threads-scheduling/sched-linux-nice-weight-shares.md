---
id: sched-linux-nice-weight-shares
title: Turn nice weights into CPU shares
level: advanced
minutes: 4
sourceLesson: sched-linux
summary: Nice changes a task’s fair scheduling weight, not its scheduling class.
---

## Weights and nice

Nice values map to weights through a fixed table in the kernel. Nice 0 is 1024, and each step is a factor of about **1.25**, so the table is close to this formula:

```formula
w ≈ 1024 / (1.25^n)
w ≈ 1024 / (1.25^5) ≈ 335.54
w ≈ 1024 / (1.25^{−5}) = 3125
where
w: the task's weight, a plain number with no unit
n: the task's nice value, from −20 to 19
1.25^n: 1.25 raised to the power n (a negative n gives 1 divided by 1.25 raised to the power −n)
≈: approximately equal to; the real table is rounded and differs slightly
In words: each nice step up divides the weight by about 1.25, and each step down multiplies it by about 1.25.
```

The exact kernel values:

| Nice | Weight |
|---|---|
| −20 | 88761 |
| −5 | 3121 |
| 0 | 1024 |
| 1 | 820 |
| 5 | 335 |
| 19 | 15 |

Weights turn into CPU time like this: when several tasks in one fair group all want the CPU, each gets its weight divided by the total weight of the competitors.

```formula
s_i = w_i / (w_1 + w_2 + … + w_n)
s_0 = 1024 / (1024 + 820) ≈ 0.555
s_1 = 820 / (1024 + 820) ≈ 0.445
where
s_i: the share of CPU time task i gets, as a fraction (0.555 means 55.5 %)
w_i: task i's weight, from the table
w_1, w_2, w_n: the weights of all n competing tasks
n: the number of runnable tasks competing for the CPU
…: "and so on" for every task in between
s_0, s_1: the shares of a nice 0 task (weight 1024) and a nice 1 task (weight 820) competing alone
≈: approximately equal to (rounded)
In words: each task gets a slice of the CPU proportional to its weight.
```

So for two otherwise equal competitors in one fair group, moving one from nice 0 to nice 1 changes the split from 50/50 to about 55.5/44.5. The share change depends on the competitors. A higher weight makes vruntime grow *more slowly*, so it needs more real CPU service to reach the same virtual-clock advance. This explains the larger fair share under classic CFS and EEVDF; EEVDF additionally compares eligibility and virtual deadlines.

**Worked example: who gets what?** Three CPU-bound tasks in the same fair group share one CPU: A and B at nice 0, C at nice 5.

```formula
w_tot = 1024 + 1024 + 335 = 2383
s_A = s_B = 1024 / 2383 ≈ 0.43
s_C = 335 / 2383 ≈ 0.14
v_C = 10 ms × 1024 / 335 ≈ 30.6 ms
where
w_tot: the total weight of the three tasks
s_A, s_B, s_C: the CPU shares of A, B and C, as fractions (0.43 means 43 %)
v_C: how much C's vruntime grows when it runs for 10 ms of real time
ms: milliseconds, thousandths of a second
≈: approximately equal to (rounded)
In words: A and B each get about 43 % of the CPU and C about 14 %, because C's virtual clock runs about three times as fast.
```

Check with vruntime: after 10 ms of real time each, A and B gain 10 ms of vruntime, but C gains about 30.6 ms. C’s virtual runtime advances about three times as fast per unit of real execution, so its long-run CPU service is about a third of either nice 0 competitor’s. This is a service-time ratio, not a guarantee about how often dispatches occur.

Note what nice is *not*: it's not a strict priority. A nice 19 task alongside a nice 0 task still gets 15 / 1039, about 1.4%. That proportional share assumes competition within the same fair group, available CPU bandwidth and no overriding higher-class work.

## Key takeaways
- Nice changes a task’s fair scheduling weight, not its scheduling class.
- A task’s long-run share is its weight divided by the competitors’ total in the same fair group.
- The approximate geometric mapping explains the trend; the kernel uses an exact rounded weight table.

## Further reading
- [CFS Scheduler — Linux kernel docs](https://docs.kernel.org/scheduler/sched-design-CFS.html)
- [EEVDF Scheduler — Linux kernel docs](https://docs.kernel.org/scheduler/sched-eevdf.html)
- [An EEVDF CPU scheduler for Linux — LWN](https://lwn.net/Articles/925371/)
- [Completing the EEVDF scheduler — LWN](https://lwn.net/Articles/969062/)
- [Deadline Task Scheduling — Linux kernel docs](https://docs.kernel.org/scheduler/sched-deadline.html)
- [Real-Time group scheduling — Linux kernel docs](https://docs.kernel.org/scheduler/sched-rt-group.html)
- [sched(7) — Linux manual page](https://man7.org/linux/man-pages/man7/sched.7.html)
- [Exact scheduler weight table — Linux 6.12 source](https://raw.githubusercontent.com/torvalds/linux/v6.12/kernel/sched/core.c)
