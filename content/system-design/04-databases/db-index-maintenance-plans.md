---
id: db-index-maintenance-plans
title: Index maintenance and planner choices
level: intermediate
minutes: 3
summary: Diagnose write overhead, HOT eligibility and sequential scans before adding or removing an index.
sourceLesson: db-indexing
---

An index earns its place only when the work it saves is worth its maintenance. Diagnose the actual write cost and chosen read plan before adding another structure or removing an existing one.

## The cost of indexes on writes

Each index adds maintenance for writes affecting its entries; partial indexes and HOT updates are important exceptions.

- An `INSERT` into a Postgres heap table with 6 B-tree indexes inserts one heap tuple and 6 index entries; InnoDB uses a clustered B-tree for the table itself. Each structure adds buffer, I/O and WAL work.
- An `UPDATE` touching an indexed column updates that index too. In Postgres, updating *any* column covered by a B-tree (or other non-summarising) index prevents a **HOT update** (heap-only tuple update), so ordinary indexes need entries for the new tuple version; summarizing indexes such as BRIN have different maintenance. A HOT update also needs free space on the same page, which is why hot tables often use a `fillfactor` below 100.
- Indexes consume memory. If they don't fit in the buffer cache, lookups and inserts start hitting disk.
- More indexes give the planner more choices, which occasionally means a bad choice.

> [!warning] Audit unused indexes
> In Postgres, `pg_stat_user_indexes.idx_scan = 0` means no scans were recorded in the observed statistics window; it does not mean the index has no purpose. Before dropping one, check statistics resets, replicas, rare jobs and especially uniqueness, primary-key or exclusion constraints. Constraint enforcement is a reason to keep an index even without query scans.

## Why an index might not be used

- The query wraps the column in a function: `WHERE date(created_at) = ...` can't use an index on `created_at`. Rewrite as a range.
- Low selectivity: if 40% of a 100-million-row table matches, a sequential scan of its million pages is cheaper than 40 million index lookups that jump around the heap. The crossover is often at a few percent of rows, and depends on how well the table's physical order matches the index.
- Type mismatch: PostgreSQL can reject a text-to-integer comparison unless you cast explicitly. Casting the indexed column may prevent an ordinary index seek; converting the parameter to the column type can preserve it.
- Leading wildcard: `LIKE '%smith'` can't use a B-tree (use a trigram GIN index).
- Stale statistics: run `ANALYZE` so the planner knows the data distribution.

## Key takeaways
- Indexes add storage and write work; PostgreSQL HOT updates can avoid ordinary index maintenance.
- Zero recorded scans alone do not establish that an index is safe to remove.
- Functions, low selectivity and stale statistics can make a raw-column index unsuitable.

## Further reading
- [PostgreSQL: Heap-only tuples (HOT)](https://www.postgresql.org/docs/current/storage-hot.html)
- [PostgreSQL: Using EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html)
- [www.postgresql.org: monitoring stats](https://www.postgresql.org/docs/current/monitoring-stats.html)
