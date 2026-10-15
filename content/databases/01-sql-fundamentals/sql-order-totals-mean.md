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

This lesson uses the same shop schema as the rest of the module. An order's total is worked out from its lines in `order_items`: multiply each line's quantity by its product's price, then add the lines up.

```formula
T = Σ (q_i p_i)
T_101 = 1 × 30 + 4 × 8
T_101 = 30 + 32 = £62
where
T: the total value of one order, in pounds (£)
Σ: sigma, "the sum of": add up the bracketed value for every line i of the order
i: one line of the order, a row of order_items
q_i: the quantity on line i, a whole number of items
p_i: the price of line i's product, in pounds (£)
T_101: the total of order 101, which has 1 Kettle at £30 and 4 Mugs at £8
In words: an order's value is each line's quantity times its price, added up over all the order's lines.
```

The same sum in SQL is `SUM(oi.qty * p.price)` grouped by order. The totals come out as 101 = £62, 102 = £80, 103 = £41, 104 = £70, 105 = £25 and 106 = £8.

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

`SUM` adds the values, `MIN` and `MAX` pick the smallest and largest, and `AVG` is the ordinary mean: the sum divided by how many values there are.

```formula
mean = (x_1 + x_2 + … + x_n) / n
mean = (30 + 25 + 40 + 90 + 8) / 5
mean = 193 / 5 = £38.6
where
mean: the arithmetic mean, which is what AVG returns, in pounds (£) here
x_1, x_2, x_n: the values being averaged, here the five prices in pounds (£)
…: "and so on": every value between x_2 and x_n is included too
n: how many values there are; NULLs are left out of both the sum and n (the NULL units)
In words: the average is the total divided by the number of values, so £38.6 is what each product would cost if the £193 were shared out equally.
```

## Key takeaways
- An order total adds each quantity times its product price.
- SUM, MIN, MAX and AVG reduce a whole input to a summary row.
- AVG shares the total across the known input values.

## Further reading
- [Aggregate functions — PostgreSQL documentation](https://www.postgresql.org/docs/current/functions-aggregate.html)
- [Built-in aggregate functions — SQLite documentation](https://www.sqlite.org/lang_aggfunc.html)
