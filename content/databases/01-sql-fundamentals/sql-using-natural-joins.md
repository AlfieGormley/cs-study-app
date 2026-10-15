---
id: sql-using-natural-joins
title: Choose explicit join keys over NATURAL
level: basic
minutes: 3
sourceLesson: sql-joins
summary: USING joins identically named keys and merges their output column.
---

The examples continue the shop database introduced in the first unit. Customers are Asha (1, London), Ben (2, Leeds), Chloe (3, unknown city), Dev (4, London) and Erin (5, Bristol). Asha has orders 101 and 102, Ben 103, Chloe 104, Dev 105; guest order 106 has no customer, and Erin has no orders. 

## USING and NATURAL

When the join columns have the same name in both tables, `USING` is shorthand.

```sql
-- Give both join keys the name product_id.
-- Rename the key for an explicit USING.
CREATE VIEW products_v AS
SELECT id AS product_id, name, price,
       category
FROM products;

SELECT order_id, name, qty
FROM order_items
JOIN products_v USING (product_id);
```

For this inner join, `USING (product_id)` means `ON order_items.product_id = products_v.product_id`. A `SELECT *` result contains one merged `product_id` column instead of two. The explicit select list above chooses just order id, product name and quantity; it returns the nine order lines. A view is a named stored query, so `products_v` provides the same products with a renamed key.

This distinction matters when reading or changing a select list. `ON` retains both input key columns in `SELECT *`, whereas `USING` merges them. With an outer join, the merged key represents the preserved side's value; a FULL JOIN can take that value from either side. Prefer explicit output columns so callers do not depend on a layout that changes when a table gains a column.

The key being named alike is only a naming convenience. Verify that both columns represent the same relationship before choosing USING. Our order and customer tables both have `id`, but those ids identify different entities. The foreign key is `orders.customer_id`, so the correct join is `ON orders.customer_id = customers.id`.

`NATURAL JOIN` goes further and joins on **every** column name the two tables share. It is fragile. In our schema the only shared name between `customers` and `orders` is `id`, so `customers NATURAL JOIN orders` matches customer ids against order ids and returns **0 rows**, with no error. Adding a column like `created_at` to both tables later would silently change the meaning of every natural join. Prefer explicit `ON`.

## Choosing a join

| Question | Join |
|---|---|
| Rows with a match | INNER |
| All of A, B if any | LEFT |
| Matches and both leftovers | FULL |
| A with no B | LEFT + IS NULL |
| Every combination | CROSS |
| Row to row in one table | self |

## Key takeaways
- USING joins identically named keys and merges their output column.
- NATURAL JOIN uses every shared column name, even an unintended id.
- Choose the join type from the rows the result must preserve.

## Further reading
- [Table expressions and joined tables — PostgreSQL docs](https://www.postgresql.org/docs/current/queries-table-expressions.html)
- [SELECT — SQLite docs](https://www.sqlite.org/lang_select.html)
