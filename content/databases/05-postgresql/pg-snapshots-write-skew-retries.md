---
id: pg-snapshots-write-skew-retries
title: Snapshots, write skew and retries
level: intermediate
minutes: 3
sourceLesson: postgresql-in-practice
summary: A stable snapshot does not prevent write skew.
---

Postgres uses **MVCC**: updates create new row versions, and snapshots decide which versions a query can see. Ordinary reads generally do not block ordinary writes, but writers updating the same row can block each other. Schema changes and explicit locks introduce other conflicts.

| Isolation | Read behaviour | Remaining responsibility |
|---|---|---|
| Read Committed | New snapshot per statement | Protect multi-step decisions |
| Repeatable Read | Stable transaction snapshot | Handle write skew and retries |
| Serializable | Successful work matches a one-at-a-time order | Retry aborted transactions |

Read Committed is the default. Two SELECTs in one transaction can see different committed values. Repeatable Read keeps a snapshot from its first non-transaction-control statement, but it is not equivalent to serial transaction execution. At every level, a transaction can see its own prior writes.

Imagine two on-call staff, both active. Each transaction sees two active staff and marks a different person inactive. At Repeatable Read, they can update different rows and both commit, breaking the rule that someone must remain on call. This is **write skew**. Use a suitable shared locking protocol or Serializable transactions for all operations maintaining that rule.

Serializable can reject a conflicting transaction with SQLSTATE `40001`. Retry the **whole transaction**, including its reads and decisions, with a bounded retry policy. Retrying only the last statement can reuse a decision based on an obsolete snapshot. Deadlocks can also require a transaction retry; acquire multiple row locks in a consistent order to reduce them.

For a more involved read-then-change operation, `SELECT ... FOR UPDATE` can lock the selected rows. It does not lock an imaginary row that does not exist, so use constraints or a suitable isolation strategy for “insert if absent” rules.

## Key takeaways

- A stable snapshot does not prevent write skew.
- Serializable participants must retry the whole failed transaction.
- Locking existing rows does not lock an absent row.

## Further reading

- [PostgreSQL 18: transaction iso](https://www.postgresql.org/docs/18/transaction-iso.html)
- [PostgreSQL 18: explicit locking](https://www.postgresql.org/docs/18/explicit-locking.html)
- [PostgreSQL 18: mvcc serialization failure handling](https://www.postgresql.org/docs/18/mvcc-serialization-failure-handling.html)
