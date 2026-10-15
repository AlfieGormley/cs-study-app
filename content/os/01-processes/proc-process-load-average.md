---
id: proc-process-load-average
sourceLesson: proc-process-abstraction
title: "Interpreting Linux load average"
level: basic
minutes: 3
summary: "Linux load counts runnable tasks and tasks in uninterruptible waits."
---

Linux load counts runnable tasks and tasks in uninterruptible waits. This lesson focuses on interpreting linux load average.

> [!warning] Load average counts `D`
> Linux's load average counts tasks in `R` *and* `D`. A load of 40 on an 8-core box doesn't necessarily mean CPU saturation; it might be 35 processes stuck on a hung NFS mount. Check `top` for many `D` processes and low CPU use.

How is the number itself made? About every 5 seconds the kernel counts the tasks in `R` or `D` and folds that count into three moving averages, one for each of the 1, 5 and 15-minute figures that `uptime` and `top` print:

```formula
n = N_R + N_D
α = e^{−(Δt / τ)}
L_new = αL_old + (1 − α)n
where
n: the number of tasks counted at this sample
N_R: tasks running or runnable (state R)
N_D: tasks in uninterruptible sleep (state D)
α: alpha, the weight kept from the old average, between 0 and 1
e: Euler's number, about 2.718; e^{x} is the exponential function
Δt: the time between samples, about 5 seconds
τ: tau, the averaging period: 60 s, 300 s or 900 s for the 1, 5 and 15-minute figures
L_old: the load average before this sample
L_new: the load average after this sample
In words: each sample nudges the average a small step towards the current count of R and D tasks; the longer the period, the smaller the step.
```

Worked example: an idle machine (load 0) suddenly has 40 tasks stuck in `R` or `D`. After one minute, which is 12 samples, the 1-minute figure is:

```formula
α = e^{−(5 s / (60 s))} ≈ 0.920
L_k = n(1 − α^k)
L_12 = 40 × (1 − 0.920^12)
L_12 ≈ 40 × 0.63 ≈ 25
where
α: alpha, the weight each sample keeps from the old average, for the 1-minute figure
e: Euler's number, about 2.718
s: second
L_k: the 1-minute load average after k samples, starting from 0
n: the steady count of R and D tasks, here 40
k: the number of 5-second samples taken so far; 12 samples is one minute
L_12: the load average after 12 samples, that is, after one minute
≈: approximately equal to (rounded)
In words: each sample keeps 92 % of the old average and adds 8 % of the current count, so after one minute the figure has covered only about 63 % of the way from 0 to 40.
```

The figure only approaches 40 after several minutes. That lag is why a load spike shows up first in the 1-minute figure and only later in the 15-minute one. The kernel actually does this arithmetic in fixed-point integers, so its constants differ slightly in the last digits.

## Key takeaways
- Linux load counts runnable tasks and tasks in uninterruptible waits.
- Exponential averaging smooths changes; load alone does not prove CPU saturation.

## Further reading
- [The Abstraction: The Process — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-intro.pdf)
- [The Abstraction: Address Spaces — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-intro.pdf)
- [proc(5) — Linux manual page](https://man7.org/linux/man-pages/man5/proc.5.html)
- [Process control block — Wikipedia](https://en.wikipedia.org/wiki/Process_control_block)
- [Process state — Wikipedia](https://en.wikipedia.org/wiki/Process_state)
- [Address space layout randomization — Wikipedia](https://en.wikipedia.org/wiki/Address_space_layout_randomization)
- [Linux load-average implementation](https://raw.githubusercontent.com/torvalds/linux/master/kernel/sched/loadavg.c)
