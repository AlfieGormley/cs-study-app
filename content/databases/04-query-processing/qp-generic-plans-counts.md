---
id: qp-generic-plans-counts
title: Parameter plans, exact counts and CTEs
level: advanced
minutes: 4
sourceLesson: qp-anti-patterns
summary: How prepared statements choose between custom and generic plans, why skewed values can get a bad cached plan, and the cost of exact counts and SELECT *.
---

Examples use PostgreSQL 18 and the module's scaled-up shop tables (1,000,000 orders, 100,000 customers; the first lesson lists them). Plans are abbreviated and illustrative: real plans and timings depend on the data, statistics, settings, cache state and version. Assume serial execution.

## 10. Generic plans for skewed parameters

Prepared statements save planning time by reusing plans. In PostgreSQL 18's default `plan_cache_mode = auto`, a parameterised prepared statement normally starts with five executions planned using the actual parameter values (**custom plans**), then builds a **generic plan** that ignores the parameter's value. From then on it uses the generic plan if its estimated cost is lower than the custom plans' average estimated cost (which includes a charge for planning). Reuse is a cost decision, not a guaranteed switch on the sixth call.

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

The generic plan doesn't know the value, so it assumes an average one, as if every status were equally common: a third of the table, 333,333 rows. For a third of the table a sequential scan looks cheapest, and the plan cannot use the partial index on pending orders, because it cannot prove `$1` is 'pending'.

What happens next depends on the first five calls. In a PostgreSQL 18.6 test:

- **Five calls for 'pending'.** Each custom plan used the partial index and cost about 660 units, far below the generic plan's 20,833. PostgreSQL kept making custom plans; `pg_prepared_statements` showed 6 custom and 0 generic plans after the sixth call.
- **Five calls for 'shipped'** (90% of rows). Each custom plan was a full scan costing more than the generic plan, so from the sixth call PostgreSQL switched to the generic Seq Scan, and kept using it when a later call asked for 'pending'.

So the trap is a skewed column whose early calls use common values: they make the generic plan look acceptable, and rare values then inherit a full scan. The `generic_plans` and `custom_plans` columns of `pg_prepared_statements` show which kind a statement has been using. Fixes: `SET plan_cache_mode = force_custom_plan` for that session or role, or write separate statements for the rare and common cases.

> [!analogy] Real-world analogy: a standard delivery route
> A courier plans each of the first five deliveries individually. If those happen to be big drops to the main depot, a single standard route to the depot looks as good as custom planning, so the firm adopts it. When a small parcel later needs to go to a village, it still goes the long way via the depot.
>
> **How it maps:** individually planned deliveries are custom plans, and the standard route is the generic plan. Adopting the route because it compared well with the first few jobs is `plan_cache_mode = auto` comparing the generic plan's cost with the average custom plan. The village parcel is a rare parameter value served by a plan built for an average one.
>
> **Where it stops:** a courier would notice the odd parcel and replan; PostgreSQL does not look at the new value once it has settled on the generic plan, unless the plan is invalidated or the setting forces custom plans.

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

