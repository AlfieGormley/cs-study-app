---
id: asql-membership-derived-tables
title: Membership tests and derived tables
level: basic
minutes: 3
summary: IN keeps a row of the enclosing query at most once, regardless of matching duplicates.
sourceLesson: asql-subqueries
---

Use the Advanced SQL fixture introduced in Scalar subqueries: customers Ana, Ben, Cat, Dev and Eve; orders total 650. Ana spends 240, Ben 135, Cat 230 and Dev 45. Eve has no orders. London contains Ana and Cat; Leeds contains Ben and Eve; York contains Dev.

### IN with a column subquery

Customers who have bought a Rug (product 4):

```sql
-- Match members without repeating them.
SELECT name FROM customers
WHERE id IN (
  SELECT o.customer_id
  FROM orders o
  JOIN order_items i
    ON i.order_id = o.id
  WHERE i.product_id = 4);
```

The result is Ana, Ben and Cat. Each has one Rug order line in the Advanced SQL fixture, so a plain join happens to return the same three customers. IN is a **semi-join**: it keeps each outer customer row at most once even if there are several matching lines. For example, switching the product to Kettle (id 1) finds Ana in orders 101 and 103; IN still returns her once, while the corresponding join returns her twice.

### Derived tables in FROM

A subquery in `FROM` acts like a temporary table. Average spend per customer, by city:

```sql
-- Average totals for ordering customers.
SELECT city, AVG(spend) AS avg_spend
FROM (
  SELECT c.city, c.id,
         SUM(o.total) AS spend
  FROM customers c
  JOIN orders o
    ON o.customer_id = c.id
  GROUP BY c.id
) AS per_cust
GROUP BY city;
```

| city | avg_spend |
|---|---|
| Leeds | 135.0 |
| London | 235.0 |
| York | 45.0 |

London's figure, for example, averages Ana's and Cat's spend. Eve has no orders, so the inner join drops her and Leeds averages Ben alone:

```formula
spend_c = Σ t_k for k = 1 to m
avg_London = (240 + 230) / 2 = 235
avg_Leeds = 135 / 1 = 135
where
spend_c: the total spend of customer c, the inner query's SUM(o.total)
c: one customer
t_k: the total of that customer's k-th order
k: a counter over the customer's orders, 1, 2, …, m
m: how many orders customer c has
Σ: sigma, "add up" the term after it for every value of k listed
avg_London, avg_Leeds: the outer query's AVG(spend) for that city's customers
240, 230: Ana's spend (120 + 60 + 60) and Cat's spend (200 + 30)
In words: first total each customer's orders, then average those per-customer totals within each city.
```

You need two levels of aggregation (sum per customer, then average per city), and SQL does not let you nest aggregates like `AVG(SUM(...))` directly. A derived table is the classic fix. The later CTE units show a named version of the same two-stage calculation.

Postgres before version 16 required the alias (`AS per_cust`); SQLite and Postgres 16+ accept it without one. Always alias anyway.

## Key takeaways
- IN keeps a row of the enclosing query at most once, regardless of matching duplicates.
- A derived table separates aggregation per customer from aggregation per city.

## Further reading
- [PostgreSQL 18: functions subquery](https://www.postgresql.org/docs/18/functions-subquery.html)
- [PostgreSQL 18: sql expressions](https://www.postgresql.org/docs/18/sql-expressions.html)
- [SQLite reference](https://www.sqlite.org/lang_expr.html)
