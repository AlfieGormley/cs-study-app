---
id: sched-cpu-bursts-preemption
title: CPU bursts, blocking and preemption
level: basic
minutes: 2
sourceLesson: sched-cpu-basics
summary: CPU-bound tasks compute for long bursts; I/O-bound tasks frequently block.
---

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

## Key takeaways
- CPU-bound tasks compute for long bursts; I/O-bound tasks frequently block.
- Cooperative execution depends on returning or suspending; a CPU loop can stall an event loop.
- Preemption lets the kernel regain control, at a workload-dependent direct and cache cost.

## Further reading
- [Scheduling: Introduction — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-sched.pdf)
- [Scheduling (computing) — Wikipedia](https://en.wikipedia.org/wiki/Scheduling_(computing))
- [Round-robin scheduling — Wikipedia](https://en.wikipedia.org/wiki/Round-robin_scheduling)
- [Shortest job next — Wikipedia](https://en.wikipedia.org/wiki/Shortest_job_next)
- [Convoy effect — Wikipedia](https://en.wikipedia.org/wiki/Convoy_effect)
