---
id: qp-refresh-statistics
title: Stale statistics after a load
level: intermediate
minutes: 3
sourceLesson: qp-statistics-optimiser
summary: Why statistics lag behind a bulk load, when autovacuum refreshes them, and why you should run ANALYZE yourself after loading data.
---

Examples use PostgreSQL 18 and the module's scaled-up shop tables (1,000,000 orders, 100,000 customers; the first lesson lists them). Plans are abbreviated and illustrative: real plans and timings depend on the data, statistics, settings, cache state and version. Assume serial execution.

## Stale statistics

Statistics describe the table as it was at the last ANALYZE. Autovacuum re-analyses a table once enough rows have changed since the last ANALYZE:

```formula reference
n_trig = n_base + k_scale × n_table
where
n_trig: the number of inserted, updated or deleted rows since the last ANALYZE that defines the analysis threshold; exceeding it makes the table eligible, rather than guaranteeing immediate analysis
n_base: `autovacuum_analyze_threshold`, a fixed number of rows, default 50
k_scale: `autovacuum_analyze_scale_factor`, the fraction of the table, default 0.1 (10%)
n_table: the table's estimated row count (`pg_class.reltuples`, updated by VACUUM and ANALYZE)
In words: by default a table becomes due for re-analysis once about a tenth of it, plus 50 rows, has changed since the last ANALYZE. For a 1,000-row table that is just over 150 changes; for a 100-million-row table it is over 10 million.
```

A 500,000-row load into a 1,000-row table passes that threshold easily. But autovacuum only checks tables periodically (every minute by default, set by `autovacuum_naptime`), so a query run straight after the load still sees the old statistics. In between, the planner can be badly wrong:

```sql
-- events: 1,000 rows of kind 'a',
-- analysed. Now load 500,000 of 'b':
EXPLAIN SELECT * FROM events
WHERE kind = 'b';
```

```
Seq Scan on events  (rows=1)
-- after ANALYZE:
Seq Scan on events  (rows=499881)
```

The planner did notice that the table had grown, because it scales `reltuples` by the current number of pages. But the MCV list said every row is 'a', so 'b' looked almost non-existent. Feed that "1 row" into a join and you get a nested loop running hundreds of thousands of loops, like the 600,000-loop example in the EXPLAIN lessons.

> [!analogy] Real-world analogy: a sat-nav with an old map
> A sat-nav plans the fastest route from its stored map. If a new bypass opened last month and the map has not been updated, it confidently sends you through the town centre, and the route it picks is only as good as the map.
>
> **How it maps:** the stored map is the statistics from the last ANALYZE, and the route is the plan. The new bypass is the bulk load: the data changed, but the planner still reasons from the old picture. Running ANALYZE is updating the map before you set off.
>
> **Where it stops:** a sat-nav may get live traffic updates during the trip, but a PostgreSQL plan does not change mid-query when actual row counts turn out different; only later queries planned after ANALYZE benefit.

Practical rules:

- Run `ANALYZE` after bulk loads, before querying the new data.
- **Temporary tables are never analysed by autovacuum.** Analyse them yourself.
- For skewed columns, raise the per-column target: `ALTER TABLE orders ALTER COLUMN customer_id SET STATISTICS 1000;`
- Add extended statistics for correlated columns used together.

## Key takeaways
- ANALYZE after a bulk load avoids relying on old column distributions.
- Temporary tables need manual ANALYZE; autovacuum thresholds make a table eligible rather than scheduling immediate analysis.

## Further reading
- [Statistics used by the planner — PostgreSQL docs](https://www.postgresql.org/docs/18/planner-stats.html)
- [Row estimation examples — PostgreSQL docs](https://www.postgresql.org/docs/18/row-estimation-examples.html)
- [Multivariate statistics examples — PostgreSQL docs](https://www.postgresql.org/docs/18/multivariate-statistics-examples.html)
- [Access path selection in a relational DBMS (Selinger et al., 1979)](https://courses.cs.duke.edu/compsci516/cps216/spring03/papers/selinger-etal-1979.pdf)
- [How Good Are Query Optimizers, Really? (Leis et al., VLDB 2015)](https://www.vldb.org/pvldb/vol9/p204-leis.pdf)
- [Genetic query optimiser — PostgreSQL docs](https://www.postgresql.org/docs/18/geqo.html)

