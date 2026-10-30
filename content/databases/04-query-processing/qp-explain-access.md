---
id: qp-explain-access
title: Spills and index access conditions
level: intermediate
minutes: 3
sourceLesson: qp-reading-explain
summary: Red flags in a plan, such as spilling sorts and filters that should be index conditions, and PostgreSQL 18's Index Searches count.
---

Examples use PostgreSQL 18 and the module's scaled-up shop tables (1,000,000 orders, 100,000 customers; the first lesson lists them). Plans are abbreviated and illustrative: real plans and timings depend on the data, statistics, settings, cache state and version. Assume serial execution.

## Red flags and what they indicate

| You see | It suggests |
|---|---|
| Estimate off by 10x+ | Stale stats, correlated columns, or a function on a column |
| Large `Rows Removed by Filter` | A missing or unusable index |
| `Sort Method: external merge  Disk:` | Sort spilled; `work_mem` too small, or an index could supply the order |
| `Batches:` greater than 1 | Hash spilled to temp files |
| High `loops` on an expensive inner node | Nested loop over too many outer rows |
| `Heap Fetches` high on an Index Only Scan | Pages are not all-visible; investigate updates, snapshots and vacuum |
| `Heap Blocks: lossy` | Bitmap too big for `work_mem`; rows rechecked per page |
| `Buffers: ... read` dominates | Absent from shared buffers; the OS cache may still serve reads |

### Sorts that spill

```sql
EXPLAIN ANALYZE
SELECT * FROM orders ORDER BY total;
```

```
Sort  (actual time=238.774..288.495
       rows=1000000.00 loops=1)
  Sort Key: total
  Sort Method: external merge
    Disk: 36344kB
  Buffers: temp read=9084 written=9101
```

With the default 4 MB `work_mem`, sorting a million rows wrote 36 MB to temporary files. Interestingly, `work_mem = 64MB` *still* spilled: the in-memory quicksort needed 71 MB (`Memory: 71451kB` at 256 MB), because in-memory sorting carries per-row overhead the compact on-disk format doesn't. With an `ORDER BY ... LIMIT 10` instead, the plan uses `top-N heapsort  Memory: 26kB` and never spills.

### Index Cond versus Filter

```
Index Scan using customers_email_pattern_idx
  Index Cond: ((email ~>=~ 'c42@'::text)
    AND (email ~<~ 'c42A'::text))
  Filter: (email ~~ 'c42@%'::text)
```

**Index Cond** is evaluated by the index access method. Leading-key bounds usually narrow a B-tree search; some later-key conditions filter index entries without reducing the contiguous range scanned. **Filter** is checked on each row after it's fetched. A condition appearing only under Filter does not supply an index access condition in that node. Here the `LIKE 'c42@%'` prefix was converted into a range for the index, then rechecked as a filter.

### New in Postgres 18: Index Searches

```
Index Scan Backward
  using orders_date_cust_idx
  Index Cond: (customer_id = 42)
  Index Searches: 1031
```

`Index Searches` counts how many separate descents into the index happened. Normally it's 1 per loop. Here, an index on `(ordered_on, customer_id)` was used for a query on `customer_id` alone, and Postgres 18's **skip scan** made 1,031 descents, across the date groups it checked. The composite-index unit explains how a leading customer key can need one search.

## Key takeaways
- Spills, high loops and heap fetches are evidence to investigate, rather than proof of one fix.
- Index Cond is handled by the index method; a separate Filter is evaluated after that access.

## Further reading
- [Using EXPLAIN — PostgreSQL docs](https://www.postgresql.org/docs/18/using-explain.html)
- [EXPLAIN command reference — PostgreSQL docs](https://www.postgresql.org/docs/18/sql-explain.html)
- [auto_explain — PostgreSQL docs](https://www.postgresql.org/docs/18/auto-explain.html)
- [pg_stat_statements — PostgreSQL docs](https://www.postgresql.org/docs/18/pgstatstatements.html)
- [PostgreSQL 18 release notes](https://www.postgresql.org/docs/18/release-18.html)
- [EXPLAIN QUERY PLAN — SQLite docs](https://www.sqlite.org/eqp.html)

