---
id: asql-cte-planner
title: CTE inlining and materialisation
level: intermediate
minutes: 3
summary: PostgreSQL 12+ normally folds eligible once-referenced SELECT CTEs.
sourceLesson: asql-ctes
---

A common table expression (CTE) is a subquery named by WITH for one statement. Naming it does not alone tell you how much of its output the database computes or stores.

## Inlined or materialised?

A CTE can be executed two ways:

- **Inlined**: substituted into the outer query like a derived table, so the optimiser can push filters into it and use indexes.
- **Materialised**: computed once into a temporary result, then read from there. Good if it is expensive and used many times; bad if the outer query only needs a few rows of a huge result.

The rules differ by database and version:

| Database | Default |
|---|---|
| Postgres 11 and earlier | No SELECT CTE folding |
| Postgres 12+ | Eligible non-recursive, side-effect-free SELECT CTEs: inlined if referenced once, otherwise materialised by default |
| SQLite | Planner's choice |

Both Postgres 12+ and SQLite 3.35+ accept `WITH x AS MATERIALIZED (...)` or `AS NOT MATERIALIZED (...)`. PostgreSQL ignores NOT MATERIALIZED for recursive or side-effecting CTEs, including SELECTs with volatile functions. SQLite treats these as planner hints; NOT MATERIALIZED does not forbid materialisation.

The old Postgres behaviour was famous as an **optimisation fence**. For this query the outer filter cannot restrict the base scan, so it reads every order while filtering the CTE output:

```sql
-- Outer filtering may be pushed inside.
WITH o AS (SELECT * FROM orders)
SELECT * FROM o WHERE id = 104;
```

Before version 12, the `id = 104` filter couldn't reach the index on `orders.id`. People deliberately used CTEs as fences to stop the planner from making a bad choice; since 12 you need `MATERIALIZED` to get that effect.

Postgres never inlines CTEs that are recursive or that have side effects (data-modifying CTEs, below).

## Key takeaways
- PostgreSQL 12+ normally folds eligible once-referenced SELECT CTEs.
- SQLite NOT MATERIALIZED is a hint and does not forbid materialisation.

## Further reading
- [PostgreSQL 18: queries with](https://www.postgresql.org/docs/18/queries-with.html)
- [SQLite reference](https://www.sqlite.org/lang_with.html)
