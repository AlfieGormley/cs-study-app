---
id: rel-th-precomputed-results
title: Materialised results and generated values
level: advanced
minutes: 3
sourceLesson: rel-th-denormalisation
summary: Materialised results and generated values, with explicit examples and the conditions that make the reasoning valid.
---

## Materialised views

Reports such as daily sales per product scan millions of rows. Precompute them:

```sql
CREATE MATERIALIZED VIEW daily_sales AS
SELECT o.day, l.product_id,
       SUM(l.qty * l.price_paid) AS revenue
FROM orders o JOIN line l
  ON l.order_id = o.id
GROUP BY o.day, l.product_id;

CREATE UNIQUE INDEX
  ON daily_sales (day, product_id);

REFRESH MATERIALIZED VIEW
  CONCURRENTLY daily_sales;
```

In Postgres, a materialised view is a stored query result. It does not update itself; `REFRESH` re-runs the whole query. Plain `REFRESH` locks out readers while it runs; concurrent refresh lets ordinary reads continue. Concurrent refresh requires an already-populated view and a qualifying unique index on plain columns covering every row, without a partial predicate or expression. Only one refresh can run on a given view at a time. Relative speed depends on how much changed, so it is not correct to promise that concurrent refresh is always slower. Core Postgres has no incremental refresh (extensions such as `pg_ivm` add it), whereas Oracle's fast-refresh materialised views and SQL Server's indexed views maintain results incrementally, with restrictions on the query shape.

The view is as stale as its last refresh. That suits a dashboard refreshed every 15 minutes; it does not suit a stock level shown at checkout.

## Generated same-row values

A value computed from other columns *in the same row* is the cheapest kind, because there is no fan-out. Postgres generated columns do it declaratively:

```sql
ALTER TABLE line ADD COLUMN amount
  NUMERIC GENERATED ALWAYS AS
  (qty * price_paid) STORED;
```

`STORED` computes on write and can be indexed. PostgreSQL 16–17 support the stored kind. PostgreSQL 18 also supports `VIRTUAL`, the default when the kind is omitted, computed on read. Explicit `STORED` makes this example portable across those versions. Generation expressions must use allowed immutable expressions over the current row: no subqueries, aggregates, other rows or other generated columns. PostgreSQL 18 imposes extra built-in-type/function restrictions on virtual expressions.

The SQL assumes `orders(id, day)` and `line(order_id, product_id, qty, price_paid)`, with quantity an integer and price an exact numeric amount in pounds per item. Multiplying gives pounds for the line; summing gives pounds for that day and product. These are example fixtures, not assumptions that every shop has one timezone or one currency. A materialised view is a stored snapshot from the query’s read snapshot; it is not guaranteed to include writes that commit during its refresh.

## Key takeaways

- PostgreSQL materialised views stay unchanged until refreshed.
- Concurrent refresh needs a populated view and a qualifying unique index; generated values have stricter same-row rules.

## Further reading

- [PostgreSQL 18: refresh materialised views](https://www.postgresql.org/docs/18/sql-refreshmaterializedview.html)
- [PostgreSQL 18: generated columns](https://www.postgresql.org/docs/18/ddl-generated-columns.html)
- [AWS: transactional outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)
