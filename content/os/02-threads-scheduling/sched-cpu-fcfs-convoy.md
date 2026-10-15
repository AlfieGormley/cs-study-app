---
id: sched-cpu-fcfs-convoy
title: Trace FCFS and the convoy effect
level: basic
minutes: 2
sourceLesson: sched-cpu-basics
summary: FCFS serves arrival order without preempting a running job.
---

## First-come, first-served (FCFS)

Run jobs in arrival order, each to completion. It's a simple FIFO queue and is non-preemptive.

Three jobs arrive at time 0 in the order P1, P2, P3, with CPU bursts of 24, 3 and 3 ms:

```
|          P1          | P2 | P3 |
0                     24   27   30
```

| Job | Burst | Waiting | Turnaround |
|---|---|---|---|
| P1 | 24 | 0 | 24 |
| P2 | 3 | 24 | 27 |
| P3 | 3 | 27 | 30 |

To compare schedules with one number, take the average waiting time: add every job's waiting time and divide by the number of jobs.

```formula
W_avg = (W_1 + W_2 + W_3) / 3
W_avg = (0 + 24 + 27) ms / 3
W_avg = 51 ms / 3 = 17 ms
where
W_avg: the average waiting time across the three jobs, in milliseconds (ms)
W_1, W_2, W_3: the waiting times of P1, P2 and P3, from the table, in ms
ms: milliseconds, thousandths of a second
In words: add up how long each job sat in the queue and share the total equally between the jobs.
```

The average waiting time is **17 ms**. If the short jobs had arrived first (P2, P3, P1), the waits would be 0, 3 and 6 ms: an average of (0 + 3 + 6) / 3 = **3 ms**. Same work, nearly six times better.

This is the **convoy effect**: short jobs stuck behind a long one, like cars behind a lorry on a single-lane road. With a mix of one CPU-bound and several I/O-bound threads, the I/O-bound ones queue behind the hog while the disks sit idle, then all finish their I/O together while the CPU sits idle.

## Key takeaways
- FCFS serves arrival order without preempting a running job.
- Short jobs behind a long CPU burst suffer the convoy effect.
- Compute waiting times from the stated arrivals and schedule before averaging them.

## Further reading
- [Scheduling: Introduction — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-sched.pdf)
- [Scheduling (computing) — Wikipedia](https://en.wikipedia.org/wiki/Scheduling_(computing))
- [Round-robin scheduling — Wikipedia](https://en.wikipedia.org/wiki/Round-robin_scheduling)
- [Shortest job next — Wikipedia](https://en.wikipedia.org/wiki/Shortest_job_next)
- [Convoy effect — Wikipedia](https://en.wikipedia.org/wiki/Convoy_effect)
