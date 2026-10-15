---
id: dl-detection-recovery-engine-policy
title: How database engines detect and recover
level: intermediate
minutes: 2
sourceLesson: dl-detection-recovery
summary: PostgreSQL delays checking a waiting backend; the chosen victim is not an application contract.
---

## Databases in practice

These three engines detect deadlocks, but they differ in when they look and whom they kill.

**PostgreSQL** doesn't check on every wait. A backend that has been waiting for a lock for `deadlock_timeout` (default 1 s) runs the check itself, walking the wait-for graph from its own transaction. If it finds a cycle, it normally aborts its own transaction with `ERROR: deadlock detected` (SQLSTATE `40P01`). The docs warn that which transaction gets aborted is hard to predict and shouldn't be relied on. The log message lists each process, what it waited for and who blocked it.

**MySQL InnoDB** enables detection by default through `innodb_deadlock_detect`. In the MySQL 8.4 source, wait-graph changes wake a detector thread; detection is not a zero-delay synchronous guarantee. It tries to roll back the **smallest** transaction, measured by the number of rows inserted, updated or deleted, and returns error 1213. On very high-concurrency systems the check itself can become a bottleneck, so some operators turn it off and rely on `innodb_lock_wait_timeout` (default 50 s) instead.

**SQL Server** runs a background lock monitor that searches every 5 seconds by default, dropping to as little as 100 ms while it keeps finding deadlocks. The victim is the session with the lowest `DEADLOCK_PRIORITY`; on a tie, the transaction that is cheapest to roll back. The victim gets error 1205.

> [!note] Timeouts are a cruder detector
> A lock timeout ends an overlong wait without proving a cycle. PostgreSQL marks the current transaction or subtransaction failed. InnoDB normally rolls back only the timed-out statement, leaving the transaction and earlier locks active; explicitly roll back the transaction when abandoning/retrying the whole unit. Merely timing out a statement does not guarantee that every held lock is released. A timeout cannot distinguish deadlock from a slow holder.

## Key takeaways
- PostgreSQL delays checking a waiting backend; the chosen victim is not an application contract.
- InnoDB and SQL Server have their own detector and victim policies.
- A statement timeout may leave earlier locks active, so whole-transaction retry needs explicit cleanup.

## Further reading
- [PostgreSQL: explicit locking and deadlocks](https://www.postgresql.org/docs/current/explicit-locking.html)
- [MySQL 8.4: InnoDB deadlock detection](https://docs.oracle.com/cd/E17952_01/mysql-8.4-en/innodb-deadlock-detection.html)
- [SQL Server: deadlock detection and victims](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-deadlocks-guide)
