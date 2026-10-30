---
id: asql-quantified-comparisons
title: ANY, ALL and empty subqueries
level: basic
minutes: 3
summary: ALL over an empty subquery is TRUE; ANY over it is FALSE.
sourceLesson: asql-subqueries
---

The shop has six products and eight non-NULL order totals. Ana, customer 1, ordered totals 120, 60 and 60. Order 104 totals 200. There are no Garden products.

## ANY, ALL and row values

PostgreSQL supports quantified comparisons. Orders bigger than *every* one of Ana's:

```sql
-- Compare against all of Ana's totals.
SELECT id FROM orders
WHERE total > ALL (
  SELECT total FROM orders
  WHERE customer_id = 1);
-- 104 (200 beats 120, 60, 60)
```

The two quantifiers read like English:

- `x > ALL (subquery)` passes only if x is greater than **every** value the subquery returns.
- `x > ANY (subquery)` passes if x is greater than **at least one** of them.

Order 104 (200) beats all three of Ana's totals, so it is the only result. If the subquery returns no rows, there is no value for ALL to fail against, so `> ALL` is TRUE for every row of the outer query (it is *vacuously* true), while `> ANY` has nothing to beat and is FALSE.

`= ANY (...)` is the same as `IN`. **SQLite does not support `ANY`/`ALL`**; for a nonempty set of non-NULL values, `> (SELECT MAX(...))` gives the same result as `> ALL (...)`. NULLs also matter: MAX ignores them, while a NULL among the ALL values makes a comparison that would otherwise pass UNKNOWN (PostgreSQL 18: `5 > ALL` of 1 and NULL is NULL). Watch the empty-set edge case: `> ALL` of an empty set is TRUE, whereas comparing with `MAX` of an empty set gives NULL, which filters everything out.

Both databases accept row-value comparisons such as `WHERE (id, city) IN (SELECT ...)`.

## Key takeaways
- ALL over an empty subquery is TRUE; ANY over it is FALSE.
- Replacing ALL by MAX also changes NULL behaviour.

## Further reading
- [PostgreSQL 18: functions subquery](https://www.postgresql.org/docs/18/functions-subquery.html)
- [PostgreSQL 18: sql expressions](https://www.postgresql.org/docs/18/sql-expressions.html)
- [SQLite reference](https://www.sqlite.org/lang_expr.html)
