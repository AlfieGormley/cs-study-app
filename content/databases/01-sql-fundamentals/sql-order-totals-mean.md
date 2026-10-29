---
id: sql-order-totals-mean
title: Compute order totals and mean product prices
level: intermediate
minutes: 3
sourceLesson: sql-group-by
summary: An order total adds each quantity times its product price.
---

The examples continue the shop database introduced in the first unit. Customers are Asha (1, London), Ben (2, Leeds), Chloe (3, unknown city), Dev (4, London) and Erin (5, Bristol). Asha has orders 101 and 102, Ben 103, Chloe 104, Dev 105; guest order 106 has no customer, and Erin has no orders. 

Most business questions are about totals, not individual rows. How many orders are pending? What has each customer spent? Which category earns the most? **Aggregate functions** collapse many rows into one value, and `GROUP BY` decides which rows get collapsed together.

This lesson uses the same shop schema as the rest of the module. An order's total is worked out from its lines in `order_items`: multiply each line's quantity by its product's price, then add the lines up. Order 101 is one £30 Kettle plus four £8 Mugs, so £30 + £32 = £62.

```sql
-- One total per order: quantity times
-- price, added over the order's lines.
SELECT oi.order_id,
       SUM(oi.qty * p.price) AS total
FROM order_items oi
JOIN products p
  ON p.id = oi.product_id
GROUP BY oi.order_id;
```

`GROUP BY oi.order_id` makes one result row per order; later units explain grouping in detail. The totals come out as 101 = £62, 102 = £80, 103 = £41, 104 = £70, 105 = £25 and 106 = £8. The multiplication happens inside `SUM`, once per line. Writing `SUM(p.price)` instead would add each product's price once and ignore the quantity, giving £38 for order 101.

## Aggregates over the whole table

With no `GROUP BY` or `HAVING` filter, an aggregate treats the whole filtered table as one group and returns exactly one row:

```sql
-- Reduce all five prices to one summary
-- row.
SELECT SUM(price), MIN(price),
       MAX(price), AVG(price)
FROM products;
```

| SUM | MIN | MAX | AVG |
|---|---|---|---|
| 193 | 8 | 90 | 38.6 |

`SUM` adds the values, `MIN` and `MAX` pick the smallest and largest, and `AVG` is the ordinary mean: the sum divided by how many values there are. Here that is £193 shared across five products, £38.60 each. NULL inputs are left out of both the sum and the count, which the NULL units explore.

## Key takeaways
- An order total adds each quantity times its product price.
- SUM, MIN, MAX and AVG reduce a whole input to a summary row.
- AVG shares the total across the known input values.

## Further reading
- [Aggregate functions — PostgreSQL documentation](https://www.postgresql.org/docs/current/functions-aggregate.html)
- [Built-in aggregate functions — SQLite documentation](https://www.sqlite.org/lang_aggfunc.html)
