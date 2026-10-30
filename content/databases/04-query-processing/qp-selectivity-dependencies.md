---
id: qp-selectivity-dependencies
title: Ranges and dependent filters
level: intermediate
minutes: 4
sourceLesson: qp-statistics-optimiser
summary: How the planner estimates ranges from a histogram, why it multiplies selectivities for combined filters, and how extended statistics fix correlated columns.
---

Examples use PostgreSQL 18 and the module's scaled-up shop tables (1,000,000 orders, 100,000 customers; the first lesson lists them). Plans are abbreviated and illustrative: real plans and timings depend on the data, statistics, settings, cache state and version. Assume serial execution.

## Range selectivity and dependencies

Selectivity is the fraction of input rows a condition keeps; cardinality is the number kept.

### A range, from the histogram

`WHERE ordered_on >= '2026-01-01'`: the column's histogram splits the non-MCV rows into 100 buckets that each hold the same number of rows. The planner counts the buckets lying above the constant, plus the part of the bucket the constant falls in, assuming values are spread evenly within that bucket:

```formula reference
s_hist ≈ (b_full + b_part) / b_total
where
s_hist: the fraction of the histogram's rows that satisfy the range condition
b_full: the number of complete buckets lying entirely on the matching side of the constant
b_part: the fraction of the constant's own bucket on the matching side, found by assuming values are spread evenly across the bucket (linear interpolation)
b_total: the number of buckets in the histogram, usually 100 at the default statistics target
≈: approximately equal to
In words: count whole buckets on the matching side and add the matching share of the bucket the constant falls in. Here 8 full buckets and a third of another lie above 1 January, so about 8.3% of the rows match.
```

The planner applies that fraction to the non-MCV rows and adds the frequencies of any MCVs that satisfy the condition, giving 84,278 rows. The actual count is 86,346.

Because each bucket holds the same number of rows, buckets are narrow where values are dense and wide where they are sparse. That is how an equal-count histogram follows a skewed distribution without storing every value.

### Combining conditions: the independence assumption

For conditions A and B, PostgreSQL normally multiplies their selectivities when it has no statistics about how the columns relate. It assumes the columns are **independent**: knowing a row's value in one column tells you nothing about the other.

```formula essential
s_AND = s_A × s_B
where
s_AND: the estimated selectivity of the combined condition A AND B
s_A: the selectivity of condition A alone
s_B: the selectivity of condition B alone
In words: if the columns are unrelated, the share of rows passing both filters is the share passing one, times the share passing the other.
```

For `status = 'pending' AND ordered_on >= '2026-01-01'`, about 3% of orders are pending and 8.4% are recent, so the planner expects about 3% of the recent orders to be pending: about 2,600 rows. That is reasonable here, because nothing links status to date in this dataset.

Now consider `customers`, where every Glasgow customer is in Scotland:

```sql
-- Both filters describe the same group.
SELECT * FROM customers
WHERE city = 'Glasgow'
  AND country = 'Scotland';
```

Each condition alone keeps one eighth of customers. Multiplying gives one sixty-fourth, about 1,560 rows. The actual count is 12,500, one eighth, because knowing the city already tells you the country. The estimate is 8 times too low.

The error can go the other way. If `orders` had a `shipped_on` date that pending orders never have, `status = 'pending' AND shipped_on IS NOT NULL` would still be estimated as the product of the two shares, although the true answer is zero. Errors like these feed straight into join and access-path choices for multi-column filters.

> [!analogy] Real-world analogy: guessing who in a crowd is Welsh and speaks Welsh
> If one in twenty people in a stadium is from Wales and one in a hundred speaks Welsh, multiplying suggests one in two thousand is both. But nearly everyone who speaks Welsh is from Wales, so the true figure is close to one in a hundred: the guess is twenty times too low.
>
> **How it maps:** the two shares are single-column selectivities, multiplying them is the independence assumption, and the strong link between the two traits is a correlation between columns that per-column statistics cannot see.
>
> **Where it stops:** a person can use general knowledge to spot the link; the planner sees only the statistics it has collected, so it cannot know about the link until you create extended statistics on those columns.

### Extended statistics

You can tell Postgres to measure the relationship:

```sql
-- Measure dependence before replanning.
CREATE STATISTICS cust_city_country
  (dependencies) ON city, country
  FROM customers;
ANALYZE customers;
```

ANALYZE then records that `city` determines `country` with degree 1.0, and the estimate becomes about 12,400 (12,423 in a PostgreSQL 18.6 run; the exact figure varies with the sample). Other kinds are `ndistinct` (for `GROUP BY a, b` estimates) and `mcv` (common *combinations* of values).

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

