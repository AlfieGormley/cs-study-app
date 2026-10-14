---
id: db-isolation-engine-differences
title: Isolation level names across engines
level: advanced
minutes: 3
summary: Compare PostgreSQL, InnoDB, Oracle and SQL Server rather than treating a level name as a universal guarantee.
sourceLesson: db-transactions-isolation
---

The anomaly traces explain what can go wrong. Now compare how each engine implements named isolation levels: the same name can protect a different set of reads and writes.

## The SQL standard levels

| Level | Forbids |
|---|---|
| Read Uncommitted | Nothing beyond dirty writes |
| Read Committed | + dirty reads |
| Repeatable Read | + non-repeatable reads |
| Serializable | + phantoms; must be serializable |

The standard defined these in terms of a few anomalies and is famously ambiguous: it doesn't mention lost updates or write skew at all. Real databases use the same names for quite different things.

### What each database actually gives you

**PostgreSQL** (default Read Committed):

- Read Uncommitted behaves exactly like Read Committed; Postgres never shows dirty data.
- Read Committed takes a new snapshot per statement.
- Repeatable Read is **snapshot isolation**. Unlike the standard's minimum, it also prevents phantoms, and it aborts a transaction that tries to update a row someone else changed after its snapshot. Write skew is still allowed.
- Serializable is **SSI**, truly serializable (since 9.1).

**MySQL InnoDB** (default Repeatable Read):

- Read Uncommitted really does allow dirty reads.
- Repeatable Read is a hybrid. Plain `SELECT`s read from a snapshot taken at the first read. But `UPDATE`, `DELETE` and locking reads (`FOR UPDATE`, `FOR SHARE`) use current locking reads. Locking depends on the access path: a unique-index lookup of a unique key locks the record alone, while range scans generally use next-key (row plus gap) locks.
- There's no first-committer-wins check, so a read-then-write race silently loses an update, and write skew is possible.
- Serializable is Repeatable Read with plain `SELECT`s turned into `SELECT ... FOR SHARE` (when autocommit is off): lock-based, effectively 2PL.

**Oracle** (default Read Committed):

- Offers only Read Committed and Serializable (plus a Read Only mode). There is no Read Uncommitted or Repeatable Read.
- Its Serializable is **snapshot isolation**: it raises `ORA-08177` on a write-write conflict but allows write skew, so it isn't truly serializable.

**SQL Server** (default Read Committed, implemented with short read locks unless `READ_COMMITTED_SNAPSHOT` is on, which it is by default in Azure SQL Database) offers a separate `SNAPSHOT` level that is snapshot isolation, and a Serializable level that uses key-range locks (2PL).

> [!warning] Names lie
> "Repeatable Read" means snapshot isolation in Postgres and a snapshot-plus-locking hybrid in MySQL; "Serializable" means SSI in Postgres and snapshot isolation in Oracle. Always check what your database's level actually prevents. Jepsen's analyses have repeatedly found databases that didn't deliver the isolation they advertised.

## Follow current writes as well as snapshots

InnoDB transactions also see their own writes. If a plain snapshot read counts ten new jobs, another transaction commits an eleventh, and an UPDATE changes all currently new jobs, that UPDATE can change eleven. A later plain SELECT can see all eleven changes because they now belong to the reading transaction. PostgreSQL Repeatable Read would not include the newly inserted job in that UPDATE.

## Key takeaways
- PostgreSQL Read Committed takes one snapshot per statement; Repeatable Read is snapshot isolation.
- InnoDB Repeatable Read mixes snapshot SELECTs with current locking writes.
- Oracle Serializable is snapshot isolation; the same names do not imply identical guarantees.

## Further reading
- [PostgreSQL: Transaction isolation](https://www.postgresql.org/docs/current/transaction-iso.html)
- [MySQL: Transaction isolation levels](https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-isolation-levels.html)
- [Oracle: Data concurrency and consistency](https://docs.oracle.com/en/database/oracle/oracle-database/19/cncpt/data-concurrency-and-consistency.html)
