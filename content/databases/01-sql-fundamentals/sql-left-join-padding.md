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

You can predict how many rows a LEFT JOIN returns from two counts: the matching pairs, which are exactly the rows the inner join gave, plus one padded row for each left row that matched nothing.

```formula
n_left = m + u_L
n_left = 5 + 1 = 6
where
n_left: the number of rows the LEFT JOIN returns
m: the number of matching pairs, the same as the row count of the INNER JOIN with the same ON condition (5 here)
u_L: the number of left-table rows that match no right-table row; each appears once, padded with NULLs (here 1, Erin)
In words: a LEFT JOIN returns every inner-join row plus one extra row for each unmatched left row, so it can never return fewer rows than the inner join.
```

Unmatched rows of the right table (guest order 106) add nothing, because a LEFT JOIN doesn't preserve them.

## Key takeaways
- LEFT JOIN preserves every left row.
- Unmatched right-hand columns are filled with NULL.
- The result contains matching pairs plus one row per unmatched left row.

## Further reading
- [Joins between tables — PostgreSQL tutorial](https://www.postgresql.org/docs/current/tutorial-join.html)
- [Table expressions and joined tables — PostgreSQL docs](https://www.postgresql.org/docs/current/queries-table-expressions.html)
