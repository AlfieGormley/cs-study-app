---
id: sync-semaphores-condvars-monitors-and-notification
title: Monitors and choosing who to wake
level: intermediate
minutes: 4
summary: Use separate predicates, appropriate notification and structured monitor APIs.
sourceLesson: sync-semaphores-condvars
---

A signalled waiter still has to reacquire the mutex and recheck its predicate. The choice of notification affects progress and overhead even when every waiter uses a correct while loop.

### signal or broadcast?

- POSIX `signal` unblocks at least one waiter, if any; callers must tolerate extra or spurious wakeups. Use it when any waiter can make progress and only one should.
- `broadcast` wakes all of them. Use it when waiters wait for *different* conditions on the same CV, or when a change could let several proceed (for example, freeing a large block that several allocation requests are waiting for).

With correctly protected predicates and a sound protocol, broadcast preserves the safety of the wait loop but can cause a **thundering herd**: 100 threads wake, contend for the mutex, 99 find nothing to do and sleep again. A common, cleaner design is one CV per condition (`not_empty`, `not_full`), so `signal` always wakes a thread that cares.

## Monitors

A **monitor** packages the pattern into a language construct: an object whose methods run under one implicit lock, plus condition variables for waiting inside those methods. The idea comes from Per Brinch Hansen and Tony Hoare in the early 1970s.

Java is the best-known example. Every object has an intrinsic lock and one implicit condition:

```java
synchronized void put(T x)
        throws InterruptedException {
    while (full())
        wait();       // release, sleep
    add(x);
    // Both caller kinds share a wait set.
    notifyAll();      // wake waiters
}
```

Because there is only one condition per object, producers and consumers share it, which is why `notifyAll` is the safe default there. `java.util.concurrent.locks` offers explicit locks with several `Condition`s.

Python's `threading.Condition` combines a lock and a CV, and its `wait_for` method writes the while loop for you:

```python
import threading
from collections import deque

items = deque()
cv = threading.Condition()

def put(x):
    with cv:
        # Publish state under the same lock.
        items.append(x)
        cv.notify()

def get():
    with cv:
        cv.wait_for(lambda: items)
        # Predicate and removal share a
        # lock.
        return items.popleft()
```

Here, without a timeout, `wait_for(predicate)` checks the predicate under the associated lock, waits and rechecks until it returns a true value. With a timeout it may instead return a false value when time expires.

## Semaphores or condition variables?

They are equally powerful: each can be built from the other plus a mutex. In practice:

| | Semaphore | Mutex + CV |
|---|---|---|
| Remembers signals | yes (count) | no |
| Condition | count above 0 | any predicate |
| Ownership | none | mutex has owner |
| Typical use | pools, signalling | general waiting |

Semaphores are compact when the problem is really about counting. Condition variables are clearer for arbitrary conditions ("queue not empty *and* not shutting down"), because the condition is written explicitly in the while loop rather than encoded in a count. Many style guides prefer CVs for that reason.

## Common mistakes

1. **Waiting with `if` instead of `while`.** Breaks under Mesa semantics and spurious wakeups.
2. **Signalling without changing state.** The waiter re-checks, finds nothing changed, and sleeps again.
3. **Changing state without holding the mutex.** Creates a lost-wakeup window even if the signal happens later.
4. **Calling `wait` without holding the mutex.** Undefined in POSIX; Python raises `RuntimeError`.
5. **Doing long work while holding the mutex** after waking. Take what you need, unlock, then work.

For POSIX condition variables, signalling with or without the mutex held is permitted, but predicate changes and object lifetime must remain correctly coordinated. Python notify/notify_all and Java notify/notifyAll require holding their associated lock or monitor; the POSIX rule must never be copied into those APIs.

## Key takeaways

- Signal is appropriate when any awakened waiter can make progress; broadcast is useful for multiple predicates or several eligible waiters.
- Separate condition variables can keep producers from waking other producers.
- Python and Java notification require the associated lock; POSIX permits signalling without it under a sound predicate/lifetime protocol.

## Further reading

- [OSTEP: Condition variables](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-cv.pdf)
- [OSTEP: Semaphores](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-sema.pdf)
- [POSIX condition wait](https://pubs.opengroup.org/onlinepubs/9799919799/functions/pthread_cond_wait.html)
- [Python threading](https://docs.python.org/3/library/threading.html)
- [Java Object monitor methods](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Object.html)
