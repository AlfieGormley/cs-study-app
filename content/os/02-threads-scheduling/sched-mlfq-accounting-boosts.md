---
id: sched-mlfq-accounting-boosts
title: Prevent gaming and starvation in MLFQ
level: intermediate
minutes: 3
sourceLesson: sched-priority-mlfq
summary: Count cumulative CPU consumption at a level, not just the latest uninterrupted burst.
---

## Rule 4 and gaming the scheduler

Early MLFQ designs had a gentler rule: *a job that gives up the CPU before its quantum expires keeps its priority*. That rewards interactive jobs, but it can be **gamed**. A job that runs for 9.9 ms of a 10 ms quantum, then issues a trivial I/O, stays at the top forever and gets nearly all the CPU.

Rule 4 closes the hole with better **accounting**: the scheduler tracks *total* CPU used at a level, not per burst. In the preceding feedback-trace unit, B uses 2 ms per burst. Dividing its allotment by the CPU it uses per burst gives the number of bursts before it is demoted:

```formula
n_bursts = A_level / t_burst
n_bursts = 10 ms / 2 ms = 5
where
n_bursts: how many bursts B can run at the top level before it is demoted
A_level: the time allotment at the top level, 10 ms here
t_burst: the CPU time B uses in each burst, 2 ms here
ms: milliseconds, thousandths of a second
In words: B's short bursts add up, and after five of them it has spent its whole allotment.
```

So after five bursts B drops to Q1. That is the cost of being game-proof: even a genuinely interactive job slowly sinks. Rule 5 lifts it back.
## Rule 5: the priority boost

Without boosts, two things go wrong:

- **Starvation**: many interactive jobs at the top can use all the CPU, and jobs in Q0 never run.
- **Changing behaviour**: a job that was CPU-bound (say, a program loading data) and then becomes interactive is stuck at the bottom.

Boosting everything to the top once every boost period fixes both. The length of that period is one of Ousterhout's "voodoo constants": too long and long jobs starve; too short and interactive jobs lose their advantage. Real systems tune it, or replace the boost with aging or decay of usage history.
## MLFQ in real systems

The cited historical Solaris documentation describes 60 time-sharing priorities and default quanta from 40 ms at priority 59 to 200 ms at priority 0; these are version/configuration-specific values. Windows uses 32 priority levels with dynamic boosts for threads that finish waiting on I/O or own the foreground window. FreeBSD's ULE scheduler computes an "interactivity score" from sleep and run times. Linux took a different route: since 2.6.23 (2007) its normal scheduler has been built on fairness rather than feedback queues, as the next lesson explains.

## Key takeaways
- Count cumulative CPU consumption at a level, not just the latest uninterrupted burst.
- Periodic boosts let long-waiting jobs run and let changed workloads regain priority.
- Queue counts, quanta and boost intervals are policy choices; historical system examples have version-specific values.

## Further reading
- [Scheduling: The Multi-Level Feedback Queue — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-sched-mlfq.pdf)
- [Glenn Reeves: what happened on Pathfinder — firsthand correction in RISKS](https://catless.ncl.ac.uk/Risks/19.54.html)
- [Priority inversion — Wikipedia](https://en.wikipedia.org/wiki/Priority_inversion)
- [Priority inheritance — Wikipedia](https://en.wikipedia.org/wiki/Priority_inheritance)
- [RT-mutex subsystem with PI support — Linux kernel docs](https://docs.kernel.org/locking/rt-mutex.html)
- [Multilevel feedback queue — Wikipedia](https://en.wikipedia.org/wiki/Multilevel_feedback_queue)
