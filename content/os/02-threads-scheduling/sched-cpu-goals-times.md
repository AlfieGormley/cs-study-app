---
id: sched-cpu-goals-times
title: Measure turnaround, waiting and response
level: basic
minutes: 3
sourceLesson: sched-cpu-basics
summary: Response measures arrival to first service; turnaround measures arrival to completion.
---

A machine can have more runnable threads than available logical CPUs; at other times many or all threads are asleep. The **scheduler** is the part of the kernel that decides which runnable thread gets each core next, and for how long.

Every scheduling algorithm is an answer to one question: *when the CPU becomes free, who goes next?* The answers differ because they optimise for different goals.
## What are we optimising?

| Metric | Meaning | Want |
|---|---|---|
| CPU utilisation | Fraction of time the CPU is busy | High |
| Throughput | Jobs finished per unit time | High |
| Turnaround time | Arrival to completion | Low |
| Waiting time | Time spent ready but not running | Low |
| Response time | Arrival to *first* run | Low |
| Fairness | Similar jobs get similar shares | Even |

The three times in the table are all worked out from moments on one clock that starts at 0 when we begin watching. Each is a subtraction. These identities hold for a job that never blocks, so it needs the CPU for one stretch (one CPU burst, defined in the next unit) and is either running or waiting in the queue:

```formula
T_turn = t_done − t_arrive
T_wait = T_turn − t_burst
T_resp = t_first − t_arrive
where
T_turn: the turnaround time: how long the job spent in the system, from arriving to finishing, in milliseconds (ms)
t_done: the completion time: the clock time at which the job finished, in ms
t_arrive: the arrival time: the clock time at which the job arrived and became ready to run, in ms
T_wait: the waiting time: the total time the job sat ready in the queue without running, in ms
t_burst: the burst time: how much CPU time the job needed in total, in ms
T_resp: the response time: how long the job waited before it got the CPU for the first time, in ms
t_first: the clock time at which the job first started running, in ms
ms: milliseconds, thousandths of a second
In words: turnaround is everything from arrival to finish; take away the time the job spent actually running and what is left is time spent waiting; response time counts only the wait before the very first run.
```

For example, a job that arrives at 2 ms, first runs at 5 ms, needs 4 ms of CPU in total and finishes at 12 ms has a turnaround time of 12 − 2 = 10 ms, a waiting time of 10 − 4 = 6 ms and a response time of 5 − 2 = 3 ms. If a job also blocks for I/O, the time it spends blocked is neither running nor waiting in the ready queue, so you would subtract that too before calling the remainder "waiting".

These goals conflict. A batch system crunching overnight jobs wants **throughput** and doesn't care about response time. An interactive desktop or a web server wants **low latency**: a keypress should be handled within milliseconds even if a compile is running. Fairness can cost throughput, because switching between jobs wastes time and cache.

## Key takeaways
- Response measures arrival to first service; turnaround measures arrival to completion.
- Subtract CPU service and any blocked time to distinguish ready-queue waiting from time in the system.
- Choose metrics for the workload; fairness, overhead and throughput can conflict.

## Further reading
- [Scheduling: Introduction — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-sched.pdf)
- [Scheduling (computing) — Wikipedia](https://en.wikipedia.org/wiki/Scheduling_(computing))
- [Round-robin scheduling — Wikipedia](https://en.wikipedia.org/wiki/Round-robin_scheduling)
- [Shortest job next — Wikipedia](https://en.wikipedia.org/wiki/Shortest_job_next)
- [Convoy effect — Wikipedia](https://en.wikipedia.org/wiki/Convoy_effect)
