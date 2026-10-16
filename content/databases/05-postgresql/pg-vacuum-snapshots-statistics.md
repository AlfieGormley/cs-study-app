---
id: pg-vacuum-snapshots-statistics
title: Vacuum, old snapshots and statistics
level: intermediate
minutes: 3
sourceLesson: postgresql-in-practice
summary: Old snapshots can delay reclamation.
---

Old row versions cannot be removed while a snapshot still needs them. **VACUUM** makes space from dead versions reusable and helps maintain visibility information and prevent transaction ID wraparound. Plain vacuum usually reuses space inside the table rather than returning all of it to the operating system.

**ANALYZE** samples data to update planner statistics. Postgres uses those estimates to choose scan and join strategies. Autovacuum automates vacuum and analyse work; monitor whether it keeps up rather than treating it as optional background noise.



## Inspect why cleanup is delayed

In our disposable database you can run:

```sql
-- Run outside an explicit transaction.
VACUUM (ANALYZE) bookings;
```

Run this outside a transaction block. A session left “idle in transaction” can retain locks and, when holding an old snapshot, prevent cleanup. If a busy table grows unexpectedly, inspect old transactions, dead tuples and autovacuum activity. Disabling autovacuum or routinely running `VACUUM FULL` is not a general fix: the latter copies the table into a new file and requires a strong lock.

An update can sometimes use a heap-only tuple (HOT), avoiding new ordinary index entries when no non-summarising indexed column changes and the original heap page has room. This reduces index maintenance; it does not remove the need for vacuum. In PostgreSQL 16–18, summarising indexes such as BRIN do not by themselves disqualify HOT. Do not assume every update is eligible.

## Key takeaways

- Old snapshots can delay reclamation.
- Plain VACUUM normally makes space reusable inside the table.
- VACUUM FULL rewrites and strongly locks the table.

## Further reading

- [PostgreSQL 18: routine vacuuming](https://www.postgresql.org/docs/18/routine-vacuuming.html)
- [PostgreSQL 18: sql vacuum](https://www.postgresql.org/docs/18/sql-vacuum.html)
- [PostgreSQL 18: storage hot](https://www.postgresql.org/docs/18/storage-hot.html)
- [PostgreSQL 18: sql analyze](https://www.postgresql.org/docs/18/sql-analyze.html)
