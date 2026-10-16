---
id: qp-generic-plans-counts
title: Parameter plans, exact counts and CTEs
level: advanced
minutes: 4
sourceLesson: qp-anti-patterns
summary: Parameter plans, exact counts and CTEs with worked examples and explicit assumptions.
---

These examples use PostgreSQL 18. SQL Fundamentals supplies the shop relations: `customers(id, name, email, city, country)`, `orders(id, customer_id, status, ordered_on, total)`, `products(id, price)` and `order_items(order_id)`. IDs join orders to customers and items to orders. Dates use `date`, IDs use `integer`, and totals use `numeric`. Each query fragment uses these names; ellipses and standalone WHERE clauses need the surrounding SELECT shown by their context.

All historical plan fragments and timings in this unit are **illustrative inputs**, not reproduced benchmarks or promises. Their row/page counts describe a hypothetical dataset; actual plans vary with statistics, indexes, settings, cache state and PostgreSQL version. Assume serial execution unless a parallel worker process is shown.

## 10. Generic plans for skewed parameters

Prepared statements save planning time by reusing plans. In PostgreSQL 18's default `plan_cache_mode = auto`, a parameterised prepared statement normally starts with five executions planned using the actual parameter values (**custom plans**), then compares a **generic plan** against the custom plans' average estimated cost including planning overhead. Reuse is a cost decision, not a guaranteed switch on the sixth call. A generic plan can't know the parameter:

```sql
-- The parameter may vary between calls.
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

The generic plan doesn't know the value, so it assumes an average one, as if every status were equally common:

```formula
s = 1 / n_distinct = 1 / 3
n_est = s × n_table
n_est = 1,000,000 / 3 ≈ 333,333
where
s: the selectivity the generic plan assumes for status = $1
n_distinct: the number of distinct values in the column, here 3 statuses
n_est: the estimated number of matching rows
n_table: the number of rows in the table, here 1,000,000
≈: approximately equal to
In words: without knowing the parameter, the planner expects a third of the table to match, so a sequential scan looks cheapest.
```

It also can't use the partial index, because it can't prove the parameter is 'pending'. If most calls ask for rare values, every call now scans the table. Fixes: `SET plan_cache_mode = force_custom_plan` for that session or role, or write separate statements for the rare and common cases.

## 11. Exact row counts and SELECT *

`SELECT count(*) FROM orders` read every page: 48 ms here, and larger tables require more work; no fixed time follows from a row count. Postgres has no stored row count, because under MVCC different transactions may legitimately see different counts. If an estimate will do (a "~1.2M results" label), read `reltuples` from `pg_class`, or the row estimate from EXPLAIN.

`SELECT *` requests every output column. It prevents an index-only scan unless a suitable index covers all required columns, and wider results can increase memory use and client transfer work, including fetching large TOASTed values. Name the columns you need.

## Myths

- **"CTEs are optimisation fences."** True before Postgres 12. Since 12, a non-recursive, side-effect-free SELECT CTE used only once in the query is normally inlined into the main query and optimised with it, unless you write `AS MATERIALIZED`.
- **"Always use a join instead of a subquery."** The earlier subquery unit showed a subquery beating a join. Read the plan.
- **"An index on every column is safe."** The previous lesson covered the write, cache and HOT costs.

## Key takeaways
- Default prepared-plan selection compares generic and custom estimated costs; a sixth-call switch is not guaranteed.
- An exact MVCC-visible count needs a scan; CTE inlining and output width depend on the query form.

## Further reading
- [Sargable — Wikipedia](https://en.wikipedia.org/wiki/Sargable)
- [Use The Index, Luke: functions in WHERE clauses](https://use-the-index-luke.com/sql/where-clause/functions)
- [Use The Index, Luke: paging through results without OFFSET](https://use-the-index-luke.com/no-offset)
- [Don't Do This — PostgreSQL wiki](https://wiki.postgresql.org/wiki/Don%27t_Do_This)
- [Subquery expressions (EXISTS, IN, NOT IN) — PostgreSQL docs](https://www.postgresql.org/docs/18/functions-subquery.html)
- [PREPARE and plan_cache_mode — PostgreSQL docs](https://www.postgresql.org/docs/18/sql-prepare.html)
- [Slow counting — PostgreSQL wiki](https://wiki.postgresql.org/wiki/Slow_Counting)
- [WITH queries (CTEs) — PostgreSQL docs](https://www.postgresql.org/docs/18/queries-with.html)

