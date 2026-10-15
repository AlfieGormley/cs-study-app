---
id: dl-prevention-ordering
title: A strict global order for locks
level: intermediate
minutes: 4
sourceLesson: dl-prevention
summary: Every nested acquisition must follow the same strict order over distinct locks.
---

## Breaking circular wait: lock ordering

This is the workhorse. Put all locks in a **total order** and require every thread to acquire them in increasing order. Then a cycle is impossible.

Why: suppose the waiting threads formed a cycle. Each thread holds a lock and waits for a higher-numbered one held by the next thread. Write down the locks' positions in the order, going round the cycle:

```formula
r(L_1) < r(L_2) < … < r(L_k) < r(L_1)
where
L_1, L_2, …, L_k: the locks held by the threads around the supposed cycle: thread 1 holds L_1 and waits for L_2, which thread 2 holds, and so on; the last thread waits for L_1
k: the number of threads (and locks) in the cycle, at least 2
r(L): the rank of lock L: its position in the agreed total order, 1 for the lock that must be taken first
<: is less than
…: the steps in between
In words: going round the cycle the rank rises at every step, yet it ends at the lock it started from, which would make r(L_1) smaller than itself.
```

A number can't be less than itself, so no such cycle exists. For example, with account locks ranked by id, a thread holding account 17 may wait for account 42, but no thread holding 42 ever waits for 17, so the chain of waits can never come back round. The argument needs every acquisition to obey the order, and the order to be *strict*: two locks with the same rank would break it.

Applied to the transfer bug:

```python
def transfer(src, dst, amount):
    # A primitive lock cannot be retaken
    # here.
    if src is dst:
        return
    # Both directions use the same lock
    # order.
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
-- Fragment: use the stated session setup.
BEGIN;
SELECT id FROM accounts
  WHERE id IN (17, 42)
  ORDER BY id
  FOR UPDATE;
-- now update both rows safely
```

The PostgreSQL docs say the best defence against deadlocks is generally to make every application acquire locks on multiple objects in a consistent order. Batch jobs that update many rows should also sort their keys before updating.

### The dining philosophers, solved by ordering

Five philosophers sit around a table with one utensil between each pair; each needs both neighbouring utensils. If everyone picks up their left utensil first, they can all hold one utensil and wait for the other: deadlock. Number the utensils 0 to 4 and have everyone pick up the lower-numbered utensil first. Philosopher 4, whose utensils are 4 and 0, now picks up utensil 0 first, breaking the symmetry and the cycle.

## Key takeaways
- Every nested acquisition must follow the same strict order over distinct locks.
- Stable unique keys avoid ties; the same-object case needs explicit handling.
- Consistent row acquisition order and ordered philosopher utensils apply the same proof.

## Further reading
- [OSTEP: Common Concurrency Problems](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-bugs.pdf)
- [PostgreSQL: explicit locking and deadlocks](https://www.postgresql.org/docs/current/explicit-locking.html)
