---
id: asql-subquery-plans
title: Subquery plans and hash memory
level: basic
minutes: 3
summary: Subquery meaning constrains rewrites; EXPLAIN reveals the chosen plan.
sourceLesson: asql-subqueries
---

A semi-join keeps a row of the enclosing query with at least one match; an anti-join keeps one with no match. These describe result semantics, while an execution plan describes how the database obtains those rows.

## How databases actually run them

"Re-evaluated for every row of the enclosing query" is the *meaning*, not necessarily the *plan*. Optimisers rewrite subqueries into joins whenever the semantics allow. These are possible PostgreSQL plan shapes, not a guarantee for this small dataset:

| Query form | Postgres plan |
|---|---|
| `IN (subquery)` | Hash (semi) join |
| `NOT EXISTS` | Hash anti join |
| `NOT IN (subquery)` | Hashed SubPlan |
| Correlated scalar | SubPlan per row |

The interesting row is `NOT IN`. Because of the NULL semantics above, PostgreSQL 18 generally keeps this nullable form as a SubPlan rather than an ordinary anti-join. When the subquery result is small it builds a hash table of it (a "hashed SubPlan"). The memory a hash table may use is set by two configuration settings:

```formula
B = work_mem × hash_mem_multiplier
B = 4 MB × 2.0 = 8 MB
where
B: the hash-memory budget: how much memory one hash-based operation may use; a hashed SubPlan must fit its estimate rather than spilling like a hash join
work_mem: the per-operation memory setting for sorts and hash tables; the default is 4 MB
hash_mem_multiplier: how many times work_mem a hash-based operation may use; the default is 2.0 since PostgreSQL 15 (it was 1.0 in 13 and 14)
MB: megabyte; in PostgreSQL settings 1 MB = 1024 × 1024 = 1,048,576 bytes
In words: a hash table may use work_mem multiplied by hash_mem_multiplier, which with default settings is 8 MB.
```

If the planner estimates that the hashed subquery will exceed this budget, it uses a plain SubPlan that rescans the subquery for each row of the enclosing query, which can be catastrophically slow on large tables. That is a second reason to prefer `NOT EXISTS`.

A correlated scalar subquery in `SELECT` typically runs as a SubPlan once per row of the enclosing query. An index on `orders(customer_id)` can make each probe cheap. Many rows of the enclosing query can make repeated probes expensive; a single GROUP BY and join may then be cheaper. Compare actual plans and preserve missing matches and NULLs rather than using a fixed row-count threshold.

> [!note] Which form should you write?
> Write whichever form states the question most clearly, then check the plan with `EXPLAIN`. `EXISTS` and `IN` can use semi-joins; an ordinary join can return duplicates and need a different plan. Investigate expensive `NOT IN` and per-row scalar subqueries, preserving their intended NULL and duplicate semantics when rewriting.

## Key takeaways
- Subquery meaning constrains rewrites; EXPLAIN reveals the chosen plan.
- In PostgreSQL 18 a large NOT IN subquery can use a repeatedly scanned SubPlan.

## Further reading
- [PostgreSQL 18: functions subquery](https://www.postgresql.org/docs/18/functions-subquery.html)
- [PostgreSQL 18: sql expressions](https://www.postgresql.org/docs/18/sql-expressions.html)
- [SQLite reference](https://www.sqlite.org/lang_expr.html)
