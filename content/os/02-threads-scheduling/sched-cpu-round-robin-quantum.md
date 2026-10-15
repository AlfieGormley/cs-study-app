---
id: sched-cpu-round-robin-quantum
title: Round robin: response versus switching cost
level: basic
minutes: 4
sourceLesson: sched-cpu-basics
summary: Round robin rotates runnable jobs after a quantum and lets short bursts finish early.
---

## Round robin (RR)

Give each job a fixed **time quantum** (time slice), then preempt it and put it at the back of the ready queue. RR is FCFS plus a timer, and it is the basis of most interactive scheduling.

Back to P1 = 24, P2 = 3 and P3 = 3, all at time 0, with a quantum of 4 ms:

```
| P1 | P2 | P3 |          P1          |
0    4    7   10                     30
```

P2 and P3 finish within their first quantum and leave early. P1 then runs alone, quantum after quantum.

| Job | Waiting | Turnaround | Response |
|---|---|---|---|
| P1 | 6 | 30 | 0 |
| P2 | 4 | 7 | 4 |
| P3 | 7 | 10 | 7 |

Averaging the columns:

```formula
W_avg = (6 + 4 + 7) ms / 3 = 17 ms / 3
W_avg ≈ 5.67 ms
R_avg = (0 + 4 + 7) ms / 3 = 11 ms / 3
R_avg ≈ 3.67 ms
where
W_avg: the average waiting time of the three jobs, in milliseconds (ms)
R_avg: the average response time: for each job, the clock time of its first run minus its arrival time (0 ms for all three), averaged, in ms
≈: approximately equal to (rounded to two decimal places)
ms: milliseconds, thousandths of a second
In words: round robin gets every job started quickly, which is what the low average response time measures.
```

Average waiting is about **5.67 ms** and average response time about **3.67 ms**, against 17 ms and 17 ms for FCFS in the original order (under FCFS a job's first run is also its only run, so its response time equals its waiting time).

> [!note] A tie-breaking convention
> When a job's quantum expires at the same moment a new job arrives, most textbooks put the new arrival in the queue first, then the preempted job. State your convention when you work these by hand; it can change the answer.
## Choosing the quantum

- **Too large**, and RR degenerates into FCFS: interactive jobs wait behind CPU hogs.
- **Too small**, and the CPU spends its time switching.

To see how much is wasted, assume every job uses its full quantum, so each quantum of useful work is followed by one context switch. The wasted fraction is the switch time divided by the whole cycle:

```formula
f = s / (q + s)
f = 0.1 ms / (10 ms + 0.1 ms) ≈ 0.0099
f = 0.1 ms / (1 ms + 0.1 ms) ≈ 0.091
where
f: the fraction of CPU time spent switching rather than running jobs (multiply by 100 for a percentage)
s: the time one context switch takes, in milliseconds (ms); 0.1 ms is an assumed illustrative figure, not a measurement
q: the time quantum, in ms
≈: approximately equal to (rounded)
ms: milliseconds, thousandths of a second
In words: the shorter the quantum, the bigger the share of each cycle that goes on switching.
```

With a 0.1 ms switch cost, a 10 ms quantum wastes about 1% and a 1 ms quantum about 9%, before counting cache effects.

Choose the quantum from measured burst lengths, latency goals and overhead. No workload trace or platform-specific measurement is supplied to justify a universal percentile target or slice range here.

RR has good response time and is fair, but its **average turnaround** can be poor when jobs are of similar length: with three 10 ms jobs and a 1 ms quantum, all three finish near 30 ms, whereas FCFS finishes them at 10, 20 and 30.
## Comparison

| Algorithm | Preemptive | Strength | Weakness |
|---|---|---|---|
| FCFS | No | Simple, no starvation | Convoy effect |
| SJF | No | Optimal avg wait | Needs burst length; starvation |
| SRTF | Yes | Even better avg wait | Same, plus more switches |
| RR | Yes | Response time, fairness | Turnaround; quantum tuning |

No real general-purpose OS uses any of these alone. Linux, Windows and macOS combine their ideas: priorities, time slices, and rewarding threads that block a lot. The following lessons build up to what Linux actually does.

## Key takeaways
- Round robin rotates runnable jobs after a quantum and lets short bursts finish early.
- State how arrivals and expired quanta are ordered when their timestamps tie.
- Small quanta improve first response but increase switching overhead; similar jobs can finish later overall.

## Further reading
- [Scheduling: Introduction — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-sched.pdf)
- [Scheduling (computing) — Wikipedia](https://en.wikipedia.org/wiki/Scheduling_(computing))
- [Round-robin scheduling — Wikipedia](https://en.wikipedia.org/wiki/Round-robin_scheduling)
- [Shortest job next — Wikipedia](https://en.wikipedia.org/wiki/Shortest_job_next)
- [Convoy effect — Wikipedia](https://en.wikipedia.org/wiki/Convoy_effect)
