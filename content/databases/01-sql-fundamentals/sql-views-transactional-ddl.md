---
id: sql-views-transactional-ddl
title: Use stored queries and roll back schema changes
level: advanced
minutes: 3
sourceLesson: sql-schema-ddl
summary: A normal view stores a query; a materialised view stores its result.
---

The examples continue the shop database introduced in the first unit. The original products are Kettle £30, Toaster £25, Lamp £40, Rug £90 and Mug £8. 

## Views and DROP

A **database view** is a named, stored query:

```sql
-- Save the total calculation as a named
-- query.
CREATE VIEW order_totals AS
SELECT oi.order_id,
  SUM(oi.qty * p.price) AS total
FROM order_items oi
JOIN products p
  ON p.id = oi.product_id
GROUP BY oi.order_id;
```

`SELECT * FROM order_totals WHERE total > 60` returns 101 (62), 102 (80) and 104 (70). A view stores no data; it runs its query each time. PostgreSQL's `MATERIALIZED VIEW` stores the result and needs `REFRESH MATERIALIZED VIEW` to update it.

> [!analogy] Real-world analogy: a saved search versus a printed list
> A saved search in your email shows the matching messages each time you open it. A printed list of those messages is quicker to read, but goes out of date until you print it again.
>
> **How it maps:** An ordinary view is the saved search: it stores only the query and runs it each time. A materialised view is the printout: it stores the result, and `REFRESH MATERIALIZED VIEW` reprints it.
>
> **Where it stops:** A view is more flexible than a saved search: a query can join it to tables, filter it and aggregate it almost anywhere a table can be used. And a view's result is only as historically accurate as the facts it reads, as the next paragraph shows.

The view inherits the price-history flaw discussed earlier: changing today's product price changes a total recomputed from `products.price`. On the redesigned schema, total the saved `qty * unit_pence` instead. Naming a query does not change which facts it reads or turn a live calculation into a historical snapshot.

Transactional DDL lets you rehearse a small change and undo it. This complete example works in SQLite and PostgreSQL:

```sql
-- Rollback removes the table as well as its
-- row.
BEGIN;
CREATE TABLE migration_probe (n integer);
INSERT INTO migration_probe VALUES (7);
ROLLBACK;
-- The new table and its row are gone.
```

After rollback, selecting from `migration_probe` raises a missing-table error. The original shop tables are unaffected. This guarantee concerns supported transactional operations: PostgreSQL's `CREATE DATABASE` and `CREATE INDEX CONCURRENTLY`, for example, cannot run inside a transaction block. Check the command's documentation instead of assuming every administrative statement is transactional.

`DROP TABLE IF EXISTS t` tolerates a missing table, so that particular drop can be repeated. It does not make an entire migration safe to repeat. In PostgreSQL, `DROP TABLE t CASCADE` also removes dependent views and foreign key constraints without a separate approval prompt; the referencing tables remain. SQLite and PostgreSQL support transactional DDL for operations such as these. Explicitly roll back a failed migration: PostgreSQL normally aborts the transaction after an error, whereas SQLite can leave earlier successful statements pending and a later COMMIT could retain them. Most MySQL DDL implicitly commits, which is one reason migrations there need extra care.

## Key takeaways
- A normal view stores a query; a materialised view stores its result.
- DROP CASCADE can remove dependent views and constraints.
- Transactional DDL needs explicit transaction error handling; MySQL most DDL implicitly commits.

## Further reading
- [Data definition — PostgreSQL documentation](https://www.postgresql.org/docs/current/ddl.html)
- [ALTER TABLE — PostgreSQL documentation](https://www.postgresql.org/docs/current/sql-altertable.html)
