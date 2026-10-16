---
id: qp-selectivity-dependencies
title: Ranges and dependent filters
level: intermediate
minutes: 5
sourceLesson: qp-statistics-optimiser
summary: Ranges and dependent filters with worked examples and explicit assumptions.
---

These examples use PostgreSQL 18. SQL Fundamentals supplies the shop relations: `customers(id, name, email, city, country)`, `orders(id, customer_id, status, ordered_on, total)`, `products(id, price)` and `order_items(order_id)`. IDs join orders to customers and items to orders. Dates use `date`, IDs use `integer`, and totals use `numeric`. Each query fragment uses these names; ellipses and standalone WHERE clauses need the surrounding SELECT shown by their context.

All historical plan fragments and timings in this unit are **illustrative inputs**, not reproduced benchmarks or promises. Their row/page counts describe a hypothetical dataset; actual plans vary with statistics, indexes, settings, cache state and PostgreSQL version. Assume serial execution unless a parallel worker process is shown.

## Range selectivity and dependencies

Selectivity is the fraction of input rows retained by a condition; cardinality is the number retained. The numerical statistics below are illustrative, rather than measurements of the small executable fixtures.

### A range, from the histogram

`WHERE ordered_on >= '2026-01-01'`: the histogram has 100 buckets, each holding 1% of the non-MCV rows. The date leaves one third of the bucket above it; that bucket runs from 2025-12-18 to 2026-01-08, and 8 more buckets lie above it. Count the buckets above the constant, including the part of the bucket it falls in:

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

For conditions A and B, PostgreSQL normally multiplies their selectivities when it has no applicable dependency information, assuming the columns are **independent**: knowing a row's value in one column tells you nothing about the other. For `status = 'pending' AND ordered_on >= '2026-01-01'`:

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

The illustrative calculation assumes status and date are independent; that assumption needs checking on real data. But consider `customers`, where every Glasgow customer is in Scotland:

```sql
-- Both filters describe the same group.
SELECT * FROM customers
WHERE city = 'Glasgow'
  AND country = 'Scotland';
```

The eight cities are equally common; Glasgow and Scotland each cover 1/8 of customers in this fixture, so the planner multiplies:

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

The actual count is 12,500, one eighth of the customers. The planner is out by a factor of 8 because knowing the city already tells you the country. Errors like this can affect plan choices for multi-column filters.

### Extended statistics

You can tell Postgres to measure the relationship:

```sql
-- Measure dependence before replanning.
CREATE STATISTICS cust_city_country
  (dependencies) ON city, country
  FROM customers;
ANALYZE customers;
```

ANALYZE then records that `city` determines `country` with degree 1.0, and the estimate becomes about 12,700. Other kinds are `ndistinct` (for `GROUP BY a, b` estimates) and `mcv` (common *combinations* of values).

## Key takeaways
- Histograms describe non-MCV rows and interpolate within buckets.
- Multiplying selectivities assumes independence; suitable extended statistics can measure dependencies or value combinations.

## Further reading
- [Statistics used by the planner — PostgreSQL docs](https://www.postgresql.org/docs/18/planner-stats.html)
- [Row estimation examples — PostgreSQL docs](https://www.postgresql.org/docs/18/row-estimation-examples.html)
- [Multivariate statistics examples — PostgreSQL docs](https://www.postgresql.org/docs/18/multivariate-statistics-examples.html)
- [Access path selection in a relational DBMS (Selinger et al., 1979)](https://courses.cs.duke.edu/compsci516/cps216/spring03/papers/selinger-etal-1979.pdf)
- [How Good Are Query Optimizers, Really? (Leis et al., VLDB 2015)](https://www.vldb.org/pvldb/vol9/p204-leis.pdf)
- [Genetic query optimiser — PostgreSQL docs](https://www.postgresql.org/docs/18/geqo.html)

