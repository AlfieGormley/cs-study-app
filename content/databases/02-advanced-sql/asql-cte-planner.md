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

> [!analogy] Real-world analogy: a sauce made to order or batch-cooked
> A recipe step says "make the tomato sauce". A cook can make just the portion each dish needs, or batch-cook a whole pot first and ladle from it.
>
> **How it maps:** Inlining is making the sauce as part of the dish: the outer query's filter (only one diner's order) shapes how much work is done, so an index can find just the needed rows. Materialising is the batch pot: the CTE result is computed once into a temporary result and every reference reads from it, which pays off when several dishes use it.
>
> **Where it stops:** A cook decides by experience; the database follows version-specific rules and planner estimates, and you can override them with `MATERIALIZED` or `NOT MATERIALIZED`. A PostgreSQL materialised CTE is also read on demand, so a consumer that stops early may not compute the whole pot.

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
