---
id: qp-statistics-optimiser
title: Statistics and the cost-based optimiser
level: intermediate
minutes: 16
summary: How the planner guesses row counts from pg_stats, turns them into costs, and searches the space of join orders. Worked selectivity calculations, the independence assumption, extended statistics and stale stats.
---

> [!note] Content gap: benchmark provenance
> Reproducible measurement records for the original laptop timings were not available to this audit, so empirical performance claims are omitted. The plan numbers below are retained only as illustrative inputs for learning EXPLAIN, not verified measurements or promised speedups. Measure your own representative workload.


The optimiser has to choose between plans without running them. It does this by **predicting** how many rows each step will produce, converting those predictions into a cost, and picking the cheapest plan it can find. This design, the **cost-based optimiser**, comes from IBM's System R in the late 1970s (Selinger et al., 1979), and every serious relational database still follows it.

An optimiser has three parts:

1. **Cardinality estimation**: how many rows will each operator produce?
2. **A cost model**: given those row counts, how expensive is each operator?
3. **A search strategy**: which of the possible plans does it actually consider?

The first is the weakest. When a plan is bad, the cause is usually a wrong row estimate, not a wrong cost formula. A well-known study (Leis et al., *How Good Are Query Optimizers, Really?*, VLDB 2015) found exactly that across several commercial and open-source systems.

## What the planner knows

`ANALYZE` (run manually or by autovacuum) reads a random sample of each table and stores a summary. Table-level figures live in `pg_class`; column-level ones are in the `pg_stats` view.

```sql
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
| status | their frequencies | 0.898, 0.072, 0.031 |
| customer_id | n_distinct | 91,709 |
| ordered_on | histogram | 101 bounds |

- **null_frac**: the fraction of NULLs.
- **n_distinct**: the number of distinct values. A negative number means a fraction of the row count (-1 means "every row is unique", as for a primary key).
- **most_common_vals / most_common_freqs (MCVs)**: the most frequent values and how often each appears.
- **histogram_bounds**: values that split the *remaining* (non-MCV) rows into buckets holding equal numbers of rows.
- **correlation**: how closely the physical row order follows the column's sort order, from -1 to 1. It affects how expensive an index scan's heap reads will be.

With the default `default_statistics_target = 100`, ANALYZE samples 300 x 100 = 30,000 rows per table, and keeps up to 100 MCVs and 100 histogram buckets per column.

> [!note] The estimates are estimates
> Because ANALYZE samples, the numbers change slightly each time it runs. That's why the planner said 30,767 pending orders when the true count is 30,066.

## Selectivity: from stats to row counts

**Selectivity** is the fraction of rows a condition keeps. The row estimate is selectivity x table rows. Here are the main rules, using the illustrative table statistics.

### Equality on a common value

`WHERE status = 'pending'`: 'pending' is in the MCV list with frequency 0.030767.

```
rows = 0.030767 x 1,000,000
     = 30,767   (actual 30,066)
```

### Equality on any other value

`WHERE customer_id = 42`: there's no MCV list (no value is especially common), so the planner assumes values are evenly spread.

```
rows = 1,000,000 / n_distinct
     = 1,000,000 / 91,709
     = 10.9 -> 11   (actual 14)
```

### A range, from the histogram

`WHERE ordered_on >= '2026-01-01'`: the histogram has 100 buckets, each holding 1% of the non-MCV rows. The date falls a third of the way from the end of the bucket that runs from 2025-12-18 to 2026-01-08, and 8 more buckets lie above it.

```
fraction ~ (8 + 1/3) / 100 = 8.3%
estimate = 84,278   (actual 86,346)
```

The planner interpolates linearly within a bucket and adds in any MCVs that satisfy the condition, which is why the final figure is slightly above 8.3%.

### Combining conditions: the independence assumption

For `A AND B`, Postgres multiplies the selectivities, assuming the columns are **independent**:

```
pending AND ordered_on >= 2026-01-01
  = 0.030767 x 0.084278 x 1,000,000
  = 2,593 rows
```

Status and date really are independent in this data, so that's about right. But consider `customers`, where every Glasgow customer is in Scotland:

```sql
SELECT * FROM customers
WHERE city = 'Glasgow'
  AND country = 'Scotland';
```

```
estimate: 1/8 x 1/8 x 100,000 ~ 1,560
actual:   12,500
```

The planner is out by a factor of 8 because knowing the city already tells you the country. Errors like this are the most common cause of bad plans for multi-column filters.

### Extended statistics

You can tell Postgres to measure the relationship:

```sql
CREATE STATISTICS cust_city_country
  (dependencies) ON city, country
  FROM customers;
ANALYZE customers;
```

ANALYZE then records that `city` determines `country` with degree 1.0, and the estimate becomes about 12,700. Other kinds are `ndistinct` (for `GROUP BY a, b` estimates) and `mcv` (common *combinations* of values).

### When there are no statistics

For conditions the planner can't analyse, it uses fixed default selectivities:

| Condition | Default | Example |
|---|---|---|
| `expr = const` | 0.5% | `lower(email) = '...'`: 500 of 100,000 |
| `expr < const` | 1/3 | `price * 2 > 100`: 3,333 of 10,000 |

The planner has stats on the `email` column, but not on `lower(email)`. An **expression index** on `lower(email)` fixes this as a side effect, because ANALYZE then gathers statistics on the indexed expression.

### Join estimates

For an equijoin, Postgres estimates selectivity as roughly 1 / max(n_distinct of the two keys) (refined using MCV lists where it has them):

```
orders JOIN customers ON customer_id = id
  = 1,000,000 x 100,000 / 100,000
  = 1,000,000 rows
```

Errors **multiply** as they go up the tree. If each of three joins is out by a factor of 3, the final estimate can be out by 27, and the join algorithm choices near the top are made on wrong numbers.

## The cost model

Postgres costs are in arbitrary units anchored on one sequential page read = 1.0:

| Parameter | Default | Charged for |
|---|---|---|
| `seq_page_cost` | 1.0 | Page read in order |
| `random_page_cost` | 4.0 | Page read out of order |
| `cpu_tuple_cost` | 0.01 | Each row processed |
| `cpu_index_tuple_cost` | 0.005 | Each index entry |
| `cpu_operator_cost` | 0.0025 | Each operator or function call |

A sequential scan with one filter costs pages x 1.0, plus rows x 0.01, plus rows x 0.0025 for the comparison:

```
Seq Scan on orders (status = 'pending')
  7,353 x 1.0       =  7,353
  1,000,000 x 0.01  = 10,000
  1,000,000 x 0.0025 = 2,500
  total             = 19,853
```

EXPLAIN shows `cost=0.00..19853.00`: exactly this. An index scan's cost depends on how many index and heap pages it expects to touch, charged at `random_page_cost`, discounted by `correlation` and `effective_cache_size` (the planner's guess of how much data is cached).

> [!tip] Tune random_page_cost for SSDs
> The default of 4.0 dates from spinning disks. On SSDs, or when most data is cached, many teams set it to around 1.1 so the planner is less reluctant to use indexes. Test the change on your workload first.

## Searching the plan space

For each table the planner generates the candidate access paths (seq scan, each usable index, bitmap scans). It then has to choose a **join order**, and that space explodes:

| Tables | Left-deep orders | All tree shapes |
|---|---|---|
| 3 | 6 | 12 |
| 5 | 120 | 1,680 |
| 10 | 3,628,800 | 17,643,225,600 |

Postgres uses System R-style **dynamic programming**. It finds the best way to join every pair of tables, then every set of three built from those, and so on. It keeps the cheapest path for each subset, plus any path that produces a useful sort order (an "interesting order") that might avoid a sort later. Working over subsets (2^10 = 1,024 for ten tables) rather than full orderings is what makes it tractable.

At or above `geqo_threshold` (default 12) FROM items, exhaustive search is too slow, so Postgres switches to **GEQO**, a genetic algorithm that finds a good plan rather than the best. Separately, `join_collapse_limit` (default 8) caps how many explicit `JOIN`s are merged into one list for reordering.

## Stale statistics

Statistics describe the table as it was at the last ANALYZE. Autovacuum re-analyses a table when the number of changed rows exceeds `50 + 10%` of its size. In between, the planner can be badly wrong:

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

The planner did notice that the table had grown, because it scales `reltuples` by the current number of pages. But the MCV list said every row is 'a', so 'b' looked almost non-existent. Feed that "1 row" into a join and you get the 600,000-loop nested loop from the previous lesson.

Practical rules:

- Run `ANALYZE` after bulk loads, before querying the new data.
- **Temporary tables are never analysed by autovacuum.** Analyse them yourself.
- For skewed columns, raise the per-column target: `ALTER TABLE orders ALTER COLUMN customer_id SET STATISTICS 1000;`
- Add extended statistics for correlated columns used together.

## Key takeaways
- The planner estimates rows from `pg_stats`: MCVs for common values, 1/n_distinct for the rest, histograms for ranges.
- It multiplies selectivities for AND, assuming independence. Correlated columns cause underestimates; `CREATE STATISTICS` fixes them.
- Functions on columns get fixed default guesses (0.5% for equality, 1/3 for inequality).
- Costs are in units of one sequential page read; the seq scan formula is pages + rows x (0.01 + 0.0025 per condition).
- With default settings, GEQO is considered from 12 FROM items; smaller join searches normally use dynamic programming, subject to join-collapse limits.
- Most bad plans come from bad row estimates, and stale stats are a common cause.

## Further reading
- [Statistics used by the planner — PostgreSQL docs](https://www.postgresql.org/docs/current/planner-stats.html)
- [Row estimation examples — PostgreSQL docs](https://www.postgresql.org/docs/current/row-estimation-examples.html)
- [Multivariate statistics examples — PostgreSQL docs](https://www.postgresql.org/docs/current/multivariate-statistics-examples.html)
- [Access path selection in a relational DBMS (Selinger et al., 1979)](https://courses.cs.duke.edu/compsci516/cps216/spring03/papers/selinger-etal-1979.pdf)
- [How Good Are Query Optimizers, Really? (Leis et al., VLDB 2015)](https://www.vldb.org/pvldb/vol9/p204-leis.pdf)
- [Genetic query optimiser — PostgreSQL docs](https://www.postgresql.org/docs/current/geqo.html)
