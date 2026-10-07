---
id: qp-anti-patterns
title: Common performance anti-patterns
level: advanced
minutes: 17
summary: The query shapes that defeat the planner. Non-sargable predicates, type mismatches, OFFSET pagination, NOT IN, correlated subqueries, DISTINCT as a join fix, OR across columns, N+1 queries, generic plans and exact counts, each with an illustrative plan and a possible rewrite.
---

> [!note] Content gap: benchmark provenance
> Reproducible measurement records for the original laptop timings were not available to this audit, so empirical performance claims are omitted. The plan numbers below are retained only as illustrative inputs for learning EXPLAIN, not verified measurements or promised speedups. Measure your own representative workload.


Most slow queries aren't exotic. They are a handful of recurring shapes that stop the planner using an index, make it misestimate, or make it do work the application didn't need. Each section below shows the anti-pattern, an illustrative PostgreSQL 18-style plan, and the fix.

The indexes on `orders` at this point are the primary key, `(customer_id, ordered_on)`, `(customer_id) INCLUDE (ordered_on, total)`, `(ordered_on)` and the partial index on pending orders.

## 1. Functions on indexed columns

```sql
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

Two things went wrong. The index on `ordered_on` can't be used, because it is sorted by `ordered_on`, not by `extract(year ...)`. And the estimate is the default 0.5% (5,000) instead of 152,653, because there are no statistics on the expression. Rewrite the condition as a range on the bare column:

```sql
WHERE ordered_on >= '2025-01-01'
  AND ordered_on <  '2026-01-01'
```

```
Index Only Scan using orders_date_idx
  (actual rows=152653.00)
  Heap Fetches: 0
Execution Time: 8.652 ms
```

That's 7.6 times faster, with an accurate estimate. A condition the database can answer with an index is called **sargable** (from "search argument"). The same trap catches `date(created_at) = ...`, `lower(email) = ...`, `col + 1 = 10` and `coalesce(col, 0) = 5`. Either rewrite it so the bare column is compared, or create an expression index that matches it.

## 2. Type mismatches

```sql
EXPLAIN SELECT * FROM orders
WHERE id = 42.0;
```

```
Seq Scan on orders  (rows=5000)
  Filter: ((id)::numeric = 42.0)
```

`id` is an integer and `42.0` is numeric, so Postgres converts every `id` to numeric to compare them. That's a function on the column, so the primary key can't be used. `WHERE id = '42'` is fine, because an untyped literal is converted to the column's type.

This usually comes from application code: a driver that sends a parameter as numeric or text, or a comparison that casts the indexed column to an incompatible representation. PostgreSQL can support indexed cross-type integer/bigint comparisons; integer/text comparisons may instead need an explicit cast or fail operator resolution. Look for `::` casts on the **column** side of a Filter.

## 3. Leading wildcards

```sql
WHERE email LIKE '%42@example.com'
```

No B-tree can help: matches could start with anything, so they are scattered across the whole index. The plan is a Seq Scan reading all 100,000 customers. A prefix (`LIKE 'c42@%'`) can use a `text_pattern_ops` index, as in the previous lesson. For substring search, use a trigram index (`CREATE EXTENSION pg_trgm` plus a GIN index) or full-text search.

## 4. OFFSET pagination

```sql
SELECT * FROM orders
ORDER BY id
LIMIT 20 OFFSET 900000;
```

```
Limit  (actual rows=20.00)
-> Index Scan using orders_pkey
     (actual rows=900020.00)
Execution Time: 66.979 ms
```

To skip 900,000 rows, Postgres has to produce them: it walked 900,020 index entries and fetched their rows, then threw away all but 20. Page 1 is fast and page 45,000 is slow, and the deeper users go the worse it gets.

**Keyset pagination** remembers where the last page ended:

```sql
SELECT * FROM orders
WHERE id > 900000   -- last id seen
ORDER BY id
LIMIT 20;
```

```
Limit  (actual rows=20.00)
-> Index Scan using orders_pkey
     Index Cond: (id > 900000)
Execution Time: 0.014 ms
```

In these illustrative timings the difference is large. Keyset pagination avoids work proportional to the skipped offset, though actual latency still depends on the data, index and system state. For a non-unique sort column, use a tie-breaker: `WHERE (ordered_on, id) < ($1, $2) ORDER BY ordered_on DESC, id DESC`. The trade-off is that you can't jump straight to page 371, which most interfaces don't need.

## 5. NOT IN with a subquery

```sql
SELECT count(*) FROM customers c
WHERE c.id NOT IN
  (SELECT customer_id FROM orders
   WHERE status = 'pending');
```

`NOT IN` has two problems.

**Semantics.** If the subquery returns even one NULL, `x NOT IN (...)` is never true (it's NULL or false), so no customer rows satisfy the filter. This `count(*)` query still returns one result row containing 0. That is almost never the intended count.

**Performance.** Because of those NULL rules, Postgres can't turn `NOT IN` into an anti-join. It runs the subquery once and probes a hash table of its results (`hashed SubPlan`), which was fine here: 17 ms. But if the subquery's results don't fit in `work_mem`, the plan becomes a plain SubPlan that rescans the materialised results for **every** outer row. With `work_mem` reduced to 64 kB the estimated cost jumped from about 10,700 to 976 million.

`NOT EXISTS` has the semantics people expect and becomes a real anti-join:

```sql
WHERE NOT EXISTS (
  SELECT 1 FROM orders o
  WHERE o.customer_id = c.id
    AND o.status = 'pending')
```

```
Hash Right Anti Join
  Hash Cond: (o.customer_id = c.id)
Execution Time: 22.855 ms
```

Here it was slightly slower than the hashed `NOT IN`, but it can't fall off the cliff, and it gives the right answer when NULLs appear.

## 6. Correlated subqueries: a nested loop in disguise

```sql
SELECT c.id,
  (SELECT count(*) FROM orders o
   WHERE o.customer_id = c.id)
FROM customers c
WHERE c.city = 'York';
```

Postgres runs a scalar subquery in the SELECT list once **per outer row**:

```
Seq Scan on customers c
  (actual rows=12500.00)
  SubPlan 1
  -> Aggregate (loops=12500)
     -> Index Only Scan using
          orders_cust_cov_idx
          (loops=12500)
Execution Time: 30.428 ms
```

That's a nested loop over 12,500 customers. With an index on `orders(customer_id)` each loop is cheap and the whole thing took 30 ms. The equivalent `LEFT JOIN ... GROUP BY` actually took 84 ms here, because it hashed all 1,000,000 orders.

So correlated subqueries aren't always slow, but they are only as fast as the inner lookup. Without the index, each of the 12,500 loops would be a full scan of `orders`: an estimated cost of about 248 million, against 23,000 for the join. Check `loops` on any SubPlan.

## 7. DISTINCT to hide duplicate rows

"Customers in Bath who have ordered" written as a join returns one row per order, so people add DISTINCT:

```sql
SELECT DISTINCT c.*
FROM customers c
JOIN orders o ON o.customer_id = c.id
WHERE c.city = 'Bath';
```

The join produced 125,174 rows, then a HashAggregate collapsed them back to 12,500: 42 ms. The question was really "does at least one order exist?", which is a semi-join:

```sql
SELECT c.* FROM customers c
WHERE c.city = 'Bath'
  AND EXISTS (SELECT 1 FROM orders o
              WHERE o.customer_id = c.id);
```

```
Nested Loop Semi Join
  (actual rows=12500.00)
Execution Time: 10.958 ms
```

Four times faster: the semi-join stops at each customer's first order instead of producing all ten and de-duplicating. A `DISTINCT` you added to fix duplicates is a sign the query asks the wrong question.

## 8. OR across different columns

```sql
WHERE customer_id = 42
   OR ordered_on = '2025-01-01'
```

Both columns are indexed, so Postgres can build a `BitmapOr` of the two index scans: 0.35 ms. Change one side to an unindexed column:

```sql
WHERE customer_id = 42 OR total = 99.99
```

Now no index covers both alternatives, so the whole condition is a filter on a Seq Scan: 31 ms. One unindexed branch makes the entire OR non-sargable. Index both columns, or split the query into a `UNION` of two indexed queries.

## 9. N+1 queries

This one lives in application code, often generated by an ORM:

```python
customers = db.fetch(
    "SELECT id, name FROM customers"
    " WHERE city = %s", ["York"])
for c in customers:
    c.orders = db.fetch(
        "SELECT * FROM orders"
        " WHERE customer_id = %s", [c.id])
```

That's 1 query plus one per customer: 12,501 queries for York. Each query might take only 0.05 ms to run, but every one pays a network round trip, typically 0.1 to 1 ms within a data centre. At 0.5 ms each that's over 6 seconds of waiting, for data one query could return:

```python
rows = db.fetch(
    "SELECT * FROM orders"
    " WHERE customer_id = ANY(%s)",
    [[c.id for c in customers]])
```

Or use a JOIN. No EXPLAIN will show N+1 because each query is fast; you find it in `pg_stat_statements` (a cheap query with a huge `calls` count) or in application traces. ORMs have eager-loading options (`select_related` / `prefetch_related` in Django, `selectinload` in SQLAlchemy) to fix it.

## 10. Generic plans for skewed parameters

Prepared statements save planning time by reusing plans. Postgres plans the first five executions with the actual parameter values (**custom plans**), then switches to a single **generic plan** if its estimated cost isn't much worse than the custom plans' average. A generic plan can't know the parameter:

```sql
PREPARE p(text) AS
  SELECT count(*) FROM orders
  WHERE status = $1;
```

```
-- custom plan for 'pending':
Index Only Scan using orders_pending_idx
  (rows=30767)
-- generic plan:
Seq Scan on orders  (rows=333333)
  Filter: (status = $1)
```

The generic plan assumes the average value (1/3 of rows, with 3 distinct statuses) and can't use the partial index. If most calls ask for rare values, every call now scans the table. Fixes: `SET plan_cache_mode = force_custom_plan` for that session or role, or write separate statements for the rare and common cases.

## 11. Exact counts and SELECT *

`SELECT count(*) FROM orders` read every page: 48 ms here, minutes on a billion-row table. Postgres has no stored row count, because under MVCC different transactions may legitimately see different counts. If an estimate will do (a "~1.2M results" label), read `reltuples` from `pg_class`, or the row estimate from EXPLAIN.

`SELECT *` requests every output column. It prevents an index-only scan unless a suitable index covers all required columns, and wider results can increase memory and transfer costs, including fetching large TOASTed values. Name the columns you need.

## Myths

- **"CTEs are optimisation fences."** True before Postgres 12. Since 12, a non-recursive, side-effect-free SELECT CTE referenced once is normally inlined into the main query and optimised with it, unless you write `AS MATERIALIZED`.
- **"Always use a join instead of a subquery."** Section 6 showed a subquery beating a join. Read the plan.
- **"An index on every column is safe."** The previous lesson covered the write, cache and HOT costs.

## Key takeaways
- Keep predicates sargable: compare bare columns, with matching types, and rewrite functions as ranges or index the expression.
- Use keyset pagination instead of deep OFFSETs; OFFSET n reads and discards n rows.
- Prefer NOT EXISTS for exclusion by a matching row: it avoids the NULL trap and often permits an anti-join. Transformation still depends on query structure.
- Correlated subqueries are nested loops. They're fine with an index on the inner side; check `loops`.
- Replace "join plus DISTINCT" with EXISTS when you only need to know a match exists.
- N+1 queries and generic plans don't look slow in a single EXPLAIN; find them with pg_stat_statements and by testing with real parameter values.

## Further reading
- [Sargable — Wikipedia](https://en.wikipedia.org/wiki/Sargable)
- [Use The Index, Luke: functions in WHERE clauses](https://use-the-index-luke.com/sql/where-clause/functions)
- [Use The Index, Luke: paging through results without OFFSET](https://use-the-index-luke.com/no-offset)
- [Don't Do This — PostgreSQL wiki](https://wiki.postgresql.org/wiki/Don%27t_Do_This)
- [Subquery expressions (EXISTS, IN, NOT IN) — PostgreSQL docs](https://www.postgresql.org/docs/current/functions-subquery.html)
- [PREPARE and plan_cache_mode — PostgreSQL docs](https://www.postgresql.org/docs/current/sql-prepare.html)
- [Slow counting — PostgreSQL wiki](https://wiki.postgresql.org/wiki/Slow_Counting)
- [WITH queries (CTEs) — PostgreSQL docs](https://www.postgresql.org/docs/current/queries-with.html)
