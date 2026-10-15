---
id: dl-fundamentals-cycle
title: Recognising a deadlock cycle
level: basic
minutes: 4
sourceLesson: dl-fundamentals
summary: A deadlocked set has a circular dependency that its members cannot resolve alone.
---

In the previous module you learnt to protect shared data with locks, semaphores and condition variables. Those tools fix races, but they introduce a new way to fail: threads that wait for each other forever.

A set of threads is **deadlocked** when every thread in the set is waiting for something that only another thread in the same set can provide. Nobody can move, so nobody ever will. The affected operations stop making progress. Sleeping lock waits can consume little CPU, while deadlocked spinlocks can burn CPU; detectors, timeouts or recovery logic may report errors.

## The intuition: a four-way junction

Picture four cars arriving at a junction with no traffic lights, each wanting to go straight on. Each car edges forward into the middle and now blocks the car on its left. Every driver is waiting for the car in front to move, and that car is waiting for the next. Nobody is doing anything wrong locally, yet the whole junction is frozen.

Two things are worth noticing:

- Each car **holds** some road while **waiting** for more.
- The waiting forms a **circle**. If any one car could reverse, the jam would clear.

That is deadlock in miniature.

## The classic bug: two locks in opposite order

Here is a common deadlock pattern. Two threads transfer money between the same two accounts, in opposite directions.

```python
import threading

class Account:
    def __init__(self, name, balance):
        self.name = name
        self.balance = balance
        self.lock = threading.Lock()

def transfer(src, dst, amount):
    # Opposite transfers choose opposite
    # locks.
    with src.lock:          # lock 1
        with dst.lock:      # lock 2
            src.balance -= amount
            dst.balance += amount

a = Account("A", 100)
b = Account("B", 100)

t1 = threading.Thread(
    target=transfer, args=(a, b, 10))
t2 = threading.Thread(
    target=transfer, args=(b, a, 20))
t1.start(); t2.start()
```

Some schedules finish; this interleaving deadlocks:

```
time  thread 1         thread 2
 1    lock A  (ok)
 2                     lock B  (ok)
 3    lock B  (waits)
 4                     lock A  (waits)
      ... forever ...
```

Thread 1 holds A and wants B. Thread 2 holds B and wants A. Neither `with` block can finish, so neither lock is ever released.

> [!warning] Deadlocks hide in testing
> The bad interleaving needs a context switch in a narrow window. A test suite may run it a million times without failing, then production hits it under load on a Friday night. "It passed the tests" tells you very little about deadlock.

## The four Coffman conditions

For the classical reusable-resource model, Coffman, Elphick and Shoshani's 1971 treatment identifies four necessary conditions for resource deadlock:

1. **Mutual exclusion.** At least one resource can be held by only one thread at a time. (A mutex, a printer, a row lock held for writing.)
2. **Hold and wait.** A thread holds at least one resource while waiting to acquire another.
3. **No preemption.** A resource cannot be forcibly taken away; the holder must release it voluntarily.
4. **Circular wait.** There is a cycle of waiting threads: each waits for a resource held by the next, and the last waits for the first.

Check them against the transfer bug:

| Condition | In the transfer bug |
|---|---|
| Mutual exclusion | Only one acquisition succeeds at a time |
| Hold and wait | Holds `src`, wants `dst` |
| No preemption | No participant forcibly releases the other lock |
| Circular wait | T1 → T2 → T1 |

The resource model and acquisition policy determine which conditions are possible; actual hold-and-wait and circular-wait relationships describe a particular state. The conditions are necessary: break any one of them and deadlock is impossible. That fact is the basis of every prevention technique in the next lesson.

> [!note] Necessary, and with single instances, sufficient
> When every resource has exactly one instance (as with ordinary mutexes), a cycle of waiting threads *is* a deadlock. When resources have several identical instances (say, 3 database connections), a cycle is necessary but not always sufficient, as we will see below.

## Key takeaways
- A deadlocked set has a circular dependency that its members cannot resolve alone.
- All four classical Coffman conditions are necessary; breaking one prevents resource deadlock.
- Opposite lock orders permit a deadlocking schedule even if many test runs finish.

## Further reading
- [OSTEP: Common Concurrency Problems](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-bugs.pdf)
- [Python: primitive and re-entrant locks](https://docs.python.org/3/library/threading.html)
