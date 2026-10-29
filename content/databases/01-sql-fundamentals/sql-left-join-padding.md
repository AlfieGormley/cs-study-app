---
id: sql-left-join-padding
title: Keep customers with no matching order
level: basic
minutes: 3
sourceLesson: sql-joins
summary: LEFT JOIN preserves every left row.
---

In the shop, customers Asha, Ben, Chloe, Dev and Erin have ids 1–5. Orders 101 and 102 belong to Asha, 103 to Ben, 104 to Chloe and 105 to Dev. Guest order 106 has customer_id NULL; Erin has no order.

## LEFT JOIN: keep everything on the left

```sql
-- Keep Erin even though she has no order.
SELECT c.name, o.id
FROM customers c
LEFT JOIN orders o
  ON o.customer_id = c.id;
```

| name | id |
|---|---|
| Asha | 101 |
| Asha | 102 |
| Ben | 103 |
| Chloe | 104 |
| Dev | 105 |
| Erin | NULL |

A **LEFT (OUTER) JOIN** keeps every row of the left table. If a left row has no partner, it appears once with NULLs in all the right table's columns. Erin is back, with `id` NULL.

This is the join for questions like "all customers, with their orders if any". It is by far the most common outer join.

You can predict how many rows a LEFT JOIN returns: every row the inner join gave, plus one padded row for each left row that matched nothing. Here that is the 5 matching pairs plus Erin's padded row, 6 rows. So a LEFT JOIN never returns fewer rows than the inner join with the same `ON` condition.

Unmatched rows of the right table (guest order 106) add nothing, because a LEFT JOIN doesn't preserve them.

## Key takeaways
- LEFT JOIN preserves every left row.
- Unmatched right-hand columns are filled with NULL.
- The result contains matching pairs plus one row per unmatched left row.

## Further reading
- [Joins between tables — PostgreSQL tutorial](https://www.postgresql.org/docs/current/tutorial-join.html)
- [Table expressions and joined tables — PostgreSQL docs](https://www.postgresql.org/docs/current/queries-table-expressions.html)
