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

The three times in the table are all worked out from moments on one clock that starts at 0 when we begin watching. Each is a subtraction. These identities hold for a job that never blocks, so it needs the CPU for one stretch (one CPU burst, defined in the next section) and is either running or waiting in the queue:

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

A **cooperative** (non-preemptive) scheduler only acts on 1 and 2: a thread keeps the CPU until it gives it up. Windows 3.1 and classic Mac OS worked this way, and one misbehaving program could freeze the whole machine. Today, cooperative scheduling survives *inside* programs: Python asyncio tasks yield when an await actually suspends, while event loops also move on when callbacks or coroutines return; so a coroutine stuck in a CPU loop stalls everything else in that loop.

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
W_P1 = 0 − 0 = 0 ms
W_P2 = 8 − 1 = 7 ms
W_P4 = 12 − 3 = 9 ms
W_P3 = 17 − 2 = 15 ms
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

### Shortest remaining time first (SRTF)

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
W_P1 = (17 − 0) − 8 = 9 ms
W_P2 = (5 − 1) − 4 = 0 ms
W_P3 = (26 − 2) − 9 = 15 ms
W_P4 = (10 − 3) − 5 = 2 ms
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

### The catch: you don't know the future

The OS can't know how long a burst will be. It can **predict** from history. Threads tend to behave like they did recently, so a common textbook method is an **exponential average**: after each burst, blend the burst that just happened with the previous prediction.

```formula
τ_{n+1} = α × t_n + (1 − α) × τ_n
τ_1 = 10 ms
τ_2 = 0.5 × 6 ms + 0.5 × 10 ms = 8 ms
τ_3 = 0.5 × 4 ms + 0.5 × 8 ms = 6 ms
where
τ_{n+1}: tau, the predicted length of the next CPU burst, in milliseconds (ms)
t_n: the measured length of the burst that just finished, in ms; here t_1 = 6 ms and then t_2 = 4 ms
τ_n: the previous prediction, the one made for the burst that just finished, in ms
α: alpha, the weight given to the latest burst, between 0 and 1; 0.5 here. Near 1, the prediction follows the last burst closely; near 0, it barely changes
τ_1: the initial guess before any burst has been measured, 10 ms here
τ_2, τ_3: the second and third predictions, in ms
ms: milliseconds, thousandths of a second
In words: the next prediction is part the latest real burst and part the old prediction; with α = 0.5 it is exactly halfway between the two.
```

It is called exponential because each step multiplies every older burst's influence by (1 − α) again: with α = 0.5, the burst before last counts a quarter, the one before that an eighth, and so on. Old history fades quickly but never vanishes. The method works only as well as the past predicts the future; a thread that suddenly changes behaviour is mispredicted for a few bursts.

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

### Choosing the quantum

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
- Scheduling goals conflict: throughput and utilisation versus response time and fairness.
- Turnaround time is completion minus arrival; waiting time is turnaround minus the CPU burst; response time is first run minus arrival.
- FCFS is simple but suffers the convoy effect: short jobs wait behind long ones.
- For the stated single-CPU, equal-arrival, known-burst, zero-switch-cost model, SJF minimises average waiting time; general workloads need additional assumptions or burst estimates and can starve long jobs; SRTF is its preemptive form.
- Round robin bounds response time with a quantum; too short wastes time on switches, too long becomes FCFS.

## Further reading
- [Scheduling: Introduction — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-sched.pdf)
- [Scheduling (computing) — Wikipedia](https://en.wikipedia.org/wiki/Scheduling_(computing))
- [Round-robin scheduling — Wikipedia](https://en.wikipedia.org/wiki/Round-robin_scheduling)
- [Shortest job next — Wikipedia](https://en.wikipedia.org/wiki/Shortest_job_next)
- [Convoy effect — Wikipedia](https://en.wikipedia.org/wiki/Convoy_effect)
