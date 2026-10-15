---
id: dl-livelock-starvation-priority-inheritance
title: Priority inversion and inheritance
level: intermediate
minutes: 2
sourceLesson: dl-livelock-starvation
summary: A medium-priority task can indirectly delay high-priority work by preempting its lock holder.
---

## Priority inversion

Module 2 introduced priority inversion and the Mars Pathfinder resets. Here is the deadlock-module view of it: it's a liveness failure where a high-priority thread is blocked, *indirectly*, by an unrelated medium-priority one.

```
time ----------------------------->
L:  lock(m) ##          ..........##unlock
H:          wakes, lock(m) blocks......
M:             runs ###############
```

1. Low-priority L takes mutex `m`.
2. High-priority H wakes up, tries to take `m` and blocks.
3. Medium-priority M becomes runnable. It outranks L, so it preempts L.
4. H now waits for L, which can't run until M finishes. Without a bound on intervening medium-priority work, this model gives no bound on H’s delay.

Pathfinder engineer Glenn Reeves described an ASI/MET task holding a VxWorks pipe/select semaphore needed by `bc_dist`. Intermediate-priority work delayed ASI/MET; the higher-priority `bc_sched` detected that `bc_dist` had not completed its work and triggered a reset. Enabling priority inheritance for the relevant semaphore class fixed this failure.

### Priority inheritance

When H blocks on a mutex held by L, L temporarily **inherits** H's priority until it releases the mutex. M can no longer preempt L in this simple three-task model. A real bound must also account for higher-priority work, nested dependencies, I/O and scheduling assumptions.

- POSIX: `pthread_mutexattr_setprotocol(&attr, PTHREAD_PRIO_INHERIT)`.
- Linux implements it with PI futexes and the kernel's `rt_mutex`, which walks chains: if L is itself blocked on a mutex held by L2, L2 is boosted too.
- It doesn't prevent deadlock, and with nested locks a high-priority thread can be blocked once per lock it needs (**chained blocking**).

## Key takeaways
- A medium-priority task can indirectly delay high-priority work by preempting its lock holder.
- Priority inheritance boosts a supported owned-lock holder and can propagate through dependency chains.
- Inheritance mitigates inversion but does not itself prevent deadlock.

## Further reading
- [Linux: priority inheritance and boost chains](https://docs.kernel.org/locking/rt-mutex-design.html)
- [Glenn Reeves: firsthand Pathfinder correction](https://catless.ncl.ac.uk/Risks/19.54.html)
