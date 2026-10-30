---
id: qp-index-maintenance
title: Index maintenance and tuning a workload
level: advanced
minutes: 3
sourceLesson: qp-index-tuning
summary: What every extra index costs in writes, memory and vacuum work, how to find unused or redundant indexes, and a safe tuning workflow.
---

Examples use PostgreSQL 18 and the module's scaled-up shop tables (1,000,000 orders, 100,000 customers; the first lesson lists them). Plans are abbreviated and illustrative: real plans and timings depend on the data, statistics, settings, cache state and version. Assume serial execution.

## What every index costs

| Index | Size |
|---|---|
| orders (the table) | 59 MB |
| orders_cust_cov_idx | 30 MB |
| orders_pkey | 21 MB |
| orders_cust_date_idx | 21 MB |
| orders_date_idx | 6.9 MB |
| orders_pending_idx | 272 kB |

The illustrative date index is smaller in part because of **B-tree deduplication** (Postgres 13+), which stores a repeated key once with a list of row pointers: 1,000,000 rows share only 2,400 distinct dates.

Costs to weigh:

- **Writes.** An INSERT maintains applicable indexes; a partial index excludes rows outside its predicate. Changing a column used by a non-summarising index, including an `INCLUDE` column, prevents a **HOT** (heap-only tuple) update. BRIN is a summarising-index exception; HOT also requires room on the original heap page.
- **Memory.** Indexes compete with table data for the buffer cache.
- **Vacuum.** Vacuum may need index cleanup for dead tuples; its actual work depends on dead-index entries and cleanup settings, and unnecessary scans can be skipped.
- **Planning.** More indexes give more paths to consider, and more chances of a surprising choice.

Find indexes that are never used:

```sql
-- Zero scans is a lead, not drop approval.
SELECT indexrelname, idx_scan,
  pg_size_pretty(
    pg_relation_size(indexrelid))
FROM pg_stat_user_indexes
WHERE idx_scan = 0;
```

Check over weeks of traffic, and on replicas, before dropping anything. Also look for **redundant** indexes: an index on `(customer_id)` is usually redundant next to one on `(customer_id, ordered_on)`, which serves the same lookups.

## A tuning workflow

1. Find the queries that matter with `pg_stat_statements`, ordered by `total_exec_time` (the execution durations of every call added together, so a fast query called a million times can outrank a slow one called once), not just the slowest single run.
2. Get `EXPLAIN (ANALYZE, BUFFERS)` on production-sized data.
3. Design an index for the query: equality columns, then sort, then range; add `INCLUDE` columns only if an index-only scan is worth the size.
4. To permit ordinary writes during the build, use `CREATE INDEX CONCURRENTLY`. It takes additional work, can wait for transactions, and cannot run in a transaction block. A failure can leave an INVALID index that still adds maintenance overhead; inspect and clean up or rebuild it.
5. Re-run EXPLAIN and compare buffers and time. Watch write latency afterwards.

## Key takeaways
- INCLUDE columns consume space and can prevent HOT updates when they change.
- Review usage over a representative window, replicas and constraints before treating an index as redundant.

## Further reading
- [Multicolumn indexes — PostgreSQL docs](https://www.postgresql.org/docs/18/indexes-multicolumn.html)
- [Index-only scans and covering indexes — PostgreSQL docs](https://www.postgresql.org/docs/18/indexes-index-only-scans.html)
- [Partial indexes — PostgreSQL docs](https://www.postgresql.org/docs/18/indexes-partial.html)
- [Combining multiple indexes — PostgreSQL docs](https://www.postgresql.org/docs/18/indexes-bitmap-scans.html)
- [Operator classes — PostgreSQL docs](https://www.postgresql.org/docs/18/indexes-opclass.html)
- [Use The Index, Luke: SQL indexing for developers](https://use-the-index-luke.com/)
- [Heap-only tuples (HOT) — PostgreSQL docs](https://www.postgresql.org/docs/18/storage-hot.html)

