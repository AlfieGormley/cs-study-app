---
id: asql-scalar-subqueries
title: Scalar subqueries and the Advanced SQL fixture
level: basic
minutes: 4
summary: A scalar subquery supplies one value; zero rows becomes NULL.
sourceLesson: asql-subqueries
---

A **subquery** is a complete `SELECT` placed inside another statement. It lets you ask a question whose answer depends on another question: "which orders are bigger than the *average* order?" You can't write the average as a constant because you don't know it yet, so you compute it in a subquery.

Every lesson in this module uses the same small shop. Result tables show values for the stated data; only an explicit final ORDER BY guarantees row order.


## The shop schema

Schema notation (column names, not executable SQL):

```text
customers(id, name, city)
products(id, name, category, price)
orders(id, customer_id, ordered_on, total)
order_items(order_id, product_id, qty)
```

| id | name | city |
|---|---|---|
| 1 | Ana | London |
| 2 | Ben | Leeds |
| 3 | Cat | London |
| 4 | Dev | York |
| 5 | Eve | Leeds |

| id | cust | date | total |
|---|---|---|---|
| 101 | 1 | 01-05 | 120 |
| 102 | 2 | 01-09 | 45 |
| 103 | 1 | 02-11 | 60 |
| 104 | 3 | 02-14 | 200 |
| 105 | 4 | 02-20 | 45 |
| 106 | 2 | 03-02 | 90 |
| 107 | 1 | 03-15 | 60 |
| 108 | 3 | 03-28 | 30 |

Treat customers.id, products.id and orders.id as primary keys. orders.customer_id is NOT NULL and references customers.id. The displayed totals, prices and quantities are non-NULL integers; ordered_on is ISO date text in SQLite and a date in PostgreSQL. These declarations matter for the grouped queries and integer arithmetic that follow.

All dates are in 2026. Products are Kettle (30), Toaster (25), Mug (10) in *Kitchen*, and Lamp (40), Rug (90), Vase (35) in *Home*. Eve has never ordered, and nobody has bought a Vase. Those two gaps will matter.

## Where a subquery can go

A subquery's *shape* decides where it is allowed:

| Shape | Returns | Used in |
|---|---|---|
| Scalar | 0–1 rows, 1 col | `SELECT`, `WHERE`, `HAVING` |
| Column | Many rows, 1 col | `IN`, `ANY`, `ALL` |
| Table | Many rows and columns | `FROM` |
| Existence | anything | `EXISTS` |

### Scalar subqueries

```sql
-- Compare each total with the mean.
SELECT id, total
FROM orders
WHERE total > (SELECT AVG(total)
               FROM orders);
```

| id | total |
|---|---|
| 101 | 120 |
| 104 | 200 |
| 106 | 90 |

This uncorrelated aggregate can be evaluated once and reused. It yields the mean order total:

```formula
avg = (t_1 + t_2 + … + t_n) / n
avg = 650 / 8 = 81.25
where
avg: the mean (average) order total, what AVG(total) returns
t_1, t_2, t_n: the totals of the first, second and last order
…: and so on, for every order in between
n: the number of rows being averaged, here 8 orders
650: the sum of the 8 totals (120 + 45 + 60 + 200 + 45 + 90 + 60 + 30)
In words: add up every order total and divide by how many orders there are.
```

The outer query then compares each row with 81.25 and keeps 120, 200 and 90. AVG skips NULL totals, so the denominator counts only non-NULL values. This is an **uncorrelated** subquery: it doesn't mention the outer query at all, so the database can evaluate it once and reuse the value.

> [!warning] A "scalar" subquery that returns two rows
> If a scalar subquery returns more than one row, **PostgreSQL raises an error**: `more than one row returned by a subquery used as an expression`. **SQLite silently uses the first row** it happens to find. A query that "works" in SQLite can fail in production on Postgres, and the SQLite answer was arbitrary anyway.

## Key takeaways
- A scalar subquery supplies one value; zero rows becomes NULL.
- PostgreSQL rejects several scalar rows; SQLite takes the first, without a guaranteed order.

## Further reading
- [PostgreSQL 18: functions subquery](https://www.postgresql.org/docs/18/functions-subquery.html)
- [PostgreSQL 18: sql expressions](https://www.postgresql.org/docs/18/sql-expressions.html)
- [SQLite reference](https://www.sqlite.org/lang_expr.html)
