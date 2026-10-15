---
id: dl-prevention-remove-waits
title: Removing exclusive resources and nested waits
level: intermediate
minutes: 3
sourceLesson: dl-prevention
summary: Immutable data, ownership and copies can remove some shared locks.
---

Deadlock needs all four Coffman conditions at once: mutual exclusion, hold and wait, no preemption and circular wait. **Prevention** means designing the system so that at least one of them can never hold. If you succeed, there is nothing to detect and nothing to recover from.

Prevention is a useful design approach for application and kernel code. Its rules can cost flexibility or concurrency; following a fixed acquisition order often requires no extra runtime detector.

Let's take the conditions one at a time, then look at the techniques that matter most in practice.

## Breaking mutual exclusion

If a resource can be shared, nobody waits for it. Options:

- **Immutable data.** Data that never changes needs no lock. Build a new version with a correct publication and lifetime protocol rather than editing published data in place.
- **Lock-free structures.** Atomic operations (compare-and-swap) replace a lock with a retry loop, as covered in the previous module.
- **Spooling.** Only a printer daemon touches the printer; everyone else drops jobs into a queue. Clients no longer directly acquire the physical printer; the queue/daemon still needs its own synchronization and back-pressure protocol.
- **Per-thread copies.** Give each thread its own counter or buffer and combine them later.

You can't remove mutual exclusion everywhere: some state really must be updated by one party at a time. But every lock you delete is one that can't deadlock.

## Breaking hold and wait

A thread must never hold one resource while waiting for another. Two ways to arrange that:

1. **Acquire everything up front.** Request all the locks you will need in one step, getting all or none. While waiting, you hold nothing.
2. **Release before requesting.** Before waiting for a new lock, drop the ones you hold. Copy out what you need, release, then take the next lock.

Both have costs. Up-front acquisition means knowing your full lock set in advance (often impossible when the second lock depends on data read under the first), and holding locks longer than needed. Release-before-request means the world may change between locks, so you must re-validate.

> [!tip] The everyday version: don't block while holding a lock
> Most practical "hold and wait" fixes are simple: don't call `join()`, wait on a future, do network I/O or call user-supplied callbacks while holding a lock. Release first, then wait. Calls made with no locks held are sometimes called **open calls**.

## Key takeaways
- Immutable data, ownership and copies can remove some shared locks.
- All-or-none acquisition removes hold and wait; discovering the full set can be difficult.
- Open calls and releasing before waiting require preserving invariants and revalidation.

## Further reading
- [OSTEP: Common Concurrency Problems](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-bugs.pdf)
- [Python: primitive and re-entrant locks](https://docs.python.org/3/library/threading.html)
