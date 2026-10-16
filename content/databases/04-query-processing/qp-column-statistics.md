---
id: qp-column-statistics
title: What column statistics record
level: intermediate
minutes: 4
sourceLesson: qp-statistics-optimiser
summary: Reading sampled column distributions, statistics targets and physical-order correlation.
---

These examples use PostgreSQL 18. SQL Fundamentals supplies the shop relations: `customers(id, name, email, city, country)`, `orders(id, customer_id, status, ordered_on, total)`, `products(id, price)` and `order_items(order_id)`. IDs join orders to customers and items to orders. Dates use `date`, IDs use `integer`, and totals use `numeric`. Each query fragment uses these names; ellipses and standalone WHERE clauses need the surrounding SELECT shown by their context.

All historical plan fragments and timings in this unit are **illustrative inputs**, not reproduced benchmarks or promises. Their row/page counts describe a hypothetical dataset; actual plans vary with statistics, indexes, settings, cache state and PostgreSQL version. Assume serial execution unless a parallel worker process is shown.

The optimiser has to choose between plans without running them. It does this by **predicting** how many rows each step will produce, converting those predictions into a cost, and picking the cheapest plan it can find. This design, the **cost-based optimiser**, comes from IBM's System R in the late 1970s (Selinger et al., 1979), and remains influential in modern query optimisers.

An optimiser has three parts:

1. **Cardinality estimation**: how many rows will each operator produce?
2. **A cost model**: given those row counts, how expensive is each operator?
3. **A search strategy**: which of the possible plans does it actually consider?

Cardinality estimation is a major source of poor choices. Leis et al., *How Good Are Query Optimizers, Really?* (VLDB 2015), found large estimation errors on its evaluated join workloads; that evidence does not establish one cause for every slow query.

## What the planner knows

`ANALYZE` (run manually or by autovacuum) reads a random sample of each table and stores a summary. Table-level figures live in `pg_class`; column-level ones are in the `pg_stats` view.

```sql
-- Inspect sampled column distributions.
SELECT attname, null_frac, n_distinct,
       most_common_vals,
       most_common_freqs
FROM pg_stats
WHERE tablename = 'orders';
```

For our `orders` table:

| Column | Statistic | Value |
|---|---|---|
| status | n_distinct | 3 |
| status | most common values | shipped, cancelled, pending |
| status | their frequencies | 0.8976, 0.0716, 0.0308 |
| customer_id | n_distinct | 91,709 |
| ordered_on | histogram | 101 bounds |

- **null_frac**: the fraction of NULLs.
- **n_distinct**: the number of distinct values. A negative number means a fraction of the row count (-1 means "every row is unique", as for a primary key).
- **most_common_vals / most_common_freqs (MCVs)**: the most frequent values and how often each appears.
- **histogram_bounds**: values that split the *remaining* (non-MCV) rows into buckets holding equal numbers of rows.
- **physical-order correlation**: how closely the physical row order follows the column's sort order, from -1 to 1. It affects how expensive an index scan's heap reads will be.

For PostgreSQL 18's built-in scalar statistics analysis, the target sample size uses the following model. Special data-type analysers and other requested statistics can affect the required sample:

```formula
n_sample = 300 × t_stats
n_sample = 300 × 100
n_sample = 30,000
where
n_sample: the target sample row count for the standard scalar analyser on a sufficiently large table; the available rows and analyser requirements can change the actual sample
t_stats: the statistics target: `default_statistics_target` (default 100), or a per-column value set with `SET STATISTICS`; the largest target among the table's columns is used
300: a multiplier fixed in PostgreSQL's source code, chosen from a statistical result (Chaudhuri, Motwani and Narasayya, 1998) on how large a random sample must be to build a reliable histogram
In words: with target 100, the standard scalar analyser requests 30,000 sample rows from a sufficiently large table; this is not a universal rule for every type or table.
```

With that default the standard scalar-statistics analyser can retain up to 100 MCVs and about 100 histogram buckets per column. Raising a column's target to 1,000 samples 300,000 rows and keeps up to 1,000 of each, at the cost of a slower ANALYZE and slightly slower planning.

> [!note] The estimates are estimates
> Because ANALYZE samples, the numbers change slightly each time it runs. That's why the planner said 30,767 pending orders when the true count is 30,066.

## Key takeaways
- ANALYZE collects sampled column distributions; the scalar-statistics target controls detail and the requested sample.
- Physical-order correlation concerns heap ordering, whereas inter-column dependence requires multivariate statistics.

## Further reading
- [Statistics used by the planner — PostgreSQL docs](https://www.postgresql.org/docs/18/planner-stats.html)
- [Row estimation examples — PostgreSQL docs](https://www.postgresql.org/docs/18/row-estimation-examples.html)
- [Multivariate statistics examples — PostgreSQL docs](https://www.postgresql.org/docs/18/multivariate-statistics-examples.html)
- [Access path selection in a relational DBMS (Selinger et al., 1979)](https://courses.cs.duke.edu/compsci516/cps216/spring03/papers/selinger-etal-1979.pdf)
- [How Good Are Query Optimizers, Really? (Leis et al., VLDB 2015)](https://www.vldb.org/pvldb/vol9/p204-leis.pdf)
- [Genetic query optimiser — PostgreSQL docs](https://www.postgresql.org/docs/18/geqo.html)


