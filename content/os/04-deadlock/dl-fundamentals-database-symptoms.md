---
id: dl-fundamentals-database-symptoms
title: Database deadlocks and diagnostic clues
level: basic
minutes: 3
sourceLesson: dl-fundamentals
summary: Database recovery aborts a victim; applications must handle the failed transaction.
---

## Database deadlocks

Database writes can acquire row, page or table locks, with duration depending on engine, isolation level and lock type. PostgreSQL row locks from these updates normally last until transaction end (commit or rollback). That makes them a rich source of deadlocks, often in code with no explicit locking at all.

```sql
-- Fragment: use the stated session setup.
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

So a database turns a permanent hang into a **failed transaction** that your application must be ready to retry. The detection and recovery lessons looks at how they do it.

## Deadlock, or just slow?

When a service "hangs", it is worth separating three situations, because they have different fixes:

| Symptom | Likely cause |
|---|---|
| 0% CPU, threads blocked on locks | Deadlock |
| 100% CPU, no progress | Livelock or busy loop |
| Progress, but some requests never finish | Starvation |

Sleeping deadlock victims may wait on futexes or conditions, while spin deadlocks can consume CPU. Low CPU and blocked stacks are clues rather than proof of a cycle. A thread dump (the debugging lessons) will show each stuck thread's stack and, often, which lock it is waiting for.

## Four strategies for dealing with deadlock

The rest of this module follows the classic taxonomy:

1. **Prevention**: design the system so that one Coffman condition can never hold (the prevention lessons).
2. **Avoidance**: let the system check each request and refuse those that could lead to deadlock (the avoidance lessons).
3. **Detection and recovery**: let deadlocks happen, notice them, and break them by killing or rolling back a victim (the detection and recovery lessons).
4. **Ignore it**: the "ostrich algorithm". General-purpose OS kernels largely do this for user-space locks: if your program deadlocks its own threads, Linux will not intervene. It is your bug.

Applications can prevent cycles through lock ordering; databases can combine ordering, detection and other concurrency controls. Avoidance illustrates explicit reasoning about safe resource states.

## Key takeaways
- Database recovery aborts a victim; applications must handle the failed transaction.
- CPU use and blocked stacks are clues; confirm the dependency cycle.
- Prevention, avoidance, detection/recovery and leaving recovery to the application are different strategies.

## Further reading
- [PostgreSQL: explicit locking and deadlocks](https://www.postgresql.org/docs/current/explicit-locking.html)
- [OSTEP: Common Concurrency Problems](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-bugs.pdf)
