---
id: asql-top-group-strategies
title: Top rows per group and indexed probes
level: advanced
minutes: 4
summary: Choose a tie rule before choosing a SQL ranking function.
sourceLesson: asql-interview-problems
---

products has id, name, category and price. order_items has product_id, order_id and qty. orders has id, customer_id, ordered_on and total. Its dates are distinct in the Advanced SQL fixture.

## 2. Top N per group

"Top two products by revenue in each category." Product revenue: Rug 360, Kettle 120, Mug 80, Toaster 50, Lamp 40, Vase 0.

```sql
-- Choose winners separately per group.
WITH rev AS (
  SELECT p.category, p.name,
    SUM(i.qty * p.price) AS revenue
  FROM products p
  JOIN order_items i
    ON i.product_id = p.id
  GROUP BY p.id
),
ranked AS (
  SELECT *, ROW_NUMBER() OVER (
    PARTITION BY category
    ORDER BY revenue DESC, name) AS rn
  FROM rev
)
SELECT category, name, revenue
FROM ranked WHERE rn <= 2;
```

| category | name | revenue |
|---|---|---|
| Home | Rug | 360 |
| Home | Lamp | 40 |
| Kitchen | Kettle | 120 |
| Kitchen | Mug | 80 |

Vase doesn't appear at all because the inner join drops products with no sales. If unsold products should compete (with revenue 0), use a `LEFT JOIN` and `COALESCE`.

Swap `ROW_NUMBER` for `RANK` or `DENSE_RANK` depending on the tie rule you agreed. Postgres offers two more tools:

```sql
-- Choose winners separately per group.
-- Latest order per customer, Postgres
SELECT DISTINCT ON (customer_id)
  customer_id, id, ordered_on
FROM orders
ORDER BY customer_id,
         ordered_on DESC;
```

`DISTINCT ON` keeps the first row of each group according to the `ORDER BY`. It's concise but Postgres-only.

```sql
-- Choose winners separately per group.
-- Top 2 per category, Postgres
SELECT c.category, t.name
FROM (SELECT DISTINCT category
      FROM products) AS c
CROSS JOIN LATERAL (
  SELECT name
  FROM product_rev r -- a view
  WHERE r.category = c.category
  ORDER BY revenue DESC
  LIMIT 2
) AS t;
```

Here `product_rev` is the aggregate product-revenue query above saved as a database view, without its later ranking step. LATERAL makes the inner query depend on the current category; a typical nested-loop plan executes it for each category. An ordinary aggregate view cannot itself have an index on its computed revenue. If product_rev is instead a maintained table or materialized view with an index on `(category, revenue DESC)`, each group can seek to its highest rows and stop after two visible matches. Obtaining the category list and computing or refreshing revenue also have a cost.

> [!note] Ties at the cut-off
> For the global top N, Postgres 13+ supports `FETCH FIRST 4 ROWS WITH TIES`. On our totals that returns 5 rows (200, 120, 90, 60, 60) because the 4th and 5th tie.

For a repeatable exact count, break revenue ties with a stable unique product key. If all tied winners matter, rank by revenue alone using RANK; DENSE_RANK instead means the highest distinct revenue bands. Those rules can return different row counts. A global LIMIT is not a per-category limit.

An indexed strategy still needs its outer category list. Computing SELECT DISTINCT category from millions of products may dominate the few inner probes. A small maintained categories table avoids that scan. Neither an ordinary aggregate view nor its computed revenue has a separately stored index; a maintained summary table or materialized view introduces refresh and consistency work.

## Key takeaways
- Choose a tie rule before choosing a SQL ranking function.
- LATERAL with an index can stop early for each known group.

## Further reading
- [PostgreSQL 18: sql select](https://www.postgresql.org/docs/18/sql-select.html)
- [PostgreSQL 18: functions aggregate](https://www.postgresql.org/docs/18/functions-aggregate.html)
- [SQLite reference](https://www.sqlite.org/windowfunctions.html)
