---
id: pg-autovacuum-thresholds
title: Understand autovacuum thresholds
level: intermediate
minutes: 4
sourceLesson: postgresql-in-practice
summary: Autovacuum waits for dead versions in proportion to table size, so big busy tables often need their own settings.
---

This unit uses PostgreSQL 18 defaults. PostgreSQL 16 and 17 have no `autovacuum_vacuum_max_threshold` cap. These are eligibility thresholds, not promises that a worker starts immediately.

## Size-dependent cleanup

Autovacuum does not clean a table after every update. It waits until enough dead row versions have built up to make the work worthwhile, and that point grows with the table. The relationship is worth seeing because it explains why large tables are cleaned so rarely:

```formula essential
T_vac = min(T_max, T_base + sN)
where
T_vac: the vacuum threshold, in row versions (tuples): autovacuum vacuums the table once its estimated count of dead versions exceeds this
min: the minimum function: whichever of its two inputs is smaller
T_max: autovacuum_vacuum_max_threshold, a cap added in PostgreSQL 18 so the threshold cannot grow without limit on huge tables; default 100,000,000 tuples
T_base: autovacuum_vacuum_threshold, a fixed base that matters only for tiny tables; default 50 tuples
s: autovacuum_vacuum_scale_factor, the fraction of the table's estimated row count added to the base; default 0.2 (20 %), no unit
N: the estimated number of rows in the table, kept in pg_class.reltuples and refreshed by VACUUM and ANALYZE
In words: by default a table becomes eligible once its dead versions exceed fifty plus a fifth of its rows, capped at one hundred million.
```

So the dead-version allowance scales with size. A 1,000-row table becomes eligible after about 250 dead versions; a 1,000,000-row table only after about 200,000; a 50-million-row table after about 10 million. The cap matters only beyond about 500 million rows. The count is of row versions, not distinct rows: updating the same row five times leaves five obsolete versions.

That proportion is why a large, busy table can bloat even though autovacuum is "working": millions of dead versions accumulate between runs, and the size the table settles at includes them. The usual fix is a smaller vacuum scale factor for that table alone, set as a storage parameter:

```sql
-- Vacuum after ~1% of rows are dead.
ALTER TABLE bookings
SET (autovacuum_vacuum_scale_factor = 0.01);
```

## Eligible is not the same as started

The autovacuum launcher tries to start a worker in each database about once every `autovacuum_naptime`, one minute by default. At most `autovacuum_max_workers` (3 by default) run at once. If several large tables become eligible together, all workers can be busy for a long time and other eligible tables wait. Workers also pause briefly as they go (cost-based delay, 2 ms by default) to limit their I/O impact, so a single large vacuum can take a while.

Two similar rules start other work:

- Many inserts start a vacuum: by default once more than 1,000 rows plus 20 % of the rows in the part of the table not yet frozen have been inserted since the last vacuum. These vacuums let insert-only tables have pages marked all-visible and rows frozen before the work piles up.
- Enough changes start an ANALYZE: by default 50 rows plus 10 % of the table, counting inserts, updates and deletes.

> [!analogy] Real-world analogy: a cleaner who visits by the size of the room
> An office cleaner comes to each room once a fifth of its desks have been left messy. A five-desk meeting room is cleaned after one messy desk; a 1,000-desk open-plan floor waits for 200. The cleaning company also has only three cleaners, who do a round of the building roughly once a minute.
>
> **How it maps:** the fraction of messy desks is the vacuum scale factor and the room size is the table's row count. Three cleaners are the default worker limit, and the round is the naptime. Telling the company to clean the big floor after ten messy desks is a per-table vacuum scale factor.
>
> **Where it stops:** a cleaner sees mess directly. Autovacuum works from estimated counts in the statistics system, a fixed base of 50 means tiny tables wait for more than the fraction alone suggests, and dead versions held back by an old snapshot stay uncleaned however often a worker visits.

## Key takeaways

- The dead-version threshold is a fixed base plus a fraction of the table, capped in PostgreSQL 18.
- Large tables accumulate many dead versions between runs; lower their vacuum scale factor per table.
- Eligibility does not guarantee an immediate start: naptime, worker limits and throttling matter.
- Separate thresholds cover insert-only tables and ANALYZE.

## Further reading

- [PostgreSQL 18: routine vacuuming](https://www.postgresql.org/docs/18/routine-vacuuming.html)
- [PostgreSQL 18: autovacuum settings](https://www.postgresql.org/docs/18/runtime-config-autovacuum.html)
- [PostgreSQL 18: vacuuming settings](https://www.postgresql.org/docs/18/runtime-config-vacuum.html)
- [PostgreSQL 18: CREATE TABLE storage parameters](https://www.postgresql.org/docs/18/sql-createtable.html)
