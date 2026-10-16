---
id: qp-equality-selectivity
title: Equality selectivity from column statistics
level: intermediate
minutes: 4
sourceLesson: qp-statistics-optimiser
summary: Equality selectivity from column statistics using explicit models and assumptions.
---

These examples use PostgreSQL 18. SQL Fundamentals supplies the shop relations: `customers(id, name, email, city, country)`, `orders(id, customer_id, status, ordered_on, total)`, `products(id, price)` and `order_items(order_id)`. IDs join orders to customers and items to orders. Dates use `date`, IDs use `integer`, and totals use `numeric`. Each query fragment uses these names; ellipses and standalone WHERE clauses need the surrounding SELECT shown by their context.

All historical plans and figures below are illustrative model inputs. Actual execution depends on version, workload and settings.

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

The rules below are all ways of working out *s*, using the illustrative column-frequency statistics.

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

This residual model requires a positive count of remaining distinct non-NULL values.

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

For example, if 3 MCVs cover 40% of rows, there are no NULLs and 103 distinct values, the remaining 60% of rows are shared among 100 values, giving 0.6% per value. PostgreSQL also caps this figure so that a value missing from the list is never estimated as more common than the least common value on it.

## Key takeaways
- Use MCV frequencies for listed values; share residual probability among the remaining distinct non-NULL values.
- The estimates assume sampled frequencies and distinct counts represent the current table.

## Further reading
- [Statistics used by the planner — PostgreSQL docs](https://www.postgresql.org/docs/18/planner-stats.html)
- [Row estimation examples — PostgreSQL docs](https://www.postgresql.org/docs/18/row-estimation-examples.html)
- [Multivariate statistics examples — PostgreSQL docs](https://www.postgresql.org/docs/18/multivariate-statistics-examples.html)
- [Access path selection in a relational DBMS (Selinger et al., 1979)](https://courses.cs.duke.edu/compsci516/cps216/spring03/papers/selinger-etal-1979.pdf)
- [How Good Are Query Optimizers, Really? (Leis et al., VLDB 2015)](https://www.vldb.org/pvldb/vol9/p204-leis.pdf)
- [Genetic query optimiser — PostgreSQL docs](https://www.postgresql.org/docs/18/geqo.html)


