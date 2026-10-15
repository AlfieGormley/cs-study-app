---
id: sql-join-chains-fanout
title: Trace join chains and multiplied child rows
level: basic
minutes: 5
sourceLesson: sql-joins
summary: A link table connects the two sides of a many-to-many relationship.
---

The examples continue the shop database introduced in the first unit. Customers are Asha (1, London), Ben (2, Leeds), Chloe (3, unknown city), Dev (4, London) and Erin (5, Bristol). Asha has orders 101 and 102, Ben 103, Chloe 104, Dev 105; guest order 106 has no customer, and Erin has no orders. 

## Joining through a link table

Orders and products have a many-to-many relationship, resolved by `order_items`. Getting product names for an order means two joins in a chain.

```sql
-- Follow Asha's orders to their product
-- lines.
SELECT o.id, p.name, i.qty
FROM orders o
JOIN order_items i ON i.order_id = o.id
JOIN products p ON p.id = i.product_id
WHERE o.customer_id = 1;
```

| id | name | qty |
|---|---|---|
| 101 | Kettle | 1 |
| 101 | Mug | 4 |
| 102 | Lamp | 2 |

Each join adds one table and one condition. Joins are associative for inner joins, so the database is free to execute them in any order it thinks is cheapest; how it chooses is the subject of the query processing module.

> [!warning] Mixing LEFT and INNER
> `customers LEFT JOIN orders ... JOIN order_items ...` drops Erin again. Her padded row has `o.id` NULL, so the inner join to `order_items` finds no match. Once a table is optional, every join that hangs off it usually needs to be a LEFT JOIN too.

## Fan-out: when joins multiply rows

For the examples below, `GROUP BY c.name` collects the joined rows for each customer name. `COUNT(o.id)` counts non-NULL order ids in that group; `COUNT(DISTINCT o.id)` counts each different known order id once. Names happen to be unique in this fixture; use the customer primary key for identity in real reporting. The aggregate units later explain these operations in depth.

Because a join produces one row per matching pair, joining a parent to a child repeats the parent once per child. That is fine until you aggregate.

```sql
-- Compare joined line count with order
-- count.
SELECT c.name,
       COUNT(o.id) AS n,
       COUNT(DISTINCT o.id) AS d
FROM customers c
JOIN orders o ON o.customer_id = c.id
JOIN order_items i ON i.order_id = o.id
GROUP BY c.name;
```

| name | n | d |
|---|---|---|
| Asha | 3 | 2 |
| Ben | 2 | 1 |
| Chloe | 2 | 1 |
| Dev | 1 | 1 |

Asha has two orders, but joining to items gives three rows (order 101 has two items). `COUNT(o.id)` says 3.

It gets worse when you join **two independent child tables** to the same parent. Asha has 2 orders and referred 2 customers. Neither child table says which order goes with which referral, so the join pairs every one with every other:

```formula
r = c_1 c_2
r = 2 × 2 = 4
where
r: the number of joined rows produced for one parent row (here Asha)
c_1: how many rows of the first child table match that parent (Asha's 2 orders)
c_2: how many rows of the second child table match it (her 2 referrals)
In words: joining two unrelated child tables to one parent multiplies their counts, so every aggregate over that parent sees each child row repeated once per row of the other child.
```

So both counts come out as 4. With three orders and four referrals it would be 12 rows. With an inner join, a parent with zero rows in either child gives 0 rows and disappears; with LEFT JOINs an unmatched child counts as one NULL-padded row instead.

```
Asha x orders(101,102)
     x referrals(Ben,Chloe)
= 4 rows: every order paired
  with every referral
```

Fixes, in order of preference:

1. Aggregate each child table separately (in a subquery or CTE), then join the one-row-per-parent results.
2. Use `COUNT(DISTINCT ...)` for counts. This does not work for `SUM`, because two different items can have the same value.

A useful habit: before trusting a total, ask "what is one row of this result?" If the answer is "one order item", a sum of order totals is wrong.

## Key takeaways
- A link table connects the two sides of a many-to-many relationship.
- An inner join hanging from an optional table can remove padded rows.
- Independent child relationships multiply rows; count or total the intended entity.

## Further reading
- [Table expressions and joined tables — PostgreSQL docs](https://www.postgresql.org/docs/current/queries-table-expressions.html)
- [Join (SQL) — Wikipedia](https://en.wikipedia.org/wiki/Join_(SQL))
