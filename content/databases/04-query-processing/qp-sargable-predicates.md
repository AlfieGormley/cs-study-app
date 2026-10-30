---
id: qp-sargable-predicates
title: Functions, casts and search predicates
level: advanced
minutes: 4
sourceLesson: qp-anti-patterns
summary: Why wrapping an indexed column in a function or cast stops the index being searched, and how to rewrite the condition so it can be.
---

Examples use PostgreSQL 18 and the module's scaled-up shop tables (1,000,000 orders, 100,000 customers; the first lesson lists them). Plans are abbreviated and illustrative: real plans and timings depend on the data, statistics, settings, cache state and version. Assume serial execution.

Most slow queries aren't exotic. They are a handful of recurring shapes that stop the planner using an index, make it misestimate, or make it do work the application didn't need. Each section below shows the anti-pattern, an illustrative PostgreSQL 18-style plan, and the fix.

The indexes on `orders` at this point are the primary key, `(customer_id, ordered_on)`, `(customer_id) INCLUDE (ordered_on, total)`, `(ordered_on)` and the partial index on pending orders.

## 1. Functions on indexed columns

```sql
-- Year extraction is a column expression.
SELECT count(*) FROM orders
WHERE extract(year FROM ordered_on) = 2025;
```

```
Seq Scan on orders  (rows=5000)
  (actual rows=152653.00)
  Filter: (EXTRACT(year FROM ordered_on)
           = '2025'::numeric)
  Rows Removed by Filter: 847347
Execution Time: 65.983 ms
```

Two things went wrong. The index on `ordered_on` cannot provide a selective search bound for this expression, because it is sorted by `ordered_on`, not by `extract(year ...)`. And the estimate is the default 0.5% (5,000) instead of 152,653, because there are no statistics on the expression. Rewrite the condition as a range on the bare column:

```sql
-- Half-open bounds retain the whole year.
WHERE ordered_on >= '2025-01-01'
  AND ordered_on <  '2026-01-01'
```

```
Index Only Scan using orders_date_idx
  (actual rows=152653.00)
  Heap Fetches: 0
Execution Time: 8.652 ms
```

In this illustrative run that is 7.6 times faster, with an accurate estimate. A condition the database can answer with an index is called **sargable** (from "search argument"). The same trap catches `date(created_at) = ...`, `lower(email) = ...`, `col + 1 = 10` and `coalesce(col, 0) = 5`. Either rewrite it so the bare column is compared, or create an expression index that matches it.

> [!analogy] Real-world analogy: a dictionary sorted by spelling
> A printed dictionary is sorted by spelling, so you can find "garden" in seconds. Ask it for every word whose *third* letter is "r", or every word ending in "-ing", and the alphabetical order no longer helps: you would read every page.
>
> **How it maps:** the dictionary is a B-tree index on a column, sorted by the column's own value. A condition on the bare column is a normal look-up. Wrapping the column in a function, such as `extract(year ...)` or a cast, asks about a transformed value the index is not sorted by, so the database falls back to checking every row.
>
> **Where it stops:** you could build a second dictionary sorted by the transformed word, and that is exactly what an expression index is; a real dictionary also has no planner deciding whether reading it cover to cover would be cheaper.

## 2. Type mismatches

```sql
-- Inspect a numeric cast on integer IDs.
EXPLAIN SELECT * FROM orders
WHERE id = 42.0;
```

```
Seq Scan on orders  (rows=5000)
  Filter: ((id)::numeric = 42.0)
```

`id` is an integer and `42.0` is numeric, so Postgres converts every `id` to numeric to compare them. That removes the selective search bound on the ordinary integer primary-key index; a different query might still scan the index as a covering path. `WHERE id = '42'` is fine, because an untyped literal is converted to the column's type.

This usually comes from application code: a driver that sends a parameter as numeric or text, or a comparison that casts the indexed column to an incompatible representation. PostgreSQL can support indexed cross-type integer/bigint comparisons; integer/text comparisons may instead need an explicit cast or fail operator resolution. Look for `::` casts on the **column** side of a Filter.

## 3. Leading wildcards

```sql
-- A suffix supplies no B-tree prefix.
WHERE email LIKE '%42@example.com'
```

There is no selective prefix bound for an ordinary B-tree: matches could start with anything, so they are scattered across the whole index. The plan is a Seq Scan reading all 100,000 customers. A prefix (`LIKE 'c42@%'`) can use a `text_pattern_ops` index, as in the previous lesson. For substring search, consider a trigram index (`CREATE EXTENSION pg_trgm` plus a GIN or GiST index). Full-text search instead matches processed words or tokens, so it is a different search behaviour.

## Key takeaways
- A half-open range of dates can search an ordinary date index while preserving the intended day or year.
- A cast on an integer column to numeric can remove a useful index bound; supported cross-type comparisons behave differently.

## Further reading
- [Sargable — Wikipedia](https://en.wikipedia.org/wiki/Sargable)
- [Use The Index, Luke: functions in WHERE clauses](https://use-the-index-luke.com/sql/where-clause/functions)
- [Use The Index, Luke: paging through results without OFFSET](https://use-the-index-luke.com/no-offset)
- [Don't Do This — PostgreSQL wiki](https://wiki.postgresql.org/wiki/Don%27t_Do_This)
- [Subquery expressions (EXISTS, IN, NOT IN) — PostgreSQL docs](https://www.postgresql.org/docs/18/functions-subquery.html)
- [PREPARE and plan_cache_mode — PostgreSQL docs](https://www.postgresql.org/docs/18/sql-prepare.html)
- [Slow counting — PostgreSQL wiki](https://wiki.postgresql.org/wiki/Slow_Counting)
- [WITH queries (CTEs) — PostgreSQL docs](https://www.postgresql.org/docs/18/queries-with.html)

