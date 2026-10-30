---
id: qp-explain-fields
title: EXPLAIN estimates and execution fields
level: intermediate
minutes: 4
sourceLesson: qp-reading-explain
summary: The EXPLAIN variants, what each number on a plan node means, and why EXPLAIN ANALYZE really runs the statement.
---

Examples use PostgreSQL 18 and the module's scaled-up shop tables (1,000,000 orders, 100,000 customers; the first lesson lists them). Plans are abbreviated and illustrative: real plans and timings depend on the data, statistics, settings, cache state and version. Assume serial execution.

`EXPLAIN` is the single most useful tool for understanding a slow query. It shows the plan the optimiser chose, with its estimates. `EXPLAIN ANALYZE` also runs the query and shows what actually happened. The skill is reading the output quickly and knowing which numbers matter.

## The variants

```sql
-- plan and estimates only; doesn't run
EXPLAIN SELECT ...;

-- runs it, adds actual rows, time, buffers
EXPLAIN ANALYZE SELECT ...;

-- the options worth knowing
EXPLAIN (ANALYZE, BUFFERS, VERBOSE,
         SETTINGS, FORMAT JSON) SELECT ...;
```

- **ANALYZE** executes the statement and reports actual figures.
- **BUFFERS** reports pages touched. Since Postgres 18 it's included automatically with ANALYZE; on older versions, ask for it.
- **VERBOSE** adds output column lists and schema-qualified names.
- **SETTINGS** lists any planner settings that differ from the defaults. Very useful when someone sends you a plan.
- **FORMAT JSON** gives machine-readable output for visualisers.
- **TIMING OFF** keeps row counts but skips per-node timing, which can have noticeable overhead on some systems.

> [!warning] EXPLAIN ANALYZE really runs the statement
> `EXPLAIN ANALYZE DELETE FROM orders` deletes the orders. Wrap data-changing statements in a transaction you roll back:
> `BEGIN; EXPLAIN ANALYZE DELETE ...; ROLLBACK;`
> Rollback does not undo sequence increments or external side effects from functions or triggers. Use disposable data when those effects are possible.

## Anatomy of one node

```sql
EXPLAIN ANALYZE
SELECT * FROM orders
WHERE status = 'pending';
```

```
Seq Scan on orders
  (cost=0.00..19853.00 rows=30767 width=26)
  (actual time=0.025..26.566
   rows=30066.00 loops=1)
  Filter: (status = 'pending'::text)
  Rows Removed by Filter: 969934
  Buffers: shared hit=7011 read=342
Planning Time: 0.133 ms
Execution Time: 27.149 ms
```

| Field | Meaning |
|---|---|
| `cost=0.00..19853.00` | Estimated startup..total cost, in planner units |
| `rows=30767` | Estimated rows output |
| `width=26` | Estimated average row size in bytes |
| `actual time=0.025..26.566` | Real ms to first row..last row |
| `rows=30066.00` | Real rows output, per loop |
| `loops=1` | Times this node was executed |
| `Rows Removed by Filter` | Rows read but rejected |
| `Buffers: shared hit` | Pages found in Postgres's cache |
| `Buffers: shared read` | Pages fetched from the OS or disk |

From this one node: the estimate (30,767) was within about 2.3% of the truth (30,066), the scan read every one of the 7,353 pages (7,011 + 342), and it threw away 97% of the rows it read. The last fact is the important one. Reading a million rows to keep 30,000 is a sign that an index might help (see the index-tuning units).

The `.00` on actual rows is new in Postgres 18. It's there because `rows` is an **average per loop**, and averages needn't be whole numbers, as you'll see below.

## Key takeaways
- Plain EXPLAIN shows estimates; ANALYZE executes the statement, including mutations.
- PostgreSQL 18 includes BUFFERS with ANALYZE and displays fractional average actual rows and index search counts.

## Further reading
- [Using EXPLAIN — PostgreSQL docs](https://www.postgresql.org/docs/18/using-explain.html)
- [EXPLAIN command reference — PostgreSQL docs](https://www.postgresql.org/docs/18/sql-explain.html)
- [auto_explain — PostgreSQL docs](https://www.postgresql.org/docs/18/auto-explain.html)
- [pg_stat_statements — PostgreSQL docs](https://www.postgresql.org/docs/18/pgstatstatements.html)
- [PostgreSQL 18 release notes](https://www.postgresql.org/docs/18/release-18.html)
- [EXPLAIN QUERY PLAN — SQLite docs](https://www.sqlite.org/eqp.html)

