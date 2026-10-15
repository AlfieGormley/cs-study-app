---
id: sql-where-having
title: Filter source rows before filtering groups
level: intermediate
minutes: 3
sourceLesson: sql-group-by
summary: WHERE selects the rows that enter groups.
---

The examples continue the shop database introduced in the first unit. Customers are Asha (1, London), Ben (2, Leeds), Chloe (3, unknown city), Dev (4, London) and Erin (5, Bristol). Asha has orders 101 and 102, Ben 103, Chloe 104, Dev 105; guest order 106 has no customer, and Erin has no orders. 

## WHERE versus HAVING

Both filter, but at different moments:

- `WHERE` filters **rows** before grouping. It cannot use aggregates.
- `HAVING` filters **groups** after aggregation. It can.

Who spent more than £50 on orders that were not cancelled?

```sql
-- Exclude cancelled lines before totalling.
SELECT o.customer_id,
       SUM(oi.qty * p.price) AS spent
FROM orders o
JOIN order_items oi
  ON oi.order_id = o.id
JOIN products p
  ON p.id = oi.product_id
WHERE o.status <> 'cancelled'
GROUP BY o.customer_id
HAVING SUM(oi.qty * p.price) > 50;
```

| customer_id | spent |
|---|---|
| 1 | 142 |
| 3 | 70 |

Asha (1) spent 62 + 80. Chloe (3) spent 70. Ben's 41 fails the `HAVING`. Dev's only order was cancelled, so `WHERE` removed it before grouping and he never forms a group.

Recall the logical order from the SELECT units: FROM, WHERE, GROUP BY, HAVING, SELECT, ORDER BY, LIMIT. Two consequences:

1. Put row conditions in `WHERE` to state their intent clearly. Adding `status` to this query's `GROUP BY` changes its groups: a customer with both shipped and pending orders can produce two totals. It is not equivalent to filtering status before grouping by customer. The optimiser may also push eligible `HAVING` predicates down, so the logical order of clauses does not dictate execution cost.
2. `HAVING` runs before `SELECT`, so in PostgreSQL you must repeat the aggregate: `HAVING spent > 50` fails with `column "spent" does not exist`. SQLite accepts the alias. `ORDER BY spent` works in both.

## Key takeaways
- WHERE selects the rows that enter groups.
- HAVING selects groups from their aggregate results.
- In PostgreSQL repeat an aggregate in HAVING instead of its SELECT alias.

## Further reading
- [GROUP BY and HAVING — PostgreSQL documentation](https://www.postgresql.org/docs/current/queries-table-expressions.html)
