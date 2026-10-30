---
id: qp-equality-selectivity
title: Equality selectivity from column statistics
level: intermediate
minutes: 3
sourceLesson: qp-statistics-optimiser
summary: How the planner turns column statistics into a row estimate for an equality condition, using the most common values or an even share of the rest.
---

Examples use PostgreSQL 18 and the module's scaled-up shop tables (1,000,000 orders, 100,000 customers; the first lesson lists them). Plans are abbreviated and illustrative: real plans and timings depend on the data, statistics, settings, cache state and version. Assume serial execution.

## Selectivity: from stats to row counts

**Selectivity** is the fraction of rows a condition keeps. Every row estimate starts from it:

```formula essential
n_est = s × n_table
where
n_est: the planner's estimated number of rows the condition keeps (its cardinality estimate)
s: the selectivity of the condition: the fraction of rows it keeps, from 0 (none) to 1 (all)
n_table: the planner's estimate of the number of rows in the table, from `pg_class.reltuples` scaled to the table's current size
In words: the estimated row count is the fraction of rows the condition keeps, times the number of rows in the table.
```

Everything below is about how the planner works out *s* for `column = value`. Which rule it uses depends on what the statistics say about that value.

### A value on the most-common-values list

`WHERE status = 'pending'`: 'pending' is in the MCV list with a sampled frequency of 0.030767, so that frequency is the selectivity. About 3.1% of a million rows is an estimate of 30,767; the actual count is 30,066, about 2% lower. The MCV list exists so that common values get their own measured share instead of an average.

### A column with no common values

`WHERE customer_id = 42`: there is no MCV list, because no customer is especially common. The planner assumes every distinct value matches the same share of rows, so the selectivity is 1 divided by `n_distinct`. A million orders shared among about 91,709 customer IDs is about 11 orders each, so the estimate is 11. The actual count for customer 42 is 14: close enough to choose the right plan. (If the column had NULLs, their fraction would be taken off first; NULL never equals anything.)

### A value missing from the list

When the column *does* have an MCV list but the value isn't on it, the planner takes away the rows the MCVs and NULLs account for, and shares the rest evenly among the remaining distinct values:

```formula reference
s = (1 − Σ f_MCV − f_null)
    / (n_distinct − n_MCV)
where
s: the selectivity for a value not in the MCV list
Σ f_MCV: the sum of the frequencies of all the values in the MCV list
Σ: sum: add up the terms
f_MCV: the frequency of one most-common value
f_null: the fraction of rows that are NULL (`null_frac`)
n_distinct: the estimated number of distinct values in the column; this model needs more distinct values than MCVs
n_MCV: the number of values in the MCV list
In words: whatever share of rows isn't taken by the common values or NULLs is assumed to be spread evenly over the values that aren't common. If 3 common values cover 40% of rows and there are 100 other values, each other value gets 0.6%.
```

PostgreSQL also caps this figure so that a value missing from the list is never estimated as more common than the least common value on it.

> [!analogy] Real-world analogy: guessing a surname's share of a phone book
> Asked how many entries in a city's phone book are "Smith", you might remember that Smith, Jones and Taylor are very common and know roughly how common each is. For an unusual name you have no figure, so you assume the remaining entries are shared evenly among all the other surnames.
>
> **How it maps:** the remembered common surnames are the MCV list with their frequencies, used directly for a listed value. The even share of the rest is the residual rule for a value not on the list, and with no common names at all it becomes 1 divided by the number of distinct names.
>
> **Where it stops:** your memory might be years old; the planner's figures come from a random sample at the last ANALYZE, which can also be out of date, but is refreshed by the database rather than by recollection.

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


