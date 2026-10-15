---
id: sched-cpu-shortest-job-traces
title: Trace SJF and shortest remaining time
level: basic
minutes: 4
sourceLesson: sched-cpu-basics
summary: Non-preemptive SJF selects the shortest available burst and then lets it finish.
---

## Shortest job first (SJF)

Always run the job with the **shortest next CPU burst**. When all jobs are available at once, SJF is provably optimal for average waiting time: moving a short job ahead of a long one reduces the short job's wait by more than it increases the long one's.

Now use staggered arrivals:

| Job | Arrival | Burst |
|---|---|---|
| P1 | 0 | 8 |
| P2 | 1 | 4 |
| P3 | 2 | 9 |
| P4 | 3 | 5 |

**Non-preemptive SJF.** At time 0 only P1 is there, so it runs to completion. At 8, P2 (4), P3 (9) and P4 (5) are waiting; the shortest is P2, then P4, then P3.

```
|   P1   |  P2  |  P4  |    P3    |
0        8     12     17         26
```

Each job runs in one piece, so its waiting time is simply its start time minus its arrival time:

```formula
W = t_start − t_arrive
W_P1 = (0 − 0) ms = 0 ms
W_P2 = (8 − 1) ms = 7 ms
W_P4 = (12 − 3) ms = 9 ms
W_P3 = (17 − 2) ms = 15 ms
W_avg = (0 + 7 + 9 + 15) ms / 4
W_avg = 31 ms / 4 = 7.75 ms
where
W: a job's waiting time, in milliseconds (ms)
t_start: the clock time at which the job starts running, read off the chart, in ms
t_arrive: the clock time at which the job arrives, from the table, in ms
W_P1, W_P2, W_P3, W_P4: the waiting times of P1, P2, P3 and P4, in ms
W_avg: the average waiting time over the four jobs, in ms
ms: milliseconds, thousandths of a second
In words: a job that is never interrupted waits only once, from its arrival until it starts, so subtract one from the other and average over the jobs.
```

The average waiting time is **7.75 ms**.
## Shortest remaining time first (SRTF)

The preemptive version: whenever a job arrives, compare its burst with the *remaining* time of the running job, and switch if it's shorter.

1. At 0 ms: P1 starts (remaining 8).
2. At 1 ms: P2 arrives needing 4, less than P1's remaining 7. Preempt; P2 runs.
3. At 2 ms and 3 ms: P3 (9) and P4 (5) arrive; neither beats P2's remaining 3 or 2.
4. At 5 ms: P2 done. Remaining: P1 7, P3 9, P4 5. P4 runs.
5. At 10 ms: P4 done. P1 (7) runs, then P3.

```
|P1| P2 |  P4  |   P1   |   P3    |
0  1    5     10       17        26
```

A preempted job can wait in several pieces (P1 waits from 1 to 10 ms), so "start minus arrival" no longer works. Instead take the job's whole time in the system and subtract the time it actually ran:

```formula
W = T_turn − t_burst
T_turn = t_done − t_arrive
W_P1 = ((17 − 0) − 8) ms = 9 ms
W_P2 = ((5 − 1) − 4) ms = 0 ms
W_P3 = ((26 − 2) − 9) ms = 15 ms
W_P4 = ((10 − 3) − 5) ms = 2 ms
W_avg = (9 + 0 + 15 + 2) ms / 4
W_avg = 26 ms / 4 = 6.5 ms
where
W: a job's total waiting time, in milliseconds (ms)
T_turn: the job's turnaround time, from arrival to completion, in ms
t_burst: the CPU time the job needs in total, from the table, in ms
t_done: the clock time at which the job finishes, read off the chart, in ms
t_arrive: the clock time at which the job arrives, from the table, in ms
W_P1, W_P2, W_P3, W_P4: the waiting times of P1, P2, P3 and P4, in ms
W_avg: the average waiting time over the four jobs, in ms
ms: milliseconds, thousandths of a second
In words: everything a job spends in the system that is not running is waiting, however many pieces it comes in.
```

The average is **6.5 ms**, better than non-preemptive SJF.

## Key takeaways
- Non-preemptive SJF selects the shortest available burst and then lets it finish.
- SRTF can preempt when a newly arrived burst is shorter than the running job’s remaining work.
- For a job that never blocks, waiting is turnaround minus total CPU service, even after preemptions.

## Further reading
- [Scheduling: Introduction — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-sched.pdf)
- [Scheduling (computing) — Wikipedia](https://en.wikipedia.org/wiki/Scheduling_(computing))
- [Round-robin scheduling — Wikipedia](https://en.wikipedia.org/wiki/Round-robin_scheduling)
- [Shortest job next — Wikipedia](https://en.wikipedia.org/wiki/Shortest_job_next)
- [Convoy effect — Wikipedia](https://en.wikipedia.org/wiki/Convoy_effect)
