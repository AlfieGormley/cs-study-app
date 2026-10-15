---
id: dl-prevention-try-lock
title: Try-lock, release and retry
level: intermediate
minutes: 2
sourceLesson: dl-prevention
summary: A failed nonblocking second acquisition releases the first lock before retry.
---

## Try-lock and rollback

If a thread cannot acquire the next lock immediately, it releases the ones it acquired for this attempt before retrying. This avoids blocking hold-and-wait; it does not forcibly preempt another owner's lock.

```python
import random
import time

def lock_both(a, b):
    if a is b:
        raise ValueError("distinct locks")
    while True:
        a.acquire()
        if b.acquire(blocking=False):
            return            # got both
        # Release before another acquisition
        # try.
        a.release()           # back off
        time.sleep(random.uniform(0, 0.01))
```

`acquire(blocking=False)` returns `True` immediately if it got the lock and `False` otherwise. In C the equivalent is `pthread_mutex_trylock`, which returns `EBUSY` when the mutex is taken. Java has `ReentrantLock.tryLock()`.

Assume callers hold no other locks and successful callers eventually release both. This acquisition loop avoids a blocking cycle because it never waits for b while holding a. If `b` is busy it releases `a` and starts again, so the hold-and-wait edge never persists.

Pitfalls:

- **Livelock.** Two threads that grab, fail, release and retry in lockstep can spin forever without progress. Random sleep can break the symmetry but gives no deterministic fairness bound; the liveness lessons covers this properly.
- **Wasted work.** If you did work between the two acquisitions, you must undo it before backing off.
- **Composability.** It only works when you control both acquisitions. It can't help if the second lock is taken deep inside a library.

A related tool is the **timed** acquire, `lock.acquire(timeout=0.5)`. A timeout turns a permanent hang into an error you can handle, but it can't tell a deadlock from a slow holder, so treat it as a safety net, not a design.

Databases do preemption at a larger scale: they abort and roll back a transaction to free its locks. That is recovery rather than prevention, and the detection and recovery lessons covers it.

## Key takeaways
- A failed nonblocking second acquisition releases the first lock before retry.
- Avoiding a blocking cycle does not guarantee freedom from livelock or starvation.
- Timed acquisition is a recovery backstop and cannot distinguish a slow holder from deadlock.

## Further reading
- [Python: primitive and re-entrant locks](https://docs.python.org/3/library/threading.html)
- [OSTEP: Common Concurrency Problems](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-bugs.pdf)
