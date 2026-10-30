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

All dates are in 2026. Products are Kettle (30), Toaster (25), Mug (10) in *Kitchen*, and Lamp (40), Rug (90), Vase (35) in *Home*. Their ids are Kettle 1, Toaster 2, Lamp 3, Rug 4, Mug 5 and Vase 6. Eve has never ordered, and nobody has bought a Vase. Those two gaps will matter.

The 13 order lines (`order_items`) give each order's contents; each order's lines add up to its total:

| order | lines (product × qty) |
|---|---|
| 101 | Kettle × 1, Rug × 1 |
| 102 | Toaster × 1, Mug × 2 |
| 103 | Kettle × 2 |
| 104 | Rug × 2, Mug × 2 |
| 105 | Toaster × 1, Mug × 2 |
| 106 | Rug × 1 |
| 107 | Lamp × 1, Mug × 2 |
| 108 | Kettle × 1 |

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

The eight totals add up to 650, so `AVG(total)` is 81.25. The outer query compares each row with 81.25 and keeps 120, 200 and 90. AVG skips NULL values, so a row with a missing total would count in neither the sum nor the divisor.

This is an **uncorrelated** subquery: it doesn't mention the outer query at all, so its value is the same for every row and the database can evaluate it once and reuse it.

A scalar subquery that returns **no rows** is not an error: its value is NULL. A comparison such as `total > NULL` is UNKNOWN, so a WHERE clause would then keep no rows.

> [!warning] A "scalar" subquery that returns two rows
> If a scalar subquery returns more than one row, **PostgreSQL raises an error**: `more than one row returned by a subquery used as an expression`. **SQLite silently uses the first row** it happens to find. A query that "works" in SQLite can fail in production on Postgres, and the SQLite answer was arbitrary anyway.

## Key takeaways
- A scalar subquery supplies one value; zero rows becomes NULL.
- PostgreSQL rejects several scalar rows; SQLite takes the first, without a guaranteed order.

## Further reading
- [PostgreSQL 18: functions subquery](https://www.postgresql.org/docs/18/functions-subquery.html)
- [PostgreSQL 18: sql expressions](https://www.postgresql.org/docs/18/sql-expressions.html)
- [SQLite reference](https://www.sqlite.org/lang_expr.html)
