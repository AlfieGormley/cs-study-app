---
id: dl-livelock-starvation-fairness
title: Starvation, ticket locks and barging
level: intermediate
minutes: 3
sourceLesson: dl-livelock-starvation
summary: Starvation affects an individual while other work keeps progressing.
---

## Starvation

**Starvation** is when the system as a whole progresses, but one thread waits indefinitely because others keep winning. Nothing is stuck in a cycle; the victim just never gets its turn.

Common sources:

- **Unfair locks.** When a lock is released, whoever grabs it first wins. A thread that has just released it is still running and cache-hot, so it often re-acquires it before a sleeping waiter even wakes up. This is called **barging**.
- **Read-write locks.** If readers can join while other readers hold the lock, a steady stream of readers can keep a writer out forever. glibc's `pthread_rwlock` prefers readers by default.
- **Priority scheduling.** Low-priority work starves under constant high-priority load (module 2). The fix there is **aging**.
- **Victim selection.** A database that always aborts the cheapest transaction can abort the same one repeatedly (the detection and recovery lessons).

### Fair locks and their cost

A **fair lock** uses first-in, first-out (FIFO) hand-off to the longest waiter. Ticket locks make this explicit:

```python
import itertools
import threading

class TicketLock:
    def __init__(self):
        self._next = itertools.count()
        self._serving = 0
        self._cv = threading.Condition()

    def acquire(self):
        with self._cv:
            me = next(self._next)
            # Condition waits must recheck
            # the turn.
            while self._serving != me:
                self._cv.wait()

    def release(self):
        with self._cv:
            self._serving += 1
            # Wake all; only the next ticket
            # enters.
            self._cv.notify_all()
```

Each thread takes a ticket; the lock serves tickets in order, so nobody can be overtaken. This teaching lock assumes each successful acquirer eventually releases exactly once, no cancelled ticket, and fair scheduling. It has no ownership checks or timeout/cancellation support. Kernel queued spinlocks use more complex architecture-dependent fast paths and queueing; they should not be described as this exact FIFO algorithm.

Strict hand-off can reduce throughput: the lock may sit unused until the designated waiter runs, even though another thread could acquire it. The CPU can run unrelated work. Repeated hand-off delays can create a **lock convoy**, but costs depend on scheduling and workload.

> [!note] Content gap
> Fixed nanosecond/microsecond hand-off costs are omitted because no reproducible benchmark record is provided.

So real locks compromise:

- **Java** `ReentrantLock` is unfair by default; `new ReentrantLock(true)` favors the longest-waiting thread under contention; untimed `tryLock()` can still barge, and lock fairness does not guarantee scheduler fairness.
- **Go** `sync.Mutex` normally allows barging, but a waiter that wakes after waiting more than 1 ms can switch a still-locked mutex to **starvation mode** and hands ownership directly to the waiter at the front of the queue.
- **Linux** kernel mutexes let a waiter that has been passed over set a **hand-off** flag, so the next unlock gives the lock to it rather than to a barging thread.

> [!tip] A useful pattern
> Go's policy illustrates a throughput/fairness compromise. Its 1 ms threshold is an implementation detail, not a maximum lock-wait or tail-latency guarantee.

## Key takeaways
- Starvation affects an individual while other work keeps progressing.
- FIFO admission bounds overtaking under release and scheduling assumptions.
- Barging can improve throughput; adaptive hand-off attempts to protect long waiters.

## Further reading
- [Go source: mutex fairness and starvation mode](https://go.dev/src/internal/sync/mutex.go)
- [Python: primitive and re-entrant locks](https://docs.python.org/3/library/threading.html)
