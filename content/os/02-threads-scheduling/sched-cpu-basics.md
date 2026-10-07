---
id: sched-cpu-basics
title: CPU scheduling basics
level: basic
minutes: 13
summary: What a scheduler is trying to optimise, CPU-bound versus I/O-bound work, preemption, and FCFS, SJF, SRTF and round robin worked through with Gantt charts.
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

Useful identities, for a job that never blocks:

```
turnaround = completion - arrival
waiting    = turnaround - burst
response   = first run  - arrival
```

These goals conflict. A batch system crunching overnight jobs wants **throughput** and doesn't care about response time. An interactive desktop or a web server wants **low latency**: a keypress should be handled within milliseconds even if a compile is running. Fairness can cost throughput, because switching between jobs wastes time and cache.

## CPU bursts and I/O bursts

Programs alternate between using the CPU (a **CPU burst**) and waiting for something (an **I/O burst**: disk, network, keyboard, a lock).

```
CPU-bound:  [=======CPU=======]..[=====CPU
I/O-bound:  [C]......io.....[C]......io...
```

- **CPU-bound** threads (video encoding, compiling, number crunching) have long bursts and rarely block.
- **I/O-bound** threads (a shell, an editor, a web server waiting on clients) have short bursts and block often.

Burst distributions depend on workload; interactive tasks often have short bursts between waits. A good scheduler lets I/O-bound threads run promptly when they wake. They need the CPU only briefly, then go back to waiting, which keeps both the CPU and the I/O devices busy.

## Preemptive versus cooperative

The scheduler can make a decision when a thread:

1. blocks (for example on I/O) or yields;
2. finishes;
3. becomes ready (an I/O completes, a new thread is created);
4. is interrupted by the timer.

A **cooperative** (non-preemptive) scheduler only acts on 1 and 2: a thread keeps the CPU until it gives it up. Windows 3.1 and classic Mac OS worked this way, and one misbehaving program could freeze the whole machine. Today, cooperative scheduling survives *inside* programs: Python asyncio tasks yield when an await actually suspends, while event loops also move on when callbacks or tasks return; so a task stuck in a CPU loop stalls everything else in that loop.

A **preemptive** scheduler can also act on 3 and 4. A periodic **timer interrupt** returns control to the kernel, which can take the CPU away from a thread that has run long enough. Every mainstream OS (Linux, Windows, macOS) preempts user threads.

Each switch costs something: saving and restoring registers, running the scheduler, and, less visibly, cold caches and TLB for the incoming thread. There is no platform-independent switch-time constant; both direct and cache costs need measurement.

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

Average waiting time = (0 + 24 + 27) / 3 = **17 ms**.

If the short jobs had arrived first (P2, P3, P1), the waits would be 0, 3 and 6: an average of **3 ms**. Same work, nearly six times better.

This is the **convoy effect**: short jobs stuck behind a long one, like cars behind a lorry on a single-lane road. With a mix of one CPU-bound and several I/O-bound threads, the I/O-bound ones queue behind the hog while the disks sit idle, then all finish their I/O together while the CPU sits idle.

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

Waiting: P1 = 0, P2 = 8 − 1 = 7, P4 = 12 − 3 = 9, P3 = 17 − 2 = 15. Average = 31 / 4 = **7.75**.

### Shortest remaining time first (SRTF)

The preemptive version: whenever a job arrives, compare its burst with the *remaining* time of the running job, and switch if it's shorter.

1. t = 0: P1 starts (remaining 8).
2. t = 1: P2 arrives with 4 < P1's remaining 7. Preempt; P2 runs.
3. t = 2 and 3: P3 (9) and P4 (5) arrive; neither beats P2's remaining 3 or 2.
4. t = 5: P2 done. Remaining: P1 7, P3 9, P4 5. P4 runs.
5. t = 10: P4 done. P1 (7) runs, then P3.

```
|P1| P2 |  P4  |   P1   |   P3    |
0  1    5     10       17        26
```

Waiting = turnaround − burst: P1 = 17 − 8 = 9, P2 = 4 − 4 = 0, P3 = 24 − 9 = 15, P4 = 7 − 5 = 2. Average = 26 / 4 = **6.5**, better than non-preemptive SJF.

### The catch: you don't know the future

The OS can't know how long a burst will be. It can **predict** from history, typically with an exponential average:

```
next = a * last_actual + (1 - a) * guess
```

With a = 0.5, an initial guess of 10 ms and actual bursts of 6 then 4 ms, the predictions are 10, then 0.5 × 6 + 0.5 × 10 = 8, then 0.5 × 4 + 0.5 × 8 = 6.

SJF also risks **starvation**: if short jobs keep arriving, a long job may never run. The next lesson covers how real schedulers avoid that.

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

Average waiting is 17 / 3 ≈ **5.67 ms** and average response time 11 / 3 ≈ **3.67 ms**, against 17 and 17 for FCFS in the original order.

> [!note] A tie-breaking convention
> When a job's quantum expires at the same moment a new job arrives, most textbooks put the new arrival in the queue first, then the preempted job. State your convention when you work these by hand; it can change the answer.

### Choosing the quantum

- **Too large**, and RR degenerates into FCFS: interactive jobs wait behind CPU hogs.
- **Too small**, and the CPU spends its time switching. With a 0.1 ms switch cost, a 10 ms quantum wastes 0.1 / 10.1 ≈ 1%; a 1 ms quantum wastes 0.1 / 1.1 ≈ 9%, before counting cache effects.

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
- Scheduling goals conflict: throughput and utilisation versus response time and fairness.
- turnaround = completion − arrival; waiting = turnaround − burst; response = first run − arrival.
- FCFS is simple but suffers the convoy effect: short jobs wait behind long ones.
- For the stated single-CPU, equal-arrival, known-burst, zero-switch-cost model, SJF minimises average waiting time; general workloads need additional assumptions or burst estimates and can starve long jobs; SRTF is its preemptive form.
- Round robin bounds response time with a quantum; too short wastes time on switches, too long becomes FCFS.

## Further reading
- [Scheduling: Introduction — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-sched.pdf)
- [Scheduling (computing) — Wikipedia](https://en.wikipedia.org/wiki/Scheduling_(computing))
- [Round-robin scheduling — Wikipedia](https://en.wikipedia.org/wiki/Round-robin_scheduling)
- [Shortest job next — Wikipedia](https://en.wikipedia.org/wiki/Shortest_job_next)
- [Convoy effect — Wikipedia](https://en.wikipedia.org/wiki/Convoy_effect)
