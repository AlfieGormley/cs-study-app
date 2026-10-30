---
id: pg-troubleshooting-query-memory
title: Trace latency and budget query memory
level: intermediate
minutes: 5
sourceLesson: postgresql-in-practice
summary: Find where a slow request spends its time, and remember that work_mem is granted per operation, not per server.
---

The settings and defaults here are for PostgreSQL 18 with standard build options; inspect the running server before relying on them.

## Find where the time goes

When a request is slow, first separate time waiting for a connection, waiting for a lock, executing SQL and transferring results. Each has a different fix, and tuning the wrong one changes nothing.

- `pg_stat_activity` shows each session's state and what it is waiting for. A session with `wait_event_type` `Lock` is blocked by another, and `pg_blocking_pids(pid)` names the sessions in its way.
- `pg_locks` lists the locks held and requested, for deeper investigation of blocking.
- The optional `pg_stat_statements` extension summarises query behaviour over time when configured.

For a slow event booking, a lock wait on one popular event may dominate even when the primary-key lookup is fast. In a test, a second booking for the same event showed `wait_event_type` `Lock` and named the first booking's session as its blocker for as long as that transaction stayed open. Another index cannot remove the need for competing reservations to coordinate over the same remaining seat count; shorter transactions can.

If the time really is in execution, reproduce the query with representative parameters, examine its plan and check statistics. Then consider query shape, indexes, transaction duration and pool size.

## Budget query memory

Avoid tuning memory or connection limits blindly. The setting that most affects query memory is `work_mem`: the base allowance for one sort or hash operation before it spills to temporary files on disk. Its default is 4 MB. Hash operations may use `work_mem` times `hash_mem_multiplier`, which defaults to 2.0.

The allowance is per operation, not per query or per server. One query can run several sorts and hashes at once, many sessions can run such queries together, and each parallel worker gets its own allowance:

```formula reference
M_sort ≈ wkc
where
M_sort: an illustrative total sort-memory allowance, in megabytes (MB); not an upper bound on server memory
≈: approximately equal to; this budget assumes every listed sort uses its full allowance
w: work_mem, the base allowance for one sort, in MB; PostgreSQL 18 default 4 MB
k: the number of sort operations active at once in each query, no unit
c: the number of sessions running such queries concurrently, no unit
MB: megabytes; PostgreSQL memory settings count 1 MB as 1024 kilobytes (kB)
In words: the worst-case sort memory is roughly the per-sort allowance multiplied by the number of sorts in each query and by the number of sessions running them at once, before adding hash, parallel-worker and other memory.
```

The allowance is an upper limit, not memory reserved in advance; small sorts use little. But it multiplies. At the default, 100 sessions each running three sorts could use about 1.2 GB for sorting alone. Raise `work_mem` to 64 MB globally "to speed up sorts" and the same workload could reach about 19 GB, on top of `shared_buffers` (typically 128 MB by default) and each backend's own baseline memory. That is how a global memory change turns a busy period into an out-of-memory crash.

You can see a spill in `EXPLAIN ANALYZE`. In a PostgreSQL 18 test, sorting 400,000 short strings at 4 MB reported `Sort Method: external merge  Disk: 9976kB`; with `work_mem` raised to 64 MB for that transaction only, it reported `quicksort  Memory: 24788kB`. A hash aggregate on the same rows used about 8 MB of memory before spilling, twice `work_mem`, as `hash_mem_multiplier` allows.

Raise the allowance where you know it helps: for one transaction with `SET LOCAL work_mem`, or for the role running a known heavy report. Limit concurrency with a connection pool rather than raising the setting globally and hoping.

> [!analogy] Real-world analogy: workbench space in a busy kitchen
> Every cook doing a big chopping job may spread out over up to one workbench; anything that does not fit goes on trolleys in the corridor, which is slower. A head chef who decides "everyone may now use four benches" has not checked how many cooks are on shift, or that each might be doing three jobs at once.
>
> **How it maps:** one job's bench limit is `work_mem` for one sort; trolleys in the corridor are temporary files after a spill. Cooks on shift are concurrent sessions, and three jobs at once are several sorts in one plan.
>
> **Where it stops:** a crowded kitchen just slows down. A server that runs out of memory can have Postgres processes killed by the operating system, which can disrupt every session, not only the greedy job; and unlike a bench, unused allowance is never set aside in advance.

## Key takeaways

- Separate connection waits, lock waits and execution time before tuning.
- `pg_blocking_pids` shows who blocks a waiting session; an index cannot fix contention on one row.
- work_mem is per operation, with larger hash allowances and extra allowances per parallel worker.
- Raise work_mem for a session or role, not globally on a busy server.

## Further reading

- [PostgreSQL 18: monitoring statistics](https://www.postgresql.org/docs/18/monitoring-stats.html)
- [PostgreSQL 18: pg_locks](https://www.postgresql.org/docs/18/view-pg-locks.html)
- [PostgreSQL 18: pg_stat_statements](https://www.postgresql.org/docs/18/pgstatstatements.html)
- [PostgreSQL 18: resource consumption settings](https://www.postgresql.org/docs/18/runtime-config-resource.html)
- [PostgreSQL 18: system information functions](https://www.postgresql.org/docs/18/functions-info.html)
