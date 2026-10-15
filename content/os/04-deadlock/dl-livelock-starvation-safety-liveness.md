---
id: dl-livelock-starvation-safety-liveness
title: Safety, liveness and progress guarantees
level: intermediate
minutes: 2
sourceLesson: dl-livelock-starvation
summary: Safety forbids bad outcomes; liveness requires eventual useful progress.
---

A system can be deadlock-free and still fail to make progress. Threads might be busy but achieving nothing, or most threads might progress while one never does. These are **liveness** failures, and they are often harder to spot than deadlock because nothing looks frozen.

## Safety and liveness

Leslie Lamport's split is a useful frame:

- A **safety** property says *nothing bad ever happens*: two threads are never in the critical section together; an account never goes negative.
- A **liveness** property says *something good eventually happens*: every request is eventually served; a thread waiting for a lock eventually gets it.

Locks exist to give you safety. Deadlock, livelock and starvation are what they cost you in liveness. A program that never runs anything is perfectly safe, and perfectly useless.

| Failure | Threads | Anyone progressing? |
|---|---|---|
| Deadlock | Unable to proceed; may sleep or spin | No (among affected participants) |
| Livelock | Repeated state changes/retries | No useful progress by affected participants |
| Starvation | Mixed | Yes, but not the victim |
| Priority inversion | Mixed | Yes, wrong order |

## Progress guarantees

Concurrent algorithms use the following progress properties. The first three form an implication hierarchy; lock guarantees additionally assume holders release and threads are scheduled:

| Guarantee | Promise |
|---|---|
| Wait-free | Each operation completes within a bounded number of its own steps |
| Lock-free | Continued collective steps guarantee system-wide operation progress |
| Obstruction-free | An operation completes after sufficiently many steps in isolation |
| Starvation-free | Every waiter eventually gets the lock |
| Deadlock-free | Some waiter eventually gets the lock |

The first three do not require a paused participant to release a lock. Obstruction freedom is weaker than lock freedom: concurrent active operations may repeatedly interfere without progress. The lock guarantees assume finite critical sections and appropriate scheduling; nested dependencies can still deadlock even fair locks.

A correctly constructed atomic-counter CAS loop using lock-free primitives and bounded local work is lock-free, but not necessarily wait-free. A failed strong CAS indicates an intervening modification; a particular operation can keep losing. Arbitrary CAS loops and emulated atomics do not automatically have this guarantee.

## Key takeaways
- Safety forbids bad outcomes; liveness requires eventual useful progress.
- Wait-free, lock-free and obstruction-free describe different concurrent progress guarantees.
- A correct strong-CAS counter can be lock-free while a particular operation repeatedly loses.

## Further reading
- [OSTEP: Common Concurrency Problems](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-bugs.pdf)
