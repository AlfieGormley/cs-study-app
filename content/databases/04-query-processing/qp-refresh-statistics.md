---
id: qp-refresh-statistics
title: Stale statistics after a load
level: intermediate
minutes: 3
sourceLesson: qp-statistics-optimiser
summary: Stale statistics after a load with worked examples and explicit assumptions.
---

These examples use PostgreSQL 18. SQL Fundamentals supplies the shop relations: `customers(id, name, email, city, country)`, `orders(id, customer_id, status, ordered_on, total)`, `products(id, price)` and `order_items(order_id)`. IDs join orders to customers and items to orders. Dates use `date`, IDs use `integer`, and totals use `numeric`. Each query fragment uses these names; ellipses and standalone WHERE clauses need the surrounding SELECT shown by their context.

All historical plan fragments and timings in this unit are **illustrative inputs**, not reproduced benchmarks or promises. Their row/page counts describe a hypothetical dataset; actual plans vary with statistics, indexes, settings, cache state and PostgreSQL version. Assume serial execution unless a parallel worker process is shown.

## Stale statistics

Statistics describe the table as it was at the last ANALYZE. Autovacuum re-analyses a table once enough rows have changed since the last ANALYZE:

```formula
n_trig = n_base + k_scale × n_table
n_trig = 50 + 0.1 × 1,000
n_trig = 150
where
n_trig: the number of inserted, updated or deleted rows since the last ANALYZE that defines the analysis threshold; exceeding it makes the table eligible, rather than guaranteeing immediate analysis
n_base: `autovacuum_analyze_threshold`, a fixed number of rows, default 50
k_scale: `autovacuum_analyze_scale_factor`, the fraction of the table, default 0.1 (10%)
n_table: the table's estimated row count (`pg_class.reltuples`, updated by VACUUM and ANALYZE), here 1,000
In words: a table is re-analysed after about a tenth of it has changed, plus 50 rows.
```

For the 1,000-row table below, more than 150 changes cross the threshold, and a 500,000-row load passes that easily. But autovacuum only checks tables periodically (every minute by default, set by `autovacuum_naptime`), so a query run straight after the load still sees the old statistics. On a 100-million-row table, more than 10,000,050 changes cross the default threshold. In between, the planner can be badly wrong:

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

The planner did notice that the table had grown, because it scales `reltuples` by the current number of pages. But the MCV list said every row is 'a', so 'b' looked almost non-existent. Feed that "1 row" into a join and you get a nested loop running hundreds of thousands of loops, like the 600,000-loop example in the next lesson.

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

