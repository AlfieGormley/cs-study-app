---
id: dl-livelock-starvation
title: Livelock, starvation and priority inversion
level: intermediate
minutes: 13
summary: The liveness failures that aren't deadlock, from polite threads that never stop retrying to unfair locks and high-priority work stuck behind low-priority work, and the fixes for each.
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

## Livelock

Two people meet in a corridor. Both step left to let the other pass, then both step right, then both step left. Each is responding sensibly to the other, and neither gets anywhere. That's **livelock**: threads keep changing state in response to each other without making progress.

Lesson 2's try-lock pattern is the classic way to create it:

```python
def polite(first, second):
    while True:
        first.acquire()
        if second.acquire(blocking=False):
            return          # got both
        first.release()
        # no back-off: retry at once
```

Run `polite(a, b)` and `polite(b, a)` on two cores in perfect lockstep:

```
T1: take a     T2: take b
T1: try b, no  T2: try a, no
T1: drop a     T2: drop b
T1: take a     T2: take b
...forever
```

In this particular repeating schedule neither thread blocks indefinitely, so a blocked-wait cycle detector misses the failure. CPU use can be high. Other schedules may briefly block at `first.acquire()`. The caller must release both locks after a successful return.

Scheduling variation may break this pattern, but it supplies no progress guarantee; repeated collisions can waste CPU and increase latency.

### The fix: break the symmetry

For this symmetric retry pattern, useful ways to improve progress include:

- **Randomised back-off.** Sleep a random time before retrying. Ethernet's original CSMA/CD did exactly this: after the nth collision a station waits a random number of slot times between 0 and 2^min(n, 10) − 1, and gives up after 16 attempts.
- **Ordering.** If both threads take `a` before `b`, the problem disappears entirely (lesson 2).
- **Priority or tie-breaking.** Let the older or lower-id contender win.

Raft uses the same trick for leader elections. If two followers time out together, they split the vote and both have to retry. Raft draws each election timeout at random (150–300 ms in the paper), so one candidate almost always gets in first.

### Livelock at system scale

The same pattern appears wherever things retry:

- **Retry storms.** A service slows down; every client times out and retries at once, doubling the load; it slows further. The fix is exponential back-off with **jitter**, for example `sleep = random(0, min(cap, base * 2**attempt))`, which AWS calls "full jitter".
- **Receive livelock.** Mogul and Ramakrishnan (1996) showed that an interrupt-driven kernel under a packet flood can spend all its time taking receive interrupts and none delivering packets to applications. Throughput collapses to near zero while the CPU is fully busy. Linux's NAPI uses interrupt-triggered, budgeted polling to mitigate receive livelock (module 7); it does not guarantee application progress under every overload or configuration.
- **Optimistic concurrency.** Two transactions that keep conflicting, aborting and restarting together can livelock. Back-off can reduce collisions; timestamp protocols need fair execution and finite transactions for eventual completion.

## Starvation

**Starvation** is when the system as a whole progresses, but one thread waits indefinitely because others keep winning. Nothing is stuck in a cycle; the victim just never gets its turn.

Common sources:

- **Unfair locks.** When a lock is released, whoever grabs it first wins. A thread that has just released it is still running and cache-hot, so it often re-acquires it before a sleeping waiter even wakes up. This is called **barging**.
- **Readers-writer locks.** If readers can join while other readers hold the lock, a steady stream of readers can keep a writer out forever. glibc's `pthread_rwlock` prefers readers by default.
- **Priority scheduling.** Low-priority work starves under constant high-priority load (module 2). The fix there is **aging**.
- **Victim selection.** A database that always aborts the cheapest transaction can abort the same one repeatedly (lesson 4).

### Fair locks and their cost

A **fair** (FIFO) lock hands ownership to the longest waiter. Ticket locks make this explicit:

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
            while self._serving != me:
                self._cv.wait()

    def release(self):
        with self._cv:
            self._serving += 1
            self._cv.notify_all()
```

Each thread takes a ticket; the lock serves tickets in order, so nobody can be overtaken. This teaching lock assumes each successful acquirer eventually releases exactly once, no cancelled ticket, and fair scheduling. It has no ownership checks or timeout/cancellation support. Kernel queued spinlocks use more complex architecture-dependent fast paths and queueing; they should not be described as this exact FIFO algorithm.

Strict hand-off can reduce throughput: the lock may sit unused until the designated waiter runs, even though another thread could acquire it. The CPU can run unrelated work. Repeated hand-off delays can create a **lock convoy**, but costs depend on scheduling and workload.

> [!note] Content gap
> Fixed nanosecond/microsecond hand-off costs are omitted because no reproducible benchmark record is provided.

So real locks compromise:

- **Java** `ReentrantLock` is unfair by default; `new ReentrantLock(true)` favors the longest-waiting thread under contention; untimed `tryLock()` can still barge, and lock fairness does not guarantee scheduler fairness.
- **Go** `sync.Mutex` normally allows barging, but if a waiter has been waiting for more than 1 ms, the mutex switches to **starvation mode** and hands ownership directly to the waiter at the front of the queue.
- **Linux** kernel mutexes let a waiter that has been passed over set a **hand-off** flag, so the next unlock gives the lock to it rather than to a barging thread.

> [!tip] A useful pattern
> Go's policy illustrates a throughput/fairness compromise. Its 1 ms threshold is an implementation detail, not a maximum lock-wait or tail-latency guarantee.

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
4. H now waits for L, which can't run until M finishes. H's delay is unbounded.

Pathfinder engineer Glenn Reeves described an ASI/MET task holding a VxWorks pipe/select semaphore needed by `bc_dist`. Intermediate-priority work delayed ASI/MET; the higher-priority `bc_sched` detected that `bc_dist` had not completed its work and triggered a reset. Enabling priority inheritance for the relevant semaphore class fixed this failure.

### Priority inheritance

When H blocks on a mutex held by L, L temporarily **inherits** H's priority until it releases the mutex. M can no longer preempt L in this simple three-task model. A real bound must also account for higher-priority work, nested dependencies, I/O and scheduling assumptions.

- POSIX: `pthread_mutexattr_setprotocol(&attr, PTHREAD_PRIO_INHERIT)`.
- Linux implements it with PI futexes and the kernel's `rt_mutex`, which walks chains: if L is itself blocked on a mutex held by L2, L2 is boosted too.
- It doesn't prevent deadlock, and with nested locks a high-priority thread can be blocked once per lock it needs (**chained blocking**).

### Priority ceiling

Each mutex is given a **ceiling**: the priority of the highest-priority thread that ever uses it. With the common *immediate* variant (`PTHREAD_PRIO_PROTECT` in POSIX), a thread that takes the mutex runs at the ceiling straight away, so lower-priority unrelated tasks cannot preempt it in the usual single-CPU fixed-priority model. Equal-priority scheduling and multiprocessor behavior need separate analysis.

The original priority ceiling protocol (Sha, Rajkumar and Lehoczky, 1990) goes further: a thread may lock a mutex only if its priority is higher than the ceilings of all mutexes currently locked by other threads. Under the protocol's single-processor fixed-priority model, correctly assigned ceilings, bounded critical sections and resource-use assumptions, that rule **prevents deadlock** and limits a job's lower-priority blocking to at most one critical section. The cost is that every ceiling must be worked out in advance, which suits static real-time systems more than general-purpose servers.

### When inheritance can't help

Inheritance needs to know *who* to boost, so conventional mutex PI needs an identifiable **owner**. Other systems can propagate priority through explicitly tracked server or resource dependencies; ownership need not literally be a POSIX mutex. A semaphore, condition variable, queue or pipe has no owner. If H waits on a semaphore that L will eventually post, the kernel has no idea that L is the one to boost.

Choose a dependency protocol that exposes ownership where blocking is unavoidable; hard real-time audio code should generally avoid blocking on lower-priority work altogether. Apple's platforms, for example, donate priority to the owner of a `pthread_mutex` or `os_unfair_lock` but can't do so for a `DispatchSemaphore`.

## Key takeaways
- Safety means nothing bad happens; liveness means something good eventually happens. Locks trade liveness for safety.
- Livelock is busy non-progress: threads react to each other forever. Break the symmetry with randomised back-off, ordering or tie-breaking.
- Retry storms and receive livelock are the same failure at system scale; exponential back-off with jitter and NAPI-style polling are the fixes.
- Starvation is one thread losing forever while others progress. Unfair locks, reader-preferring rwlocks and naive victim selection all cause it.
- Fair ordering limits overtaking under scheduling/release assumptions, not wall-clock wait time. Hand-off can cost throughput; Go and Linux use adaptive policies.
- Priority inheritance mitigates inversion on supported owned locks. Ceiling-protocol bounds need a suitable scheduling model and static analysis. Ownerless waits do not identify a producer to boost, though a condition wait's associated PI mutex may help during mutex reacquisition.

## Further reading
- [Starvation (computer science) — Wikipedia](https://en.wikipedia.org/wiki/Starvation_(computer_science))
- [Exponential Backoff And Jitter — AWS Architecture Blog](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)
- [Go source: mutex fairness and starvation mode](https://go.dev/src/internal/sync/mutex.go)
- [Priority inversion — Wikipedia](https://en.wikipedia.org/wiki/Priority_inversion)
- [Priority ceiling protocol — Wikipedia](https://en.wikipedia.org/wiki/Priority_ceiling_protocol)
- [What really happened on Mars Pathfinder — Mike Jones (Cornell mirror)](https://www.cs.cornell.edu/courses/cs614/1999sp/papers/pathfinder.html)
- [Non-blocking algorithm — Wikipedia](https://en.wikipedia.org/wiki/Non-blocking_algorithm)
