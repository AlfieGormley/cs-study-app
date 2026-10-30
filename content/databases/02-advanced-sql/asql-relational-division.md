---
id: asql-relational-division
title: Relational division: requiring every match
level: advanced
minutes: 3
summary: COUNT(DISTINCT ...) avoids counting repeat purchases as new required products.
sourceLesson: asql-interview-problems
---

The shop has customers, orders, order_items and products. Kettle and Mug are product names. Ana bought Kettle twice and Mug once; Cat bought both. Ben bought Mug but no Kettle.

## 3. Relational division: "all of"

"Customers who bought **both** Kettle and Mug." A `WHERE name = 'Kettle' AND name = 'Mug'` can never be true on one row. Filter to the candidates, group, and count:

```sql
-- Count covered required products.
SELECT c.name
FROM customers c
JOIN orders o
  ON o.customer_id = c.id
JOIN order_items i
  ON i.order_id = o.id
JOIN products p
  ON p.id = i.product_id
WHERE p.name IN ('Kettle', 'Mug')
GROUP BY c.id
HAVING COUNT(DISTINCT p.name) = 2;
-- Ana, Cat
```

The `WHERE p.name IN (…)` filter keeps only lines for required products, and `COUNT(DISTINCT p.name) = 2` checks that the number of different required products a customer bought equals the number required, which means they bought all of them.

> [!analogy] Real-world analogy: a stamp card that needs every stamp
> A coffee-shop offer gives a prize for a card with a stamp from each of two branches. Two stamps from the same branch do not complete it.
>
> **How it maps:** The required branches are the required products. Each order line is a stamp. `COUNT(DISTINCT p.name)` counts different branches stamped, so repeat visits to one branch do not count twice; the card is complete when that count equals the number of branches required.
>
> **Where it stops:** A stamp card has a fixed list printed on it. In SQL the "2" must match the required list, so if the list changes or is supplied from another table, compare with its count rather than a hard-coded number, and decide what an empty list should mean.

`DISTINCT` matters: Ana bought Kettle in two different orders, so a plain `COUNT` gives her 3 and wrongly excludes her. Worse, a customer who bought Kettle twice and no Mug would count 2 and wrongly pass.

The same shape answers "customers who ordered in **every** month that had orders" (SQLite's `strftime`; PostgreSQL would use `to_char(ordered_on, 'YYYY-MM')`):

```sql
-- Count covered required products.
SELECT c.name
FROM customers c
JOIN orders o
  ON o.customer_id = c.id
GROUP BY c.id
HAVING COUNT(DISTINCT
  strftime('%Y-%m', o.ordered_on))
  = (SELECT COUNT(DISTINCT
       strftime('%Y-%m', ordered_on))
     FROM orders);
-- Ana
```

The textbook alternative is a double `NOT EXISTS` ("there's no month in which this customer has no order"). The counting version returns only customers represented by the inner join. If there are no required months, it returns nobody, whereas double NOT EXISTS returns every customer (the empty requirement is vacuously satisfied). Choose the intended empty-set behaviour.

## Key takeaways
- COUNT(DISTINCT ...) avoids counting repeat purchases as new required products.
- An empty requirement needs an explicit business rule.

## Further reading
- [PostgreSQL 18: sql select](https://www.postgresql.org/docs/18/sql-select.html)
- [PostgreSQL 18: functions aggregate](https://www.postgresql.org/docs/18/functions-aggregate.html)
- [SQLite reference](https://www.sqlite.org/windowfunctions.html)
