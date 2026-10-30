---
id: pg-xid-freezing-wraparound
title: Why transaction IDs need freezing
level: intermediate
minutes: 4
sourceLesson: postgresql-in-practice
summary: Transaction IDs wrap around after about two billion, so vacuum must freeze old rows before they look like the future.
---

PostgreSQL assigns a normal **transaction ID** (XID) when a transaction needs one, commonly when it first writes. A transaction that only reads never gets one unless it asks explicitly, for example by calling `pg_current_xact_id()`. Row-version headers record which XID inserted them and, if any, which deleted them. MVCC compares those XIDs with the current one to decide whether a version was written in the past (possibly visible) or the future (invisible).

## A counter that wraps around

The XIDs in row headers are 32-bit numbers, so there are about 4.3 billion of them, and the counter wraps back to the start when it runs out. Comparison is therefore circular: from any XID, the roughly 2.1 billion values behind it count as the past and the roughly 2.1 billion ahead count as the future. Newer SQL functions can expose a 64-bit full ID that adds an XID epoch, but row headers still store the 32-bit value.

If a row version kept its original XID while the counter moved more than about 2.1 billion transactions on, it would suddenly look as if it came from the future, and committed data would vanish from queries. This is **transaction ID wraparound**.

VACUUM prevents it by **freezing** old row versions: marking their committed insertion as old enough to be visible to every current and future transaction, so that insertion XID no longer needs normal comparison. Freezing does not lock a row against change; a later update or deletion still follows the usual visibility rules. Even a table whose contents never change must be frozen, because the counter keeps advancing with every write elsewhere in the cluster.

> [!analogy] Real-world analogy: times on a 12-hour clock
> If a note says "3 o'clock" and it is now 5 o'clock, you assume the note means two hours ago. That only works if you know the note is less than half a day old: a note from yesterday's 3 o'clock would be read wrongly, and one from 10 hours ago looks like "in two hours". Archivists avoid this by stamping old notes "long ago" instead of keeping the clock time.
>
> **How it maps:** clock times are 32-bit XIDs, and half the dial is the roughly 2.1-billion-ID window treated as the past. Stamping a note "long ago" is freezing: the row is then treated as older than every transaction, whatever its original number.
>
> **Where it stops:** a clock goes round every 12 hours whether or not anything happens, but the XID counter advances only when transactions take IDs, so wraparound depends on write activity, not elapsed time.

## Forced freezing and what blocks it

Postgres forces an anti-wraparound vacuum on any table whose oldest unfrozen XID is more than `autovacuum_freeze_max_age` XIDs old: 200 million by default, about one tenth of the 2.1-billion window, leaving a wide safety margin. These limits count allocated IDs, not elapsed time. Anti-wraparound vacuums run even when autovacuum is disabled.

Freezing can only advance past rows that no transaction might still need, so the same things that block ordinary cleanup also stop the oldest XID moving forward: long-running or idle-in-transaction sessions, forgotten prepared transactions and stale replication slots. If the age keeps climbing, the server starts warning when about 40 million IDs remain before wraparound. With fewer than about 3 million left, it refuses to start transactions that need new XIDs, so writes fail while queries that only read continue, until a vacuum catches up.

Monitor the age of the oldest unfrozen XID in each database:

```sql
-- Compare with autovacuum_freeze_max_age.
SELECT datname, age(datfrozenxid)
FROM pg_database
ORDER BY 2 DESC;
```

A steady climb towards and beyond 200 million, while anti-wraparound vacuums run, points at something blocking freezing. Find and end the blocker, then let vacuum run; the documentation advises against stopping the server or using single-user mode to recover.

## Key takeaways

- 32-bit XID comparisons look about two billion IDs into the past and two billion into the future.
- Freezing marks old committed insertions as visible to everyone, so wraparound cannot hide them.
- Old transactions, prepared transactions and stale replication slots stop freezing advancing.
- Near the limit, PostgreSQL refuses new XIDs, stopping writes, until vacuum catches up.

## Further reading

- [PostgreSQL 18: routine vacuuming](https://www.postgresql.org/docs/18/routine-vacuuming.html)
- [PostgreSQL 18: object identifier types](https://www.postgresql.org/docs/18/datatype-oid.html)
- [PostgreSQL 18: system information functions](https://www.postgresql.org/docs/18/functions-info.html)
