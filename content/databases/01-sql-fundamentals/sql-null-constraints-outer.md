---
id: sql-null-constraints-outer
title: Trace NULL through constraints and outer joins
level: intermediate
minutes: 3
sourceLesson: sql-null
summary: CHECK rejects FALSE but permits UNKNOWN; add NOT NULL when required.
---

The examples continue the shop database introduced in the first unit. Customers are Asha (1, London), Ben (2, Leeds), Chloe (3, unknown city), Dev (4, London) and Erin (5, Bristol). Asha has orders 101 and 102, Ben 103, Chloe 104, Dev 105; guest order 106 has no customer, and Erin has no orders. 

## NULL in constraints

Constraints also lean towards letting NULL through.

**UNIQUE** allows many NULLs. Two rows with a NULL email don't violate `email UNIQUE`, because neither is known to equal the other. Both SQLite and PostgreSQL behave this way by default. PostgreSQL 15 added `UNIQUE NULLS NOT DISTINCT` for when you want at most one NULL.

**CHECK** fails only when the condition is FALSE. With `age INTEGER CHECK (age >= 18)`, inserting age 10 fails, but inserting NULL succeeds, because `NULL >= 18` is UNKNOWN, not FALSE. Add `NOT NULL` when the value is required:

```sql
-- Column definition inside CREATE TABLE.
age INTEGER NOT NULL
    CHECK (age >= 18)
```

This asymmetry, where WHERE rejects UNKNOWN but CHECK accepts it, catches people out. Both follow the same principle: only reject on evidence.

## NULLs from outer joins

A `LEFT JOIN` fills unmatched right-hand columns with NULL. Filtering on those columns in `WHERE` quietly turns the outer join back into an inner one:

```sql
-- This WHERE removes unmatched referrers.
SELECT c.name, r.name AS ref
FROM customers c
LEFT JOIN customers r
  ON r.id = c.referred_by
WHERE r.city <> 'Leeds';
```

| name | ref |
|---|---|
| Ben | Asha |
| Chloe | Asha |

Asha and Erin have no referrer, so `r.city` is NULL, the test is UNKNOWN and they vanish. Dev's referrer is Ben, from Leeds. If you meant "keep everyone, but only show referrers outside Leeds", move `r.city <> 'Leeds'` into `ON`. Replacing the `WHERE` condition with `r.city IS DISTINCT FROM 'Leeds'` keeps unmatched rows but still removes Dev, whose referrer is in Leeds; it does not preserve everyone.

## Design advice

- Use `NOT NULL` by default and allow NULL only where "unknown" or "not applicable" is a real state. Every nullable column makes every query on it harder to reason about.
- Don't invent stand-in values such as `''`, `0` or `1900-01-01` for unknown. They take part in comparisons and aggregates as if they were real.
- When a column is nullable, ask for each query: what happens to the NULL rows here?

## Key takeaways
- CHECK rejects FALSE but permits UNKNOWN; add NOT NULL when required.
- Default UNIQUE rules permit multiple NULLs in SQLite and PostgreSQL.
- Move a referrer eligibility test into ON to retain every customer.

## Further reading
- [Constraints — PostgreSQL documentation](https://www.postgresql.org/docs/current/ddl-constraints.html)
- [Null (SQL) — Wikipedia](https://en.wikipedia.org/wiki/Null_(SQL))
- [Comparison functions and operators — PostgreSQL documentation](https://www.postgresql.org/docs/current/functions-comparison.html)
- [NULL handling in SQLite versus other database engines](https://www.sqlite.org/nulls.html)
