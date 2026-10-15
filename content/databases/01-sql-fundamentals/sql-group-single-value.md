---
id: sql-group-single-value
title: Group rows and choose one value per group
level: intermediate
minutes: 4
sourceLesson: sql-group-by
summary: GROUP BY emits one result row per grouping key.
---

The examples continue the shop database introduced in the first unit. Customers are Asha (1, London), Ben (2, Leeds), Chloe (3, unknown city), Dev (4, London) and Erin (5, Bristol). Asha has orders 101 and 102, Ben 103, Chloe 104, Dev 105; guest order 106 has no customer, and Erin has no orders. 

## GROUP BY: one row per group

`GROUP BY` splits the rows into groups that share the same values in the listed columns, then runs the aggregates once per group:

```sql
-- Each category becomes one summary row.
SELECT category,
       COUNT(*) AS n,
       AVG(price) AS avg_p
FROM products
GROUP BY category;
```

| category | n | avg_p |
|---|---|---|
| NULL | 1 | 8.0 |
| home | 2 | 65.0 |
| kitchen | 2 | 27.5 |

```
products        groups        result
Kettle  kit  ┐
Toaster kit  ┘─> kitchen ──> 2, 27.5
Lamp    home ┐
Rug     home ┘─> home    ──> 2, 65.0
Mug     NULL ──> NULL    ──> 1, 8.0
```

All NULL categories form **one** group, even though `NULL = NULL` is not true elsewhere in SQL.

You can group by an expression. Monthly order counts:

```sql
-- SQLite: group calendar dates by month.
SELECT strftime('%Y-%m', ordered_on)
         AS month,
       COUNT(*) AS n
FROM orders
GROUP BY month;
```

That gives 2026-01: 1, 2026-02: 2 and 2026-03: 3. In PostgreSQL, with a real `date` column, you would write `date_trunc('month', ordered_on)` instead. Both databases allow `GROUP BY` to use a select-list alias; check support and name-resolution rules when moving to another SQL engine.

### The single-value rule

After grouping, each output row stands for a whole group. Every column in `SELECT` must therefore have one value per group: either it is in the `GROUP BY` list, or it is inside an aggregate.

```sql
-- Deliberate bare column: PostgreSQL
-- rejects.
SELECT customer_id, ordered_on,
       COUNT(*)
FROM orders
GROUP BY customer_id;
```

Asha has two orders with different dates. Which `ordered_on` should her row show?

- **PostgreSQL** refuses: `column "orders.ordered_on" must appear in the GROUP BY clause or be used in an aggregate function`.
- **SQLite** accepts it and picks the value from some row in the group. Here it showed 2026-01-05, but nothing guarantees which one. (MySQL behaves the same unless `ONLY_FULL_GROUP_BY` is on, which it is by default since 5.7.5.)

SQLite has one documented special case. If the query uses exactly one `MIN()` or `MAX()`, the bare columns come from the row that holds that minimum or maximum. `SELECT category, MAX(price), name ... GROUP BY category` returns Rug for home and Kettle for kitchen. It is convenient, but it is not portable. In PostgreSQL, the standard "row with the max per group" tool is `DISTINCT ON` or a window function (module 2).

PostgreSQL does relax the rule in one sensible case. If you group by a table's **primary key**, you may select any other column from that table, because the key determines them:

```sql
-- The grouped primary key determines
-- c.name.
SELECT c.id, c.name, COUNT(o.id)
FROM customers c
LEFT JOIN orders o
  ON o.customer_id = c.id
GROUP BY c.id;  -- name allowed
```

## Key takeaways
- GROUP BY emits one result row per grouping key.
- Use an aggregate when an ungrouped column has several values per group.
- PostgreSQL recognises columns determined by a grouped primary key.

## Further reading
- [GROUP BY and HAVING — PostgreSQL documentation](https://www.postgresql.org/docs/current/queries-table-expressions.html)
- [Bare columns in aggregate queries — SQLite documentation](https://www.sqlite.org/lang_select.html#bare_columns_in_an_aggregate_query)
