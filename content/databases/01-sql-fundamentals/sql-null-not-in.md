---
id: sql-null-not-in
title: Avoid NULL poisoning in NOT IN
level: intermediate
minutes: 3
sourceLesson: sql-null
summary: A NULL in a nonempty scalar NOT IN list prevents a TRUE result.
---

The examples continue the shop database introduced in the first unit. Customers are Asha (1, London), Ben (2, Leeds), Chloe (3, unknown city), Dev (4, London) and Erin (5, Bristol). Asha has orders 101 and 102, Ben 103, Chloe 104, Dev 105; guest order 106 has no customer, and Erin has no orders. 

## The NOT IN trap

This query looks like "customers who have never ordered":

```sql
-- The guest customer_id poisons the list.
SELECT name FROM customers
WHERE id NOT IN (
  SELECT customer_id FROM orders);
```

It returns **no rows at all**, even though Erin has never ordered. The reason is the guest order's NULL `customer_id`. The subquery produces (1, 1, 2, 3, 4, NULL), and `x NOT IN (list)` expands to:

```
x <> 1 AND x <> 1 AND x <> 2
AND x <> 3 AND x <> 4 AND x <> NULL
```

For Erin (id 5), every comparison is TRUE except the last, which is UNKNOWN. `TRUE AND UNKNOWN` is UNKNOWN, so `WHERE` drops her. For everyone else one comparison is FALSE. An AND chain is only as true as its weakest term, so one NULL in the list means `NOT IN` can never be TRUE.

Positive matches with IN still work: `1 IN (1, NULL)` is TRUE. A nonmatch can still be UNKNOWN: `3 IN (1, NULL)` is UNKNOWN, rather than FALSE. The especially surprising loss of every row occurs when a NULL prevents a NOT IN result from becoming TRUE.

The empty-set case is different. If the subquery returns zero rows, IN is FALSE and NOT IN is TRUE, even for a NULL left operand. Both engines accept an empty subquery; PostgreSQL rejects the literal syntax `IN ()`, which SQLite accepts. Do not confuse an empty result with a one-row result containing NULL.

The fix is `NOT EXISTS`, which asks whether a matching row exists, a question that is always TRUE or FALSE:

```sql
-- Only a true matching pair defeats EXISTS.
SELECT name FROM customers c
WHERE NOT EXISTS (
  SELECT 1 FROM orders o
  WHERE o.customer_id = c.id);
-- Erin
```

The `LEFT JOIN ... WHERE o.id IS NULL` anti-join from the joins lesson also works. Adding `WHERE customer_id IS NOT NULL` to the subquery fixes `NOT IN` too, but it is easy to forget, and the bug only appears once the first NULL arrives in production. Prefer `NOT EXISTS` by habit. PostgreSQL's planner also handles `NOT EXISTS` well (as an anti-join), while it often can't turn `NOT IN` over a subquery into one, precisely because of these NULL rules.

## Key takeaways
- A NULL in a nonempty scalar NOT IN list prevents a TRUE result.
- NOT EXISTS asks whether any matching row exists.
- An empty subquery makes NOT IN true even for a NULL left operand.

## Further reading
- [Subquery expressions (NOT IN, EXISTS) — PostgreSQL documentation](https://www.postgresql.org/docs/current/functions-subquery.html)
