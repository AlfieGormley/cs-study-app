---
id: dl-prevention
title: Deadlock prevention
level: intermediate
minutes: 11
summary: Make deadlock structurally impossible by breaking one Coffman condition, with lock ordering, try-lock and back-off, and lock hierarchies.
---

Deadlock needs all four Coffman conditions at once: mutual exclusion, hold and wait, no preemption and circular wait. **Prevention** means designing the system so that at least one of them can never hold. If you succeed, there is nothing to detect and nothing to recover from.

This is the main strategy for application and kernel code. It costs some flexibility and concurrency, but it is cheap at run time and easy to reason about.

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
        a.release()           # back off
        time.sleep(random.uniform(0, 0.01))
```

`acquire(blocking=False)` returns `True` immediately if it got the lock and `False` otherwise. In C the equivalent is `pthread_mutex_trylock`, which returns `EBUSY` when the mutex is taken. Java has `ReentrantLock.tryLock()`.

Assume callers hold no other locks and successful callers eventually release both. This acquisition loop avoids a blocking cycle because it never waits for b while holding a. If `b` is busy it releases `a` and starts again, so the hold-and-wait edge never persists.

Pitfalls:

- **Livelock.** Two threads that grab, fail, release and retry in lockstep can spin forever without progress. Random sleep can break the symmetry but gives no deterministic fairness bound; lesson 5 covers this properly.
- **Wasted work.** If you did work between the two acquisitions, you must undo it before backing off.
- **Composability.** It only works when you control both acquisitions. It can't help if the second lock is taken deep inside a library.

A related tool is the **timed** acquire, `lock.acquire(timeout=0.5)`. A timeout turns a permanent hang into an error you can handle, but it can't tell a deadlock from a slow holder, so treat it as a safety net, not a design.

Databases do preemption at a larger scale: they abort and roll back a transaction to free its locks. That is recovery rather than prevention, and lesson 4 covers it.

## Breaking circular wait: lock ordering

This is the workhorse. Put all locks in a **total order** and require every thread to acquire them in increasing order. Then a cycle is impossible.

Why: suppose there were a cycle T1 → T2 → ... → Tn → T1. Each thread holds a lock and waits for a higher-numbered one held by the next thread. Going around the cycle the lock numbers strictly increase at every step, yet we come back to where we started. A number can't be greater than itself, so no such cycle exists.

Applied to the transfer bug:

```python
def transfer(src, dst, amount):
    if src is dst:
        return
    first, second = sorted(
        (src, dst), key=lambda acc: acc.id)
    with first.lock:
        with second.lock:
            src.balance -= amount
            dst.balance += amount
```

Now `transfer(a, b)` and `transfer(b, a)` both lock the lower id first. The second thread waits on the first lock while holding nothing, so no cycle can form.

```
time  thread 1         thread 2
 1    lock A  (ok)
 2                     lock A  (waits)
 3    lock B  (ok)
 4    ... unlock B, A
 5                     lock A  (ok)
 6                     lock B  (ok)
```

> [!warning] Order by something stable
> Use a stable total ordering that distinguishes distinct lock objects, such as unique immutable account IDs. Python id() orders live objects within a process. In portable C, relational comparison of pointers to unrelated objects is not a valid general ordering rule; use explicit keys or a documented platform convention. Address order is not a distributed identity.

> [!warning] The src == dst case
> If someone transfers from an account to itself, `first` and `second` are the same object and a non-reentrant lock deadlocks on itself. Check for it and take the lock once (or reject the transfer).

### Ordering in SQL

The same trick prevents database deadlocks. Lock rows in a consistent order at the start of the transaction:

```sql
BEGIN;
SELECT id FROM accounts
  WHERE id IN (17, 42)
  ORDER BY id
  FOR UPDATE;
-- now update both rows safely
```

The PostgreSQL docs say the best defence against deadlocks is generally to make every application acquire locks on multiple objects in a consistent order. Batch jobs that update many rows should also sort their keys before updating.

### The dining philosophers, solved by ordering

Five philosophers sit around a table with one fork between each pair; each needs both neighbouring forks. If everyone picks up their left fork first, they can all hold one fork and wait for the other: deadlock. Number the forks 0 to 4 and have everyone pick up the lower-numbered fork first. Philosopher 4, whose forks are 4 and 0, now picks up fork 0 first, breaking the symmetry and the cycle.

## Lock hierarchies

On a large codebase, a global ordering over *every* lock instance is impractical. Instead, assign each lock a **level** and require that a thread only acquires locks at a strictly higher level than any it already holds. Locks at the same level must never be held together (or need their own ordering rule, such as by id).

A typical layering:

| Level | Lock |
|---|---|
| 10 | Request / session |
| 20 | Account |
| 30 | Ledger |
| 40 | Logging, metrics |

You can enforce this at run time:

```python
import threading

_held = threading.local()

class LevelLock:
    def __init__(self, level, name):
        self.level = level
        self.name = name
        self._lock = threading.Lock()

    def __enter__(self):
        stack = getattr(_held, "stack", [])
        top = stack[-1] if stack else None
        if top and top.level >= self.level:
            raise RuntimeError(
                f"{self.name} taken while "
                f"holding {top.name}")
        self._lock.acquire()
        stack.append(self)
        _held.stack = stack
        return self

    def __exit__(self, *exc):
        _held.stack.pop()
        self._lock.release()
```

Each thread keeps a stack of the locks it holds. Taking a lock at a level no higher than the top of the stack raises immediately, *even if no deadlock happens on this run*. That is the key benefit: an ordering violation is caught in testing the first time the bad path executes, not months later when the unlucky interleaving finally occurs.

This is the same idea as the hierarchical mutex in Anthony Williams's *C++ Concurrency in Action*, and it is roughly what the Linux kernel's lockdep does automatically, without you assigning levels (lesson 6).

> [!note] Document the order
> Large systems write their lock order down. The Linux memory-management code, for example, has long comments in files such as `mm/rmap.c` listing which locks must be taken before which. A lock order that exists only in someone's head will be broken.

## Choosing a technique

| Technique | Breaks | Main cost |
|---|---|---|
| Immutable / lock-free | Mutual excl. | Design effort |
| All locks up front | Hold and wait | Less concurrency |
| Try-lock + back-off | Blocking hold-and-wait | Livelock risk |
| Lock ordering | Circular wait | Discipline |
| Lock hierarchy | Circular wait | Level design |

In practice:

1. First, **hold fewer locks**. Many deadlocks disappear when a function holds one lock at a time.
2. When you must hold two, **order them**: by id for same-type objects, by level for different types.
3. Use **try-lock** where ordering is impossible (for example, you discover the second lock only after taking the first) and add jitter.
4. **Never block** on I/O, joins or callbacks while holding a lock.
5. **Enforce** the order with assertions or tools, because conventions decay.

## Key takeaways
- Prevention makes deadlock impossible by ensuring one Coffman condition can never hold.
- Lock ordering is the standard technique: if every thread acquires locks in increasing order, no cycle can form.
- Order by a stable key (account id, level) and handle the same-lock case explicitly.
- Try-lock with release-on-failure avoids blocking hold-and-wait. Jitter can reduce livelock risk but does not guarantee fairness.
- Lock hierarchies scale ordering to large codebases and, when checked at run time, catch violations on the first bad path rather than the first bad interleaving.
- The simplest prevention of all is to hold one lock at a time and never wait while holding a lock.

## Further reading
- [OSTEP: Common Concurrency Problems (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-bugs.pdf)
- [Deadlock prevention algorithms — Wikipedia](https://en.wikipedia.org/wiki/Deadlock_prevention_algorithms)
- [pthread_mutex_trylock — man7.org](https://man7.org/linux/man-pages/man3/pthread_mutex_trylock.3p.html)
- [PostgreSQL docs: Explicit Locking](https://www.postgresql.org/docs/current/explicit-locking.html)
- [Dining philosophers problem — Wikipedia](https://en.wikipedia.org/wiki/Dining_philosophers_problem)
