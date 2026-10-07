---
id: dl-fundamentals
title: What deadlock is
level: basic
minutes: 10
summary: The four Coffman conditions, resource-allocation graphs, and the everyday ways code and databases end up stuck forever.
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
4. **Circular wait.** There is a cycle of threads T1, T2, ..., Tn where each waits for a resource held by the next, and Tn waits for T1.

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

## Resource-allocation graphs

A **resource-allocation graph** (RAG) makes the conditions visible. It has two kinds of node and two kinds of edge:

- Circles are threads (or processes): `T1`, `T2`.
- Boxes are resources: `[A]`, `[B]`. Dots inside a box show how many instances it has.
- A **request edge** `T → R` means T is waiting for R.
- An **assignment edge** `R → T` means R is held by T.

The transfer deadlock looks like this:

```
     holds           wants
 [A] -----> (T1) -----> [B]
  ^                      |
  |  wants        holds  |
  +------ (T2) <---------+
```

Follow the arrows: A → T1 → B → T2 → A. A cycle.

### When a cycle isn't a deadlock

Suppose resource R has **two** instances (two identical database connections, say) and resource S has one:

```
 R has 2 instances: held by T1 and T4
 S has 1 instance:  held by T2

 T1 wants S   (T1 -> S -> T2)
 T2 wants R   (T2 -> R -> T1, or -> T4)
```

There is a cycle T1 → S → T2 → R → T1. But T4 also holds an instance of R and is not waiting for anything. When T4 finishes and releases its instance, T2 gets it, finishes, releases S, and T1 proceeds. The cycle dissolves.

So the rules are:

- **No cycle**: no deadlock, guaranteed.
- **Cycle, single-instance resources**: deadlock, guaranteed.
- **Cycle, multi-instance resources**: deadlock *possible*; you need a more careful check (the detection algorithm in lesson 4).

## Deadlock beyond mutexes

Anything a thread can wait on can be part of a deadlock cycle, not just mutexes.

- **Self-deadlock.** A thread takes a non-reentrant lock it already holds. A second blocking acquisition of a held `threading.Lock` waits; if no other thread releases it, this is self-deadlock. `threading.RLock` supports same-thread re-entry.
- **Joining.** Thread A calls `b.join()` while holding a lock that B needs before it can exit.
- **Bounded queues.** Producer P blocks on a full queue Q1 while consumer C blocks putting a reply onto full queue Q2 that P is supposed to drain.
- **Thread pools.** A task running on a pool of size 4 submits a sub-task to the same pool and waits for its result. If all 4 workers do this at once, no worker is free to run any sub-task. This is a classic in Java `ExecutorService` and Python `concurrent.futures` code.
- **Processes and pipes.** A parent writes a large input to a child's stdin and only then reads its stdout. The child fills its stdout pipe buffer (capacity depends on page size, limits and configuration) and blocks writing; the parent blocks writing because the child stopped reading. Python's `subprocess` docs warn about exactly this and recommend `communicate()`.

## Database deadlocks

Database writes can acquire row, page or table locks, with duration depending on engine, isolation level and lock type. PostgreSQL row locks from these updates normally last until transaction end (commit or rollback). That makes them a rich source of deadlocks, often in code with no explicit locking at all.

```sql
-- Session 1
BEGIN;
UPDATE accounts SET bal = bal - 10
  WHERE id = 1;            -- locks row 1

-- Session 2
BEGIN;
UPDATE accounts SET bal = bal - 20
  WHERE id = 2;            -- locks row 2

-- Session 1
UPDATE accounts SET bal = bal + 10
  WHERE id = 2;            -- waits for S2

-- Session 2
UPDATE accounts SET bal = bal + 20
  WHERE id = 1;            -- waits for S1
```

This is the transfer bug again, written in SQL. The difference is that databases expect it. PostgreSQL, after a session has waited for `deadlock_timeout` (default 1 second), runs a deadlock check, finds the cycle and aborts one transaction with `ERROR: deadlock detected` (SQLSTATE `40P01`). The other transaction then proceeds. SQL Server returns error 1205 and MySQL's InnoDB returns error 1213 in the same situation.

So a database turns a permanent hang into a **failed transaction** that your application must be ready to retry. Lesson 4 looks at how they do it.

## Deadlock, or just slow?

When a service "hangs", it is worth separating three situations, because they have different fixes:

| Symptom | Likely cause |
|---|---|
| 0% CPU, threads blocked on locks | Deadlock |
| 100% CPU, no progress | Livelock or busy loop |
| Progress, but some requests never finish | Starvation |

Sleeping deadlock victims may wait on futexes or conditions, while spin deadlocks can consume CPU. Low CPU and blocked stacks are clues rather than proof of a cycle. A thread dump (lesson 6) will show each stuck thread's stack and, often, which lock it is waiting for.

## Four strategies for dealing with deadlock

The rest of this module follows the classic taxonomy:

1. **Prevention**: design the system so that one Coffman condition can never hold (lesson 2).
2. **Avoidance**: let the system check each request and refuse those that could lead to deadlock (lesson 3).
3. **Detection and recovery**: let deadlocks happen, notice them, and break them by killing or rolling back a victim (lesson 4).
4. **Ignore it**: the "ostrich algorithm". General-purpose OS kernels largely do this for user-space locks: if your program deadlocks its own threads, Linux will not intervene. It is your bug.

Applications can prevent cycles through lock ordering; databases can combine ordering, detection and other concurrency controls. Avoidance illustrates explicit reasoning about safe resource states.

## Key takeaways
- Deadlock is a set of threads each waiting for another member of the set; the affected operations cannot progress without external recovery; CPU use depends on the waiting mechanism.
- All four Coffman conditions must hold: mutual exclusion, hold and wait, no preemption and circular wait. Break one and deadlock cannot happen.
- Inconsistent lock order is a common cause.
- In a resource-allocation graph, a cycle means deadlock when every resource has one instance, but only possible deadlock when resources have several.
- Anything you can wait on can deadlock: joins, bounded queues, thread pools, pipes and database row locks.
- Databases detect deadlocks and abort a victim transaction, so application code must handle the error and may safely retry the whole logical transaction with a limit.

## Further reading
- [Deadlock (computer science) — Wikipedia](https://en.wikipedia.org/wiki/Deadlock_(computer_science))
- [OSTEP: Common Concurrency Problems (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-bugs.pdf)
- [PostgreSQL docs: Explicit Locking and Deadlocks](https://www.postgresql.org/docs/current/explicit-locking.html)
- [The Java Tutorials: Deadlock](https://docs.oracle.com/javase/tutorial/essential/concurrency/deadlock.html)
