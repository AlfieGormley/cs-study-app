---
id: pg-autovacuum-thresholds
title: Understand autovacuum thresholds
level: intermediate
minutes: 4
sourceLesson: postgresql-in-practice
summary: The dead-tuple threshold scales with estimated table size.
---

This unit uses PostgreSQL 18 defaults. PostgreSQL 16 and 17 have no `autovacuum_vacuum_max_threshold` cap. These are eligibility thresholds, not promises that a worker starts immediately.

## Size-dependent cleanup

Autovacuum does not clean a table after every update. It waits until enough dead row versions have built up to make the work worthwhile, and the point at which it acts grows with the table. In PostgreSQL 18 the rule is below; the cap, `autovacuum_vacuum_max_threshold`, is new in version 18.

```formula
T_vac = min(T_max, T_base + sN)
T_vac = min(10^8, 50 + 0.2 × 10^6)
T_vac = min(10^8, 200050)
T_vac = 200050 tuples
where
T_vac: the vacuum threshold: autovacuum vacuums the table when the estimated dead-tuple count exceeds this; worker availability and other triggers also matter
min: the minimum function: whichever of its two inputs is smaller
T_max: autovacuum_vacuum_max_threshold, a cap that stops the threshold growing without limit on huge tables; default 100,000,000 (10^8) tuples
T_base: autovacuum_vacuum_threshold, the fixed dead-version base added to the size-dependent component before applying the configured cap; default 50 tuples
s: autovacuum_vacuum_scale_factor, the fraction of the estimated table row count added to the dead-version base threshold; default 0.2 (20 %), no unit
N: the estimated number of rows in the table, kept in pg_class.reltuples and refreshed by VACUUM and ANALYZE; here 1,000,000 (10^6)
tuples: the unit counted here: row versions, which PostgreSQL calls tuples
In words: with these PostgreSQL 18 defaults, the dead-tuple eligibility threshold is fifty plus a fifth of the estimated row count, capped at one hundred million.
```

So a 1,000,000-row table passes this dead-tuple threshold when its estimated dead-version count exceeds 200,050. Repeated updates to the same logical row can leave several obsolete versions. This is not a count of distinct rows, and an eligible table may wait for a worker. For anything above a few hundred rows the 20 % term dominates; the fixed 50 only matters for tiny tables. The cap only matters for very large tables: a 1,000,000,000-row table would otherwise wait for about 200 million dead versions, but with the cap the threshold is capped at 100 million dead versions.

The threshold is checked, not a start-time guarantee: `autovacuum_naptime` defaults to one minute between autovacuum runs on a database. Worker availability and a running worker's progress also matter. Similar rules start a vacuum after many inserts (`autovacuum_vacuum_insert_threshold`, 1,000 rows by default, plus 20 % of the table's not-yet-frozen part) and start ANALYZE (50 rows plus 10 % of the estimated table size by default, counting inserts, updates and deletes). A large, busy table often needs a smaller vacuum scale factor of its own, set per table as a storage parameter, for example `ALTER TABLE bookings SET (autovacuum_vacuum_scale_factor = 0.01)`.

## Key takeaways

- The dead-tuple threshold scales with estimated table size.
- PostgreSQL 18 adds a configurable maximum threshold.
- Worker availability and checks determine when eligible work runs.

## Further reading

- [PostgreSQL 18: routine vacuuming](https://www.postgresql.org/docs/18/routine-vacuuming.html)
- [PostgreSQL 18: runtime config vacuum](https://www.postgresql.org/docs/18/runtime-config-vacuum.html)
- [PostgreSQL 18: sql createtable](https://www.postgresql.org/docs/18/sql-createtable.html)
