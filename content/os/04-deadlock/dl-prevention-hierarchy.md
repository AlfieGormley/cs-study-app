---
id: dl-prevention-hierarchy
title: Enforcing a hierarchy at runtime
level: intermediate
minutes: 4
sourceLesson: dl-prevention
summary: Each new lock must have a strictly higher level than all locks already held.
---

## Lock hierarchies

On a large codebase, maintaining a global ordering over *every* lock instance can become awkward. Instead, assign each lock a **level** and require that a thread only acquires locks at a strictly higher level than any it already holds:

```formula
lvl(L_new) > lvl(L_top)
30 > 20
where
L_new: the lock the thread is about to take
L_top: the most recently taken lock the thread still holds, which has the highest level it holds
lvl(L): the level number assigned to lock L, such as 20 for an account lock and 30 for a ledger lock
>: is greater than
In words: each new lock must sit strictly higher in the hierarchy than everything the thread already holds.
```

So a thread holding an account lock (20) may take the ledger lock (30), but a thread holding the ledger may not then take an account, because 20 is not greater than 30. This is the lock-ordering argument applied to levels rather than individual locks. Locks at the same level must never be held together (or need their own ordering rule, such as by id).

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
        # Thread-local state tracks nested
        # locks.
        stack = getattr(_held, "stack", [])
        top = stack[-1] if stack else None
        # Equal levels cannot prove strict
        # order.
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

Each thread keeps a stack of the locks it holds. Taking a lock at a level no higher than the top of the stack raises immediately, *even if no deadlock happens on this run*. That is the key benefit: an ordering violation is caught in testing the first time the forbidden acquisition executes, not months later when the unlucky interleaving finally occurs.

This is the same idea as the hierarchical mutex in Anthony Williams's *C++ Concurrency in Action*, and it is roughly what the Linux kernel's lockdep does automatically, without you assigning levels (the debugging lessons).

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
- Each new lock must have a strictly higher level than all locks already held.
- A debug hierarchy catches an observed forbidden order without waiting for an actual deadlock.
- Ordering and avoiding blocking callbacks need enforcement as a codebase changes.

## Further reading
- [Linux: runtime locking correctness validator](https://docs.kernel.org/locking/lockdep-design.html)
- [OSTEP: Common Concurrency Problems](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-bugs.pdf)
