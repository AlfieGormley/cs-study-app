---
id: pg-troubleshooting-query-memory
title: Trace latency and budget query memory
level: intermediate
minutes: 4
sourceLesson: postgresql-in-practice
summary: Separate connection waits, lock waits and execution time.
---

The settings and defaults here are for PostgreSQL 18 with standard build options; inspect the running server before relying on them.

When a request is slow, first separate time waiting for a connection, waiting for a lock, executing SQL and transferring results. `pg_stat_activity` exposes current sessions and waits; `pg_locks` helps investigate blocking. The optional `pg_stat_statements` extension summarises query behaviour over time when configured.

Next, reproduce the query with representative parameters, examine its plan and check statistics. Then consider query shape, indexes, transaction duration and pool size. Avoid tuning memory or connection limits blindly: a per-operation memory allowance can multiply across operations and concurrent sessions.

The main setting behind that warning is `work_mem`: the base memory allowance for an individual sort operation before spilling to temporary files; hash operations have a multiplied allowance. It is a per-operation limit, not a per-server one, so a base sort-memory budget multiplies out:

```formula
M_sort ≈ wkc
M_sort ≈ 4 MB × 3 × 100
M_sort ≈ 1200 MB
where
M_sort: an illustrative total sort-memory allowance, in megabytes (MB); not an upper bound on server or mixed sort/hash memory
≈: approximately equal to; this budget assumes every listed sort uses its full allowance
w: work_mem, the base allowance for one sort, in MB; PostgreSQL 18 default 4 MB. Hash operations instead use work_mem times hash_mem_multiplier, whose default is 2.0
k: the number of simultaneously active sort operations in each query, no unit; here 3
c: the number of sessions running such queries concurrently, no unit; here 100
MB: megabytes; PostgreSQL memory settings count 1 MB as 1024 kilobytes (kB)
In words: three simultaneous sorts in each of one hundred busy sessions can collectively use about twelve hundred megabytes at a four-megabyte allowance per sort.
```

This example excludes hash operations, parallel workers and other query memory. A hash operation may use `work_mem` times `hash_mem_multiplier`; parallel workers can each receive their own allowances. This is a capacity-planning illustration, not a guaranteed maximum.

Raising `work_mem` to 64 MB "to speed up sorts" turns the same workload into about 19,200 MB, nearly 19 GB (18.75 GB counting 1024 MB per GB). That comes on top of `shared_buffers` (PostgreSQL's own shared buffers, typically 128 MB by default) and each backend process's own baseline memory. Raise it for one session or role running a known heavy report, or limit concurrency with a connection pool, rather than raising it globally and hoping.

For a slow event booking, a lock wait on one popular event may dominate even when the primary-key lookup is fast. Another index cannot remove the need for competing reservations to coordinate over the same remaining seat count.

## Key takeaways

- Separate connection waits, lock waits and execution time.
- work_mem is per operation, with extra hash and parallel-worker allowances.
- A fast index cannot remove contention on the same seat count.

## Further reading

- [PostgreSQL 18: monitoring stats](https://www.postgresql.org/docs/18/monitoring-stats.html)
- [PostgreSQL 18: view pg locks](https://www.postgresql.org/docs/18/view-pg-locks.html)
- [PostgreSQL 18: pgstatstatements](https://www.postgresql.org/docs/18/pgstatstatements.html)
- [PostgreSQL 18: runtime config resource](https://www.postgresql.org/docs/18/runtime-config-resource.html)
