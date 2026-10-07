---
id: sync-semaphores-condvars
title: Semaphores, condition variables and monitors
level: intermediate
minutes: 13
summary: Counting and binary semaphores, how condition variables let threads sleep until a condition holds, why you always re-check the condition in a while loop, and how monitors package it all up.
---

A lock answers one question: "may I enter?" Threads often need to wait for something else entirely: "is there an item in the queue?", "has the worker finished?", "is a connection free?". Spinning on a flag wastes CPU and, as you saw in lesson 1, is a data race unless done with atomics.

This lesson covers the two classic tools for **waiting on a condition**: semaphores, and condition variables used with a mutex.

## Semaphores

A **semaphore**, introduced by Edsger Dijkstra in the 1960s, is an integer counter with two atomic operations:

- **wait** (also called P, `down`, `acquire`, `sem_wait`): decrement the counter. If the result would be negative, block until it can go ahead.
- **signal** (also called V, `up`, `release`, `sem_post`): increment the counter, waking one blocked waiter if there is one.

P and V are historical names for the wait and signal operations.

The counter represents a number of available **permits**. What you use it for depends on the initial value.

| Initial value | Use |
|---|---|
| 1 | mutual exclusion, with balanced waits/posts |
| N | N identical resources |
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

Initialised to N, up to N threads proceed at once and the (N+1)th waits. A web server might allow at most 10 concurrent database queries:

```python
import threading

db_slots = threading.BoundedSemaphore(10)

def handle(req):
    with db_slots:      # wait / signal
        return query(req)
```

`BoundedSemaphore` raises `ValueError` if released more times than acquired, which catches a common bug (an extra release silently raising the limit).

### As an ordering tool

Initialised to 0, a `wait` blocks until some other thread `signal`s. This makes "B must happen after A" trivial:

```c
sem_t done;  // sem_init(&done, 0, 0)
             // before creating the child

void *child(void *arg) {
    do_work();
    sem_post(&done);   // 0 -> 1
    return NULL;
}

// parent
pthread_create(&t, NULL, child, NULL);
sem_wait(&done);       // blocks until post
```

Assuming initialization and calls succeed, it works whichever thread runs first. POSIX sem_wait can fail with EINTR; real code must retry that case and handle other errors rather than enter a protected section without a permit. The snippets omit this error handling. If the child posts before the parent waits, the counter is 1 and the parent's wait returns immediately. The semaphore *remembers* the signal. That memory is the key difference from a condition variable.

### Semaphore versus mutex

A binary semaphore looks like a mutex, but:

- A semaphore has **no owner**. Any thread can `post`, which is what makes the ordering pattern work, but also means nobody catches a stray release.
- A mutex has an owner, which enables error checking, re-entrancy and **priority inheritance**. A semaphore cannot support priority inheritance, because there is no single holder to boost.

Use a mutex for mutual exclusion and a semaphore for counting or signalling.

## Condition variables

A **condition variable** (CV) is a queue of threads waiting for some condition on shared state to become true. It has no counter and no memory. It is always used together with a mutex that protects the shared state.

The operations (POSIX names):

- `pthread_cond_wait(&cv, &m)`: the caller must hold `m`. It **atomically** releases `m` and puts the thread to sleep. When woken, it **re-acquires `m`** before returning.
- `pthread_cond_signal(&cv)`: wake at least one waiting thread, if any.
- `pthread_cond_broadcast(&cv)`: wake all waiting threads.

If nobody is waiting, `signal` does nothing. It is not remembered.

The canonical pattern, waiting for a child thread to finish:

```c
int done = 0;
pthread_mutex_t m =
    PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t c =
    PTHREAD_COND_INITIALIZER;

void thr_exit(void) {
    pthread_mutex_lock(&m);
    done = 1;
    pthread_cond_signal(&c);
    pthread_mutex_unlock(&m);
}

void thr_join(void) {
    pthread_mutex_lock(&m);
    while (done == 0)
        pthread_cond_wait(&c, &m);
    pthread_mutex_unlock(&m);
}
```

Three parts are essential, and each one fixes a real bug.

### 1. The state variable

Without `done`, if the child signals before the parent waits, the signal is lost and the parent sleeps forever. The CV is just a waiting room; the *truth* lives in shared state (`done`, a queue length, a counter).

### 2. The mutex

Suppose the parent checks `done == 0` without the lock. Between that check and the call to `wait`, the child can set `done = 1` and signal. The parent then sleeps, having missed the only wakeup. This is a **lost wakeup**. Holding the mutex across the check, and having `wait` release it atomically as it sleeps, closes that window. (It is the same reason `FUTEX_WAIT` checks the value inside the kernel.)

### 3. The while loop

Always re-check the condition after waking:

```c
while (!condition)        // not "if"
    pthread_cond_wait(&cv, &m);
```

There are two reasons.

**Mesa semantics.** When thread A signals, the woken thread B does not run immediately. It merely becomes runnable and must re-acquire the mutex. In the meantime another thread C can grab the mutex and change the state. By the time B runs, the condition may be false again. A signal is only a **hint** that the state has changed.

**Spurious wakeups.** POSIX explicitly allows `pthread_cond_wait` to return even though nobody signalled. Allowing this makes CVs easier to implement efficiently, particularly on multiprocessors and when signals interrupt the wait.

> [!example] The `if` bug, traced
> One item slot, two consumers C1 and C2, one producer P. C1 waits (queue empty). P adds an item and signals; C1 becomes runnable but has not run yet. C2 arrives, takes the mutex, sees an item and consumes it. Now C1 runs, returns from `wait`, and (with `if`) assumes there is an item. It pops from an empty queue. With `while`, C1 re-checks, sees it is empty and waits again.

The alternative, **Hoare semantics**, hands the mutex directly to the woken thread so the condition is guaranteed to hold. This gives a stronger handoff contract. POSIX, Java and Python instead require callers to tolerate delayed reacquisition and recheck their predicates; the performance trade-off depends on implementation.

### signal or broadcast?

- POSIX `signal` unblocks at least one waiter, if any; callers must tolerate extra or spurious wakeups. Use it when any waiter can make progress and only one should.
- `broadcast` wakes all of them. Use it when waiters wait for *different* conditions on the same CV, or when a change could let several proceed (for example, freeing a large block that several allocation requests are waiting for).

With correctly protected predicates and a sound protocol, broadcast preserves the safety of the wait loop but can cause a **thundering herd**: 100 threads wake, contend for the mutex, 99 find nothing to do and sleep again. A common, cleaner design is one CV per condition (`not_empty`, `not_full`), so `signal` always wakes a thread that cares.

## Monitors

A **monitor** packages the pattern into a language construct: an object whose methods run under one implicit lock, plus condition variables for waiting inside those methods. The idea comes from Per Brinch Hansen and Tony Hoare in the early 1970s.

Java is the best-known example. Every object has an intrinsic lock and one implicit condition:

```
synchronized void put(T x)
        throws InterruptedException {
    while (full())
        wait();       // release, sleep
    add(x);
    notifyAll();      // wake waiters
}
```

Because there is only one condition per object, producers and consumers share it, which is why `notifyAll` is the safe default there. `java.util.concurrent.locks` offers explicit locks with several `Condition`s.

Python's `threading.Condition` bundles a lock and a CV, and its `wait_for` method writes the while loop for you:

```python
import threading
from collections import deque

items = deque()
cv = threading.Condition()

def put(x):
    with cv:
        items.append(x)
        cv.notify()

def get():
    with cv:
        cv.wait_for(lambda: items)
        return items.popleft()
```

`wait_for(predicate)` checks the predicate, waits, and re-checks it on every wakeup, returning once it is true.

## Semaphores or condition variables?

They are equally powerful: each can be built from the other plus a mutex. In practice:

| | Semaphore | Mutex + CV |
|---|---|---|
| Remembers signals | yes (count) | no |
| Condition | "count > 0" | any predicate |
| Ownership | none | mutex has owner |
| Typical use | pools, signalling | general waiting |

Semaphores are compact for counting problems. Condition variables are clearer for arbitrary conditions ("queue not empty *and* not shutting down"), because the condition is written explicitly in the while loop rather than encoded in a count. Many style guides prefer CVs for that reason.

## Common mistakes

1. **Waiting with `if` instead of `while`.** Breaks under Mesa semantics and spurious wakeups.
2. **Signalling without changing state.** The waiter re-checks, finds nothing changed, and sleeps again.
3. **Changing state without holding the mutex.** Creates a lost-wakeup window even if the signal happens later.
4. **Calling `wait` without holding the mutex.** Undefined in POSIX; Python raises `RuntimeError`.
5. **Doing long work while holding the mutex** after waking. Take what you need, unlock, then work.

For POSIX condition variables, signalling with or without the mutex held is permitted, but predicate changes and object lifetime must remain correctly coordinated. Python notify/notify_all and Java notify/notifyAll require holding their associated lock or monitor; the POSIX rule must not be copied into those APIs.

## Key takeaways
- A semaphore is a counter of permits: init 1 for a lock, N for a pool, 0 for "wait until it happens". It remembers posts and has no owner.
- A condition variable has no memory. The condition lives in shared state protected by a mutex, and `wait` atomically releases that mutex and sleeps.
- Always wait in a `while` loop: Mesa semantics let state change before you run, and POSIX permits spurious wakeups.
- Use `signal` when any one waiter will do and `broadcast` when waiters wait for different things; separate CVs per condition avoid thundering herds.
- Monitors (Java `synchronized`, Python `Condition`) bundle a lock with condition variables into one structured construct.

## Further reading
- [OSTEP: Condition variables (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-cv.pdf)
- [OSTEP: Semaphores (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-sema.pdf)
- [pthread_cond_wait — POSIX manual page](https://man7.org/linux/man-pages/man3/pthread_cond_wait.3p.html)
- [Semaphore (programming) — Wikipedia](https://en.wikipedia.org/wiki/Semaphore_(programming))
- [Monitor (synchronization) — Wikipedia](https://en.wikipedia.org/wiki/Monitor_(synchronization))
- [Spurious wakeup — Wikipedia](https://en.wikipedia.org/wiki/Spurious_wakeup)
- [threading — Python documentation](https://docs.python.org/3/library/threading.html)
