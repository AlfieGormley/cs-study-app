---
id: sync-lock-free-progress-and-cas
title: Progress guarantees and CAS retries
level: advanced
minutes: 4
summary: Separate blocking, obstruction-free, lock-free and wait-free progress and trace a maximum update.
sourceLesson: sync-lock-free
---

Locks are simple and correct, but they have one structural weakness: **if the thread holding a lock stops, everyone waiting for it stops too**. The holder might be preempted, page-faulting, running a signal handler, or simply slow. Under heavy load that one stalled thread sets the pace for all the others.

Lock-free techniques avoid holding anything that others must wait for. Instead of "acquire, modify, release", threads prepare a change privately and publish it with a single atomic instruction, retrying if someone else got there first. This lesson covers how that works, why it is much harder than it looks, and the more practical read-mostly tools (read-write locks, seqlocks and RCU) that real kernels and servers rely on.

## Progress guarantees

"Lock-free" has a precise meaning. It describes what happens when threads are delayed, not whether the code contains the word `lock`.

| Guarantee | Promise |
|---|---|
| Blocking | a stalled thread can stop all |
| Obstruction-free | a thread alone finishes |
| Lock-free | some thread always progresses |
| Wait-free | every thread finishes, bounded |

- **Blocking algorithm**: any algorithm using a mutex. If the holder is descheduled, nobody else in that critical section progresses.
- **Obstruction-free**: a thread finishes in a bounded number of steps if all others pause. Contending threads may keep undoing each other's work.
- **Lock-free**: continued execution guarantees system-wide operation progress under the algorithm's primitive and scheduling assumptions. An individual operation can starve; this is not a fixed wall-clock completion deadline.
- **Wait-free**: *every* thread completes in a bounded number of its own steps, however others behave. The strongest guarantee and the hardest to build.

A spinlock built from CAS is **not** lock-free: if the holder is preempted, every spinner makes zero progress. Using atomic instructions does not by itself make an algorithm lock-free.

Maurice Herlihy showed in 1991 that primitives differ in power. Plain loads and stores, or test-and-set, cannot build wait-free versions of every data structure for arbitrary numbers of threads; compare-and-swap (and LL/SC) can. That is why CAS is the foundation of everything in this lesson.

## The CAS retry loop

The example keeps a maximum with an initial floor of zero: values below zero do not lower that floor. The basic lock-free pattern is: read the current value, compute a new one privately, and CAS it in. On comparison failure, another update changed the expected value; a weak CAS may also fail spuriously. Reload/recompute as the algorithm requires.

```c
#include <stdatomic.h>

atomic_long max_seen = 0;

void record(long v) {
    // Retry only while our value is larger.
    long cur = atomic_load(&max_seen);
    while (v > cur &&
           !atomic_compare_exchange_weak(
               &max_seen, &cur, v))
        ;  // cur now holds the new value
}
```

On failure, C11's CAS writes the value it found into `cur`, so the loop re-tests with fresh data. Assuming lock-free atomic primitives and their required forward progress, the loop has system-wide non-blocking progress. A comparison mismatch shows interference; a weak CAS can also fail spuriously, so not every failed call proves another operation succeeded.

CAS retry loops generally do not give each thread a fixed retry bound. By contrast, a fetch-add implemented as one native instruction has a bounded number of algorithmic steps, assuming that primitive completes. This is not a bound on wall-clock latency: scheduling, faults and hardware contention still matter.

## Key takeaways

- A spinlock remains blocking even when it uses compare-and-swap.
- Lock-free gives system-wide progress, while wait-free bounds each operation’s own steps under its assumptions.
- Non-spurious comparison failure indicates interference; weak CAS may also fail spuriously.

## Further reading

- [Herlihy: Wait-free synchronization](https://cs.brown.edu/~mph/Herlihy91/p124-herlihy.pdf)
- [Michael–Scott queue paper](https://www.cs.rochester.edu/u/scott/papers/1996_PODC_queues.pdf)
- [Linux RCU documentation](https://www.kernel.org/doc/html/latest/RCU/whatisRCU.html)
- [Linux sequence counters and seqlocks](https://www.kernel.org/doc/html/latest/locking/seqlock.html)
- [Userspace RCU](https://liburcu.org/)
- [Python threading](https://docs.python.org/3/library/threading.html)
