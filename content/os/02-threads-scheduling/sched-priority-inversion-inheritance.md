---
id: sched-priority-inversion-inheritance
title: Priority inversion and inherited lock priority
level: intermediate
minutes: 4
sourceLesson: sched-priority-mlfq
summary: A medium-priority task can delay a high-priority waiter by preempting its low-priority lock holder.
---

## Priority inversion

Priorities interact badly with locks. Take three threads on one CPU, sharing a mutex `m`:

- **H**: high priority, needs `m` briefly;
- **M**: medium priority, CPU-heavy, never touches `m`;
- **L**: low priority, takes `m` now and then.

```
L: lock(m) ...........   ...unlock
H:      wakes, lock(m) -> BLOCKED
M:           wakes, runs, runs, runs
           <---- H waits for M ---->
```

1. L takes `m`.
2. H wakes, preempts L and tries to lock `m`. It blocks.
3. M wakes. It outranks L, so it preempts L.
4. L can't run, so it can't release `m`, so H can't run.

H is now waiting for M, a lower-priority thread that has nothing to do with `m`. The priorities have been **inverted**. Worse, the delay isn't bounded by L's short critical section; it lasts as long as M (and any other medium-priority work) keeps running. This is **unbounded priority inversion**.
## Mars Pathfinder, 1997

Glenn Reeves, who led Pathfinder's software team, describes a priority inversion involving a semaphore inside VxWorks `select`/pipe handling. The low-priority ASI/MET task held the resource; intermediate work delayed it while the higher-priority `bc_dist` task waited. A deadline check by `bc_sched` triggered a reset.

Engineers reproduced the failure with tracing, enabled priority inheritance through a configuration change, tested the wider effects and deployed it using their validated spacecraft patch mechanism. Reeves explicitly says they **did not use the VxWorks shell** for the update. He also says the pre-landing occurrence was investigated and remained unresolved, rather than being dismissed as a hardware glitch.

This firsthand correction matters: retain the inversion lesson without repeating the inaccurate interpreter-fix and ignored-warning story.
## Priority inheritance

The fix is **priority inheritance**: while a thread holds a lock that a higher-priority thread is waiting for, it temporarily runs at the waiter's priority.

1. H blocks on `m`, held by L. L is boosted to H's priority.
2. M wakes but can't preempt L, which now outranks it.
3. L finishes its critical section and releases `m`, dropping back to low priority.
4. H takes `m` and runs.

In this isolated three-thread example, H waits for L's remaining critical section plus scheduling overhead. General bounds must include nesting, higher-priority interference and any blocking by the holder. Inheritance must be **transitive**: if L is itself blocked on a lock held by another thread, that thread is boosted too.

An alternative is an **immediate priority ceiling** protocol: each mutex gets a ceiling equal to the highest priority of any thread that may lock it, and whoever holds it runs at the ceiling straight away. It needs the ceiling worked out in advance, but avoids repeated priority changes.

POSIX exposes both as mutex attributes. This configuration fragment assumes m is a declared mutex; production code must check the return values and destroy the attribute object when finished:

```c
pthread_mutexattr_t a;
pthread_mutexattr_init(&a);
pthread_mutexattr_setprotocol(
    &a, PTHREAD_PRIO_INHERIT);
/* or PTHREAD_PRIO_PROTECT for ceiling */
pthread_mutex_init(&m, &a);
```

On Linux, `PTHREAD_PRIO_INHERIT` mutexes are built on PI futexes and the kernel's `rt_mutex`, which handles chains of boosts. The PREEMPT_RT real-time kernel goes further and converts most kernel spinlocks into priority-inheriting sleeping locks for the same reason.

Priority inversion matters most for real-time threads with strict priorities. Ordinary Linux threads under the fair scheduler suffer milder versions: a low-weight thread holding a lock still runs, just slowly. The next module covers locks in depth.

## Key takeaways
- A medium-priority task can delay a high-priority waiter by preempting its low-priority lock holder.
- Priority inheritance boosts holders along blocking chains; priority ceilings use precomputed mutex ceilings.
- Pathfinder’s firsthand account describes enabling inheritance through a tested patch, without using a VxWorks shell.

## Further reading
- [Scheduling: The Multi-Level Feedback Queue — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-sched-mlfq.pdf)
- [Glenn Reeves: what happened on Pathfinder — firsthand correction in RISKS](https://catless.ncl.ac.uk/Risks/19.54.html)
- [Priority inversion — Wikipedia](https://en.wikipedia.org/wiki/Priority_inversion)
- [Priority inheritance — Wikipedia](https://en.wikipedia.org/wiki/Priority_inheritance)
- [RT-mutex subsystem with PI support — Linux kernel docs](https://docs.kernel.org/locking/rt-mutex.html)
- [Multilevel feedback queue — Wikipedia](https://en.wikipedia.org/wiki/Multilevel_feedback_queue)
