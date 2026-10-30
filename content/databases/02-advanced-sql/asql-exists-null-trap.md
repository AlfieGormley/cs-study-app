---
id: asql-exists-null-trap
title: EXISTS and the NOT IN NULL trap
level: basic
minutes: 3
summary: NOT EXISTS keeps rows of the enclosing query without a match and tolerates nullable inner keys.
sourceLesson: asql-subqueries
---

The shop customer ids are Ana 1, Ben 2, Cat 3, Dev 4 and Eve 5. Only Eve has no orders. The orders table has eight rows, and customer_id is NOT NULL in the Advanced SQL fixture.

## EXISTS and NOT EXISTS

`EXISTS (subquery)` is true if the subquery returns at least one row. What it selects is irrelevant, so `SELECT 1` is the convention.

Customers who have never ordered:

```sql
-- Keep customers with no matching order.
SELECT c.name
FROM customers c
WHERE NOT EXISTS (
  SELECT 1 FROM orders o
  WHERE o.customer_id = c.id);
```

Result: Eve. The same pattern on `products` and `order_items` finds Vase. This is an **anti-join**: keep rows of the enclosing query with *no* match.

## The NOT IN trap

`NOT IN` looks like it should be the same as `NOT EXISTS`. It isn't, because of NULL.

```sql
-- Keep customers with no matching order.
SELECT name FROM customers
WHERE id NOT IN (2, 3, NULL);
-- returns no rows at all
```

Work through it for Ana (id 1). `1 NOT IN (2, 3, NULL)` means `1 <> 2 AND 1 <> 3 AND 1 <> NULL`. The last term is UNKNOWN, and `TRUE AND UNKNOWN` is UNKNOWN. `WHERE` keeps only TRUE rows, so Ana is dropped. So is everyone else.

> [!analogy] Real-world analogy: a banned list with one unreadable entry
> A door supervisor admits only guests they can confirm are *not* on a banned list. One entry on the list is smudged and unreadable. For any guest who isn't clearly on the list, the honest answer becomes "I can't tell", so nobody gets in.
>
> **How it maps:** `NOT IN` asks "is this id different from every value in the list?" The NULL is the smudged entry: `id <> NULL` is UNKNOWN, so the combined answer is never TRUE, and WHERE admits only TRUE. `NOT EXISTS` instead looks for a matching row; a NULL simply fails to match, so it never blocks anyone.
>
> **Where it stops:** UNKNOWN follows fixed rules of SQL's three-valued logic, not real uncertainty about reading the list: a NULL is never "possibly 4". The analogy also explains only the negative test; with plain `IN`, a definite match is still TRUE, as described below.

In real code the NULL arrives through a subquery: `WHERE id NOT IN (SELECT referrer_id FROM ...)` where one row has a NULL `referrer_id`. The query silently returns nothing.

> [!tip] Prefer NOT EXISTS
> `NOT EXISTS` compares row by row with `=` inside the subquery, and a NULL there simply fails to match. It does not make unrelated nonmatches UNKNOWN. If you use `NOT IN`, filter NULLs from its subquery and decide how a nullable outer key should behave: filtering the subquery result alone does not make NULL outer values match NOT EXISTS semantics.

`IN` with a NULL in the list still gives UNKNOWN for nonmatching values; in this positive WHERE filter that does not change which rows survive: `id IN (2, 3, NULL)` still returns Ben and Cat, because `OR` with one TRUE term is TRUE.

## Key takeaways
- NOT EXISTS keeps rows of the enclosing query without a match and tolerates nullable inner keys.
- A NULL in a NOT IN list prevents any nonmatching value from becoming TRUE.

## Further reading
- [PostgreSQL 18: functions subquery](https://www.postgresql.org/docs/18/functions-subquery.html)
- [PostgreSQL 18: sql expressions](https://www.postgresql.org/docs/18/sql-expressions.html)
- [SQLite reference](https://www.sqlite.org/lang_expr.html)
