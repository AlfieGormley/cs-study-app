---
id: db-mvcc-snapshot-conflicts
title: MVCC snapshots and write conflicts
level: advanced
minutes: 3
summary: Explain row-version visibility, retained-snapshot bloat and why snapshot isolation still permits write skew.
sourceLesson: db-transactions-isolation
---

A snapshot chooses which row versions a transaction can see. Stable visibility is useful for reports, but it does not by itself protect every invariant across different rows.

## MVCC: how reads avoid blocking

**Multiversion concurrency control** keeps several versions of each row. A writer creates a new version rather than overwriting, so readers can carry on reading the old one. *Plain snapshot reads avoid row-level reader/writer blocking.* Table locks, explicit locking reads and DDL can still block.

In Postgres each row version has `xmin` (the transaction that created it) and `xmax` (the one that deleted or replaced it). A transaction's **snapshot** records which transactions had committed when it started; a version is visible if its `xmin` committed before the snapshot and its `xmax` didn't.

```
row id=1 versions:
 [xmin=100 xmax=205 bal=100]
 [xmin=205 xmax=  - bal= 50]
snapshot taken before tx 205
committed → sees bal=100
```

Old versions are garbage-collected later: by `VACUUM` in Postgres, and purge of undo logs in InnoDB. An old retained snapshot or transaction-id horizon can delay cleanup and cause **bloat**; merely issuing BEGIN without acquiring such a horizon is not sufficient.

- **Read Committed** takes a new snapshot per *statement*.
- **Snapshot isolation / Repeatable Read** takes one snapshot per *transaction* (in Postgres, at its first non-transaction-control statement, not at BEGIN).

## Snapshot isolation

Under SI, a transaction sees a consistent snapshot as of its start, and its own writes. On write-write conflicts, **first committer wins**: if T2 tries to update a row that T1 updated and committed after T2's snapshot was taken, T2 aborts. In Postgres, T2 first waits on T1's row lock; if T1 commits, T2 fails with `could not serialize access due to concurrent update`, and if T1 rolls back, T2 carries on.

SI prevents dirty reads, non-repeatable reads, read skew, most phantoms, and lost updates on the same row. It **does not prevent write skew**, because the conflict check only looks at rows both transactions *wrote*.

## One snapshot for a report

Separate Read Committed statements can add branch balances from different instants, even inside one transaction. PostgreSQL Repeatable Read uses one snapshot for the report, avoiding that mixture. The report can still retain old versions and take table locks; stable row visibility does not mean zero operational cost.

## Key takeaways
- Plain snapshot reads avoid row-level reader/writer blocking; table locks and DDL still matter.
- Old retained snapshots can delay cleanup and create bloat.
- Snapshot isolation rejects conflicting same-row writes but permits decisions that update different rows.

## Further reading
- [PostgreSQL: Transaction isolation](https://www.postgresql.org/docs/current/transaction-iso.html)
- [www.postgresql.org: explicit locking](https://www.postgresql.org/docs/current/explicit-locking.html)
