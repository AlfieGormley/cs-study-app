---
id: sched-mlfq-feedback-trace
title: Learn job behaviour with feedback queues
level: intermediate
minutes: 3
sourceLesson: sched-priority-mlfq
summary: New jobs start at the top so genuinely short jobs can finish promptly.
---

## The multilevel feedback queue (MLFQ)

The deeper problem is that the OS doesn't know which jobs are short or interactive. SJF needs that knowledge; round robin ignores it. The **multilevel feedback queue**, first described by Corbató's CTSS in 1962 (part of the work that earned him the Turing Award), *learns* it by watching how jobs behave.

MLFQ keeps several ready queues, one per priority level. The textbook rules (as in OSTEP) are:

1. If job A has a higher priority than job B, A runs.
2. If A and B have the same priority, they share the CPU round robin.
3. A new job enters at the **highest** priority.
4. Once a job uses up its **time allotment** at a level, however many times it gave up the CPU along the way, it moves down one level.
5. After a fixed period (the boost period), move **every** job back to the top queue (the **priority boost**).

Lower queues usually get **longer quanta**: short slices at the top for responsiveness, long slices at the bottom where CPU-bound jobs live and switching overhead matters more.

```
Q2 (high)  10 ms slice  [new, interactive]
Q1         20 ms slice  [demoted once]
Q0 (low)   40 ms slice  [CPU-bound, RR]
```
## Why it approximates SJF

Rule 3 assumes every new job might be short. If it is, it finishes (or blocks) while still at the top, getting SJF-like treatment. If it isn't, Rule 4 pushes it down level by level until it sits with the other long jobs. The scheduler has learned the job is CPU-bound without being told.
## A worked trace

Three levels as above, with an allotment of one quantum per level. A CPU-bound job A arrives at 0. An interactive job B arrives at 50 and repeatedly runs for 2 ms, then waits 8 ms for I/O.

```
ms      0   10        30   50 52   60 62
Q2      [A ]               [B]     [B]
Q1          [A     ]
Q0                  [A   ]    [A  ]   [A
```

1. 0–10: A uses its full 10 ms at Q2 and is demoted.
2. 10–30: A uses 20 ms at Q1 and is demoted to Q0.
3. 30–50: A runs at Q0.
4. 50: B arrives at Q2 and preempts A immediately (Rule 1).
5. B runs 2 ms and blocks; A carries on until B's I/O completes at 60, when B preempts it again.

In the idealised zero-overhead trace, B runs immediately when ready; no measured wake-up latency is implied. A uses all the leftover time. That's the behaviour we want from a desktop.

## Key takeaways
- New jobs start at the top so genuinely short jobs can finish promptly.
- CPU-heavy jobs sink through queues with longer slices.
- Higher-priority arrivals preempt lower queues in the stated idealised policy.

## Further reading
- [Scheduling: The Multi-Level Feedback Queue — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-sched-mlfq.pdf)
- [Glenn Reeves: what happened on Pathfinder — firsthand correction in RISKS](https://catless.ncl.ac.uk/Risks/19.54.html)
- [Priority inversion — Wikipedia](https://en.wikipedia.org/wiki/Priority_inversion)
- [Priority inheritance — Wikipedia](https://en.wikipedia.org/wiki/Priority_inheritance)
- [RT-mutex subsystem with PI support — Linux kernel docs](https://docs.kernel.org/locking/rt-mutex.html)
- [Multilevel feedback queue — Wikipedia](https://en.wikipedia.org/wiki/Multilevel_feedback_queue)
