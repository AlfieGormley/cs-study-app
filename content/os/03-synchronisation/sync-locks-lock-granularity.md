---
id: sync-locks-lock-granularity
title: Choose lock granularity from evidence
level: intermediate
minutes: 3
summary: Trade simpler invariants against contention, ordering risk and false sharing.
sourceLesson: sync-locks
---

One global lock is easy to understand, but unrelated operations can queue behind it. Splitting it helps only when the application can maintain its invariants under the new protocol.

The main lever is **granularity**, meaning how much data each lock protects.

| | Coarse-grained | Fine-grained |
|---|---|---|
| Example | one lock per table | one lock per bucket |
| Simplicity | easy to get right | many locks to order |
| Parallelism | low | high |
| Overhead | one lock op | more lock ops |

Real systems have moved from coarse to fine over time:

- **Linux's Big Kernel Lock** let only one CPU run most kernel code at a time when SMP support was first added. It was gradually replaced by fine-grained locks and finally removed in 2.6.39 (2011).
- **CPython's GIL** is a coarse interpreter lock in conventional builds, limiting parallel execution of Python bytecode within an interpreter. Extensions can release it. PEP 703 specifies a free-threaded build using mechanisms including per-object locking; performance depends on the build and workload.
- **Java's `ConcurrentHashMap`** originally used **lock striping** (16 segments by default, each with its own lock). The JDK 8 implementation uses CAS for an empty bin and bin-level locking for several occupied-bin updates, with additional tree-bin and resizing protocols. These are version-specific internals, rather than a description of every operation.

Fine-grained locking has costs. More locks mean more chances to take them in inconsistent orders, which leads to deadlock (the subject of the next module), and operations spanning several items (resizing the whole table) become harder.

Practical rules:

1. **Keep critical sections short.** Avoid blocking I/O, logging or network calls under a hot lock where the required ordering and lifetime rules permit moving them out.
2. **Measure before splitting.** Profilers and `perf lock` or mutex contention counters tell you which lock is actually hot.
3. **Avoid sharing instead of locking it.** Per-thread counters combined at the end can reduce contention when delayed aggregation preserves the required semantics.
4. **Watch for false sharing.** Independent writes sharing a cache line can cause coherence traffic even under separate locks. Cache-line size is architecture-dependent; 64 bytes is one common example.

> [!warning] Priority inversion
> A low-priority thread holds a lock, a high-priority thread waits for it, and a medium-priority thread preempts the low one. The high-priority thread is now effectively blocked by the medium one. This famously reset the Mars Pathfinder lander in 1997. The fix is **priority inheritance**: the holder temporarily runs at the waiter's priority (`PTHREAD_PRIO_INHERIT`).

> [!note] Content gap
> No reproducible lock or syscall benchmark accompanies this lesson, so exact nanosecond costs and universal speed-up claims are omitted. The futex code is a teaching sketch, not a portable production mutex.

## Key takeaways

- Fine-grained locks can expose parallelism but complicate multi-object operations and lock ordering.
- Measure hold times and contention before changing the protocol.
- Per-thread aggregation, false-sharing fixes and shorter sections must preserve the required semantics.

## Further reading

- [OSTEP: Locks](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-locks.pdf)
- [Futexes Are Tricky — Ulrich Drepper](https://www.akkadia.org/drepper/futex.pdf)
- [Linux futex manual](https://man7.org/linux/man-pages/man2/futex.2.html)
- [Linux lock types and PREEMPT_RT](https://www.kernel.org/doc/html/latest/locking/locktypes.html)
- [PEP 703](https://peps.python.org/pep-0703/)
