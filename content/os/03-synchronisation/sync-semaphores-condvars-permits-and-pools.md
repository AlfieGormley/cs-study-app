---
id: sync-semaphores-condvars-permits-and-pools
title: Count semaphore permits
level: intermediate
minutes: 3
summary: Use semaphore initial values for exclusion, resource pools and non-blocking acquisition.
sourceLesson: sync-semaphores-condvars
---

A lock answers one question: "may I enter?" Threads often need to wait for something else entirely: "is there an item in the queue?", "has the worker finished?", "is a connection free?". Spinning on a flag wastes CPU and, as the earlier race-condition units showed, is a data race unless done with atomics.

This lesson covers the two classic tools for **waiting on a condition**: semaphores, and condition variables used with a mutex.

## Semaphores

A **semaphore**, introduced by Edsger Dijkstra in the 1960s, is an integer counter with two atomic operations:

- **wait** (also called P, `down`, `acquire`, `sem_wait`): decrement the counter. If the result would be negative, block until it can proceed.
- **signal** (also called V, `up`, `release`, `sem_post`): increment the counter, waking one blocked waiter if there is one.

P and V are historical names for the wait and signal operations.

The counter represents a number of available **permits**. Each completed wait takes one permit and each signal gives one back, so at a quiescent point when none of these operations is in flight:

```formula
S = S_0 + n_signal − n_wait
S ≥ 0
where
S: the semaphore's current counter value: the number of permits available right now
S_0: the initial value, chosen when the semaphore is created
n_signal: the number of successful signal/post operations completed so far
n_wait: the number of successful wait operations completed so far, excluding failed or still-blocked waits
≥: greater than or equal to
In words: the count is the starting permits, plus every signal, minus every completed wait, and it never goes below zero; a wait that would push it below zero blocks instead.
```

For example, start with three permits, complete three waits and one post, and leave no operation in flight: one permit remains. With no competing operation or further post, the next successful wait consumes it and a following blocking wait cannot proceed yet.

What you use a semaphore for depends on the initial value.

| Initial value | Use |
|---|---|
| 1 | mutual exclusion, with balanced waits/posts |
| pool size | a pool of identical resources |
| 0 | "wait until X happens" |

### As a lock

Initialised to 1, the first `wait` takes it to 0 and enters; the next `wait` blocks until a `signal`.

```c
#include <semaphore.h>

sem_t s;
sem_init(&s, 0, 1); // 0: shared by threads
                    // only, not processes

sem_wait(&s);
/* critical section */
sem_post(&s);
```

### As a resource pool

Initialised to the size of a pool, say 10, up to 10 threads proceed at once and the 11th waits. A web server might allow at most 10 concurrent database queries:

```python
import threading

db_slots = threading.BoundedSemaphore(10)

def handle(req):
    with db_slots:      # wait / signal
        # Return this permit on every exit.
        return query(req)
```

`BoundedSemaphore` raises `ValueError` if a release would raise its current count above the initial value. This detects over-release, but does not track which thread acquired each permit.

## Key takeaways

- A completed successful wait consumes a permit; a post supplies one.
- A pool semaphore limits concurrency only when acquisitions and releases are balanced.
- BoundedSemaphore detects a release that would exceed its initial count.

## Further reading

- [OSTEP: Condition variables](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-cv.pdf)
- [OSTEP: Semaphores](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-sema.pdf)
- [POSIX condition wait](https://pubs.opengroup.org/onlinepubs/9799919799/functions/pthread_cond_wait.html)
- [Python threading](https://docs.python.org/3/library/threading.html)
- [Java Object monitor methods](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Object.html)
