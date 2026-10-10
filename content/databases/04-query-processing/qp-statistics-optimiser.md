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

The size of ANALYZE's random sample is set by the statistics target:

```formula
n_sample = 300 × t_stats
n_sample = 300 × 100
n_sample = 30,000
where
n_sample: the number of rows ANALYZE samples from a large table (a table with fewer rows is read completely)
t_stats: the statistics target: `default_statistics_target` (default 100), or a per-column value set with `SET STATISTICS`; the largest target among the table's columns is used
300: a multiplier fixed in PostgreSQL's source code, chosen from a statistical result (Chaudhuri, Motwani and Narasayya, 1998) on how large a random sample must be to build a reliable histogram
In words: with the default target of 100, ANALYZE reads a random sample of 30,000 rows, however big the table is.
```

With that default it also keeps up to 100 MCVs and 100 histogram buckets per column. Raising a column's target to 1,000 samples 300,000 rows and keeps up to 1,000 of each, at the cost of a slower ANALYZE and slightly slower planning.

> [!note] The estimates are estimates
> Because ANALYZE samples, the numbers change slightly each time it runs. That's why the planner said 30,767 pending orders when the true count is 30,066.

## Selectivity: from stats to row counts

**Selectivity** is the fraction of rows a condition keeps. Every row estimate starts from it:

```formula
n_est = s × n_table
where
n_est: the planner's estimated number of rows the condition keeps (its cardinality estimate)
s: the selectivity of the condition: the fraction of rows it keeps, from 0 (none) to 1 (all)
n_table: the planner's estimate of the number of rows in the table, from `pg_class.reltuples` scaled to the table's current size
In words: the estimated row count is the fraction of rows the condition keeps, times the number of rows in the table.
```

The rules below are all ways of working out *s*, using the illustrative table statistics.

### Equality on a common value

`WHERE status = 'pending'`: 'pending' is in the MCV list, so the planner uses its measured frequency, 0.030767, as the selectivity:

```formula
n_est = f_MCV × n_table
n_est = 0.030767 × 1,000,000
n_est = 30,767
where
n_est: the estimated number of matching rows
f_MCV: the value's frequency in the most-common-values (MCV) list: the fraction of sampled rows holding it, here 0.030767 for 'pending'
n_table: the number of rows in the table, here 1,000,000
In words: if about 3.1% of the sample was 'pending', expect about 3.1% of the table to be.
```

The actual count is 30,066, so the estimate is about 2% high.

### Equality on any other value

`WHERE customer_id = 42`: there's no MCV list (no value is especially common), so the planner assumes values are evenly spread and every value matches the same share of rows. The column has no NULLs here; if it had, their fraction would be taken off first:

```formula
s = 1 / n_distinct
n_est = n_table / n_distinct
n_est = 1,000,000 / 91,709
n_est ≈ 10.9 ≈ 11
where
s: the selectivity: the fraction of rows expected to match
n_distinct: the estimated number of distinct values in the column, here 91,709 customer ids
n_est: the estimated number of matching rows, rounded to a whole number
n_table: the number of rows in the table, here 1,000,000
≈: approximately equal to
In words: a million orders shared evenly among about 92,000 customers gives about 11 orders per customer.
```

The actual count for customer 42 is 14: close enough to choose the right plan.

When the column *does* have an MCV list but the value isn't on it, the planner takes away the rows the MCVs and NULLs account for and shares the rest evenly among the remaining distinct values:

```formula
s = (1 − Σ f_MCV − f_null)
    / (n_distinct − n_MCV)
where
s: the selectivity for a value not in the MCV list
Σ f_MCV: the sum of the frequencies of all the values in the MCV list
Σ: sum: add up the terms
f_MCV: the frequency of one most-common value
f_null: the fraction of rows that are NULL (`null_frac`)
n_distinct: the estimated number of distinct values in the column
n_MCV: the number of values in the MCV list
In words: whatever fraction of rows isn't covered by the common values or NULLs is assumed to be spread evenly over the values that aren't common.
```

For example, if 3 MCVs cover 40% of rows, there are no NULLs and 103 distinct values, any other value gets (1 − 0.4) / 100 = 0.6% of rows. PostgreSQL also caps this figure so that a value missing from the list is never estimated as more common than the least common value on it.

### A range, from the histogram

`WHERE ordered_on >= '2026-01-01'`: the histogram has 100 buckets, each holding 1% of the non-MCV rows. The date falls a third of the way from the end of the bucket that runs from 2025-12-18 to 2026-01-08, and 8 more buckets lie above it. Count the buckets above the constant, including the part of the bucket it falls in:

```formula
s_hist ≈ (b_full + b_part) / b_total
s_hist ≈ (8 + 1/3) / 100
s_hist ≈ 0.083 (8.3%)
where
s_hist: the fraction of the histogram's rows that satisfy the condition
b_full: the number of complete buckets lying entirely above the constant, here 8
b_part: the fraction of the constant's own bucket that lies above it, here 1/3, found by assuming values are spread evenly across the bucket (linear interpolation)
b_total: the number of buckets in the histogram, here 100
≈: approximately equal to
In words: about 8⅓ of the 100 equal-sized buckets lie above 1 January, so about 8.3% of the rows do.
```

The planner applies that fraction to the non-MCV rows and adds the frequencies of any MCVs that satisfy the condition, which is why its final estimate, 84,278 rows, is slightly above 8.3%. The actual count is 86,346.

### Combining conditions: the independence assumption

For `A AND B`, Postgres multiplies the selectivities, assuming the columns are **independent**: knowing a row's value in one column tells you nothing about the other. For `status = 'pending' AND ordered_on >= '2026-01-01'`:

```formula
s_AND = s_A × s_B
n_est = s_A × s_B × n_table
n_est = 0.030767 × 0.084278 × 1,000,000
n_est ≈ 2,593
where
s_AND: the selectivity of the combined condition A AND B
s_A: the selectivity of the first condition, here 0.030767 for status = 'pending'
s_B: the selectivity of the second condition, here 0.084278 for the date range (84,278 of 1,000,000 rows)
n_est: the estimated number of rows satisfying both conditions
n_table: the number of rows in the table, here 1,000,000
≈: approximately equal to
In words: if 3% of orders are pending and 8.4% are recent, and the two are unrelated, about 3% of the recent orders are pending: about 2,600 rows.
```

Status and date really are independent in this data, so that's about right. But consider `customers`, where every Glasgow customer is in Scotland:

```sql
SELECT * FROM customers
WHERE city = 'Glasgow'
  AND country = 'Scotland';
```

Each of the 8 cities and each of the 8 countries covers 1/8 of customers, so the planner multiplies:

```formula
n_est = s_city × s_country × n_table
n_est = 1/8 × 1/8 × 100,000
n_est ≈ 1,560
where
n_est: the planner's estimated number of matching customers
s_city: the selectivity of city = 'Glasgow', 1/8
s_country: the selectivity of country = 'Scotland', 1/8
n_table: the number of customers, 100,000
≈: approximately equal to (the exact product is 1,562.5)
In words: treating city and country as unrelated, the planner expects one eighth of one eighth of the customers.
```

The actual count is 12,500, one eighth of the customers. The planner is out by a factor of 8 because knowing the city already tells you the country. Errors like this are the most frequent cause of bad plans for multi-column filters.

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

For an equijoin (a join on `=`), the selectivity is the fraction of all possible row pairs that match. Postgres estimates it from the distinct counts of the two join keys, refined using MCV lists where it has them. For `orders JOIN customers ON customer_id = id`:

```formula
s_join ≈ 1 / max(d_R, d_S)
n_est = n_R × n_S × s_join
n_est = 1,000,000 × 100,000 / 100,000
n_est = 1,000,000
where
s_join: the join selectivity: the fraction of all (order, customer) pairs that satisfy the join condition
max: the larger of the values in brackets
d_R: the number of distinct values of the join key in orders, here 91,709 customer ids
d_S: the number of distinct values of the join key in customers, here 100,000 ids
n_R: the number of rows in orders, 1,000,000
n_S: the number of rows in customers, 100,000
n_est: the estimated number of rows the join produces
≈: approximately equal to
In words: every order matches one customer out of 100,000, so the join produces one row per order: about a million.
```

The formula assumes every key value on the side with fewer distinct values has a match on the other side, which is exactly true for a foreign key.

Errors **multiply** as they go up the tree. If each of three joins is out by a factor of 3, the final estimate can be out by 27, and the join algorithm choices near the top are made on wrong numbers.

## The cost model

Postgres costs are in arbitrary units anchored on one sequential page read = 1.0:

| Parameter | Default | Charged for |
|---|---|---|
| `seq_page_cost` | 1.0 | Page read in order |
| `random_page_cost` | 4.0 | Page read at random |
| `cpu_tuple_cost` | 0.01 | Each row processed |
| `cpu_index_tuple_cost` | 0.005 | Each index entry |
| `cpu_operator_cost` | 0.0025 | Each operator or function call |

A sequential scan pays for every page it reads, every row it processes and every condition it evaluates on each row. For `orders` with `status = 'pending'`:

```formula
C_seq = P × c_page
      + n × c_tuple
      + n × q × c_op
C_seq = 7,353 × 1.0
      + 1,000,000 × 0.01
      + 1,000,000 × 1 × 0.0025
C_seq = 7,353 + 10,000 + 2,500
C_seq = 19,853
where
C_seq: the estimated total cost of the sequential scan, in planner cost units (1 unit = one sequential page read)
P: the number of pages in the table, here 7,353
c_page: `seq_page_cost`, default 1.0 per page read in order
n: the number of rows in the table, here 1,000,000
c_tuple: `cpu_tuple_cost`, default 0.01 per row processed
q: the number of operators (comparisons) in the filter evaluated on each row, here 1 for status = 'pending'
c_op: `cpu_operator_cost`, default 0.0025 per operator or function call
In words: read 7,353 pages, process a million rows and test one condition on each; the row work costs more than the page reads.
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

Both columns come from counting arrangements:

```formula
L(n) = n!
T(n) = (2 × n − 2)! / (n − 1)!
L(10) = 10! = 3,628,800
T(10) = 18! / 9! = 17,643,225,600
where
L(n): the number of left-deep join orders for n tables: each step joins one more base table to the result so far, so an order is just a sequence of the tables
T(n): the number of join trees of any shape (left-deep or bushy), counting which input goes on which side of each join
n: the number of tables being joined
!: factorial: multiply all the whole numbers from 1 up to the number, so 3! = 1 × 2 × 3 = 6
In words: the number of possible plans grows faster than exponentially, so trying them all is hopeless beyond a handful of tables.
```

For 3 tables, L is 3! = 6 and T is 4! / 2! = 12, matching the first row.

Postgres uses System R-style **dynamic programming**. It finds the best way to join every pair of tables, then every set of three built from those, and so on. It keeps the cheapest plan for each subset, plus any plan that produces a useful sort order (an "interesting order") that might avoid a sort later. Working over subsets rather than full orderings is what makes it tractable:

```formula
N_sub = 2^n
N_sub = 2^10 = 1,024
where
N_sub: the number of subsets of the tables, counting the empty set; each table is either in a subset or not, giving 2 choices per table
n: the number of tables being joined, here 10
In words: ten tables have only 1,024 subsets, against 3.6 million orderings.
```

The work per subset still varies, because each subset can be split in several ways and each split has several physical join methods, but the count stays far below the number of trees.

At or above `geqo_threshold` (default 12) FROM items, exhaustive search is too slow, so Postgres switches to **GEQO**, a genetic algorithm that finds a good plan rather than the best. Separately, `join_collapse_limit` (default 8) caps how many explicit `JOIN`s are merged into one list for reordering.

## Stale statistics

Statistics describe the table as it was at the last ANALYZE. Autovacuum re-analyses a table once enough rows have changed since the last ANALYZE:

```formula
n_trig = n_base + k_scale × n_table
n_trig = 50 + 0.1 × 1,000
n_trig = 150
where
n_trig: the number of inserted, updated or deleted rows since the last ANALYZE that makes autovacuum analyse the table again
n_base: `autovacuum_analyze_threshold`, a fixed number of rows, default 50
k_scale: `autovacuum_analyze_scale_factor`, the fraction of the table, default 0.1 (10%)
n_table: the table's estimated row count (`pg_class.reltuples`, updated by VACUUM and ANALYZE), here 1,000
In words: a table is re-analysed after about a tenth of it has changed, plus 50 rows.
```

For the 1,000-row table below, 150 changes are enough, and a 500,000-row load passes that easily. But autovacuum only checks tables periodically (every minute by default, set by `autovacuum_naptime`), so a query run straight after the load still sees the old statistics. On a 100-million-row table, 10 million rows must change first. In between, the planner can be badly wrong:

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
- The planner estimates rows from `pg_stats`: MCVs for common values, 1/n_distinct for the rest, histograms for ranges.
- It multiplies selectivities for AND, assuming independence. Correlated columns cause underestimates; `CREATE STATISTICS` fixes them.
- Functions on columns get fixed default guesses (0.5% for equality, 1/3 for inequality).
- Costs are in units of one sequential page read. A sequential scan costs 1 per page, plus 0.01 per row, plus 0.0025 per row for each condition.
- With default settings, GEQO is considered from 12 FROM items; smaller join searches normally use dynamic programming, subject to join-collapse limits.
- Most bad plans come from bad row estimates, and stale stats are a frequent culprit.

## Further reading
- [Statistics used by the planner — PostgreSQL docs](https://www.postgresql.org/docs/current/planner-stats.html)
- [Row estimation examples — PostgreSQL docs](https://www.postgresql.org/docs/current/row-estimation-examples.html)
- [Multivariate statistics examples — PostgreSQL docs](https://www.postgresql.org/docs/current/multivariate-statistics-examples.html)
- [Access path selection in a relational DBMS (Selinger et al., 1979)](https://courses.cs.duke.edu/compsci516/cps216/spring03/papers/selinger-etal-1979.pdf)
- [How Good Are Query Optimizers, Really? (Leis et al., VLDB 2015)](https://www.vldb.org/pvldb/vol9/p204-leis.pdf)
- [Genetic query optimiser — PostgreSQL docs](https://www.postgresql.org/docs/current/geqo.html)
