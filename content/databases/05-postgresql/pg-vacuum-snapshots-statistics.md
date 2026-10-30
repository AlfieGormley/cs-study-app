---
id: pg-vacuum-snapshots-statistics
title: Vacuum, old snapshots and statistics
level: intermediate
minutes: 5
sourceLesson: postgresql-in-practice
summary: Why update-heavy tables grow, what stops vacuum reclaiming space, and how to find the blocker.
---

Every UPDATE in Postgres writes a new row version and leaves the old one behind; a DELETE leaves its version behind too. An old version cannot be removed while any transaction might still need to see it. Once no transaction can, it is a dead tuple.

**VACUUM** removes dead versions from tables and indexes and marks their space reusable for future rows. It also maintains visibility information and freezes old rows to prevent transaction ID wraparound, covered two units later. Plain vacuum normally reuses space inside the table rather than returning it to the operating system; it only gives back completely empty pages at the very end of the table.

**ANALYZE** samples data to update planner statistics. Postgres uses those estimates to choose scan and join strategies. Autovacuum runs both automatically; monitor whether it keeps up rather than treating it as optional background noise.

## Why a table bloats

A healthy update-heavy table settles at a stable size: its live rows plus the dead space that builds up between vacuum runs, which new versions keep reusing. It grows beyond that, which is called table bloat, when dead versions pile up faster than they are reclaimed. Two causes are common:

- Vacuum runs too rarely for the update rate, which the next unit's thresholds explain.
- Something holds back the **cleanup horizon**: the oldest point in time that some transaction might still need to see. Vacuum cannot remove a version that died after that point, however often it runs.

Long-running work holds the horizon back. The usual culprits are:

- a long-running query or transaction, including one left **idle in transaction** by an application that forgot to commit;
- a forgotten prepared transaction;
- a replication slot that still records an old `xmin` from a standby that has stopped connecting (a logical slot holds back only system-catalog cleanup and WAL);
- a standby with `hot_standby_feedback` on, running long queries.

The isolation level matters for an idle transaction. Under Read Committed, each statement takes a fresh snapshot and releases it when it finishes. A transaction that has only read and then sits idle holds no snapshot, so it does not block cleanup, although it may still hold locks. A Repeatable Read transaction keeps its snapshot until it ends. A transaction that has written anything holds a transaction ID, and that also holds the horizon back until it ends.

In a PostgreSQL 18 test, updating all 10,000 rows of a small table while another session sat in an idle Repeatable Read transaction left `VACUUM (VERBOSE)` reporting "0 removed … 10000 are dead but not yet removable". Three rounds of updates and vacuums nearly quadrupled the table from 360 kB to 1,416 kB. Once the old transaction ended, the next vacuum removed all 30,000 dead versions, but the file stayed at 1,416 kB; later updates reused that free space. Only `VACUUM FULL` shrank it back to 360 kB.

> [!analogy] Real-world analogy: a library that keeps old editions for slow readers
> A library replaces its reference books with new editions but keeps each old edition on the shelf while anyone who borrowed the reading room before the change is still inside. One visitor who never leaves forces it to keep every edition published since they arrived, and the shelves fill up.
>
> **How it maps:** editions are row versions; the visitor who arrived earliest is the oldest snapshot, which sets the cleanup horizon. Clearing old editions onto a "free shelf space" list is plain VACUUM. Building a new, smaller bookcase and moving everything across is VACUUM FULL.
>
> **Where it stops:** the library knows exactly which visitor reads which book. Postgres does not track that: one old snapshot holds back cleanup of versions in every table of that database, whether or not it ever reads them, and the horizon also counts slots and standbys that are not readers at all.

## Find the blocker

Look for the oldest transactions holding a transaction ID or snapshot:

```sql
-- Oldest horizon holders first.
SELECT pid, state, xact_start,
       backend_xid, backend_xmin
FROM pg_stat_activity
WHERE backend_xid IS NOT NULL
   OR backend_xmin IS NOT NULL
ORDER BY xact_start;
```

Also check `pg_prepared_xacts` for old prepared transactions and `pg_replication_slots` for slots with an old `xmin` or `catalog_xmin`. `pg_stat_user_tables` shows each table's estimated dead tuples and its last vacuum times. Ending the blocker lets the next vacuum clean up; `idle_in_transaction_session_timeout` can end forgotten idle-in-transaction sessions automatically.

To vacuum and analyse one table by hand:

```sql
-- Run outside an explicit transaction.
VACUUM (ANALYZE) bookings;
```

Disabling autovacuum or routinely running `VACUUM FULL` is not a general fix. `VACUUM FULL` copies the table into a new file, needs extra disk space while it runs, and holds an ACCESS EXCLUSIVE lock that blocks even reads of the table until it finishes.

An update can sometimes be a heap-only tuple (HOT) update, avoiding new ordinary index entries when no non-summarising indexed column changes and the original heap page has room. This reduces index maintenance and lets dead versions be pruned within the page; it does not remove the need for vacuum. Since PostgreSQL 16, summarising indexes such as BRIN do not by themselves disqualify HOT. Leaving free space in pages with a lower `fillfactor` makes HOT updates more likely.

## Key takeaways

- An update-heavy table bloats when dead versions pile up faster than vacuum reclaims them.
- Old snapshots, written-but-uncommitted transactions, prepared transactions and replication slots with an old `xmin` hold back cleanup.
- An idle Read Committed transaction that has only read does not hold a snapshot.
- Plain VACUUM makes space reusable; the file does not shrink. VACUUM FULL rewrites and strongly locks the table.

## Further reading

- [PostgreSQL 18: routine vacuuming](https://www.postgresql.org/docs/18/routine-vacuuming.html)
- [PostgreSQL 18: VACUUM](https://www.postgresql.org/docs/18/sql-vacuum.html)
- [PostgreSQL 18: heap-only tuples](https://www.postgresql.org/docs/18/storage-hot.html)
- [PostgreSQL 18: ANALYZE](https://www.postgresql.org/docs/18/sql-analyze.html)
- [PostgreSQL 18: pg_stat_activity and statistics views](https://www.postgresql.org/docs/18/monitoring-stats.html)
