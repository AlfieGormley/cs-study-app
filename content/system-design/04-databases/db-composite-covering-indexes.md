---
id: db-composite-covering-indexes
title: Composite, covering and specialised indexes
level: intermediate
minutes: 3
summary: Order index columns for a query, include needed payloads, and select a partial or specialised access path.
sourceLesson: db-indexing
---

Design an index for the predicate, ordering and returned columns of a real query. Column order decides the contiguous range you can seek; extra payloads decide whether table visits are necessary.

## Composite indexes

A **composite** (multi-column) index sorts by the first column, then by the second within ties, and so on, like a phone book sorted by surname then first name.

```sql
-- Customer equality narrows the date range.
CREATE INDEX idx_orders_cust_date
  ON orders (customer_id, created_at);
```

This index serves:

- `WHERE customer_id = 42`
- `WHERE customer_id = 42 AND created_at > '2026-09-01'`
- `WHERE customer_id = 42 ORDER BY created_at DESC LIMIT 20` with no sort step

With many distinct customers, it may not efficiently serve `WHERE created_at > '2026-09-01'` alone, because entries for that date range are scattered across every customer. This is the **leftmost-prefix rule**.

Some engines soften the rule with a **skip scan** (MySQL 8.0, Oracle, and Postgres from version 18): when the leading column has only a few distinct values, they probe the index once per value. With millions of customers that doesn't help, so design the index for the query rather than relying on it.

> [!tip] Column order: equality first, then range
> Put columns tested with `=` first and the range or sort column last. With `(created_at, customer_id)`, a conventional scan may cover September entries for many customers; skip scan and other planner choices can change that.

## Covering indexes

Normally an index lookup finds a row pointer, then fetches the row from the table: an extra random read per row. If the index contains *every column the query needs*, the database can answer from the index alone. That's a **covering index**, and Postgres calls the resulting plan an *index-only scan*.

```sql
-- INCLUDE stores payload, not sort keys.
CREATE INDEX idx_orders_cover
  ON orders (customer_id, created_at)
  INCLUDE (total_p, status);

-- Seek customer 42 and read newest first.
SELECT created_at, total_p, status
FROM orders
WHERE customer_id = 42
ORDER BY created_at DESC LIMIT 20;
```

These SQL fragments assume an `orders` table with the named columns. Returned values and whether a plan avoids heap visits depend on the data and visibility map.

`INCLUDE` adds non-key payload columns to the leaves without affecting sort order. For a query returning 20 rows, that can avoid heap visits when the visibility conditions permit; avoided visits are not necessarily physical disk reads.

In Postgres, index-only scans also depend on the **visibility map**: if a page has recent, unvacuumed changes, Postgres still visits the heap to check row visibility. Keep autovacuum healthy on tables where you rely on them.

## Other index types

- **Hash** indexes: equality only, no ranges. Rarely better than a B-tree in Postgres.
- **Partial indexes**: index only the rows you query, e.g. `WHERE status = 'pending'`. Much smaller.
- **Expression** indexes: `ON users (lower(email))` serves `WHERE lower(email) = ...`.
- **GIN** (inverted): for `jsonb`, arrays and full-text search.
- **GiST/SP-GiST, BRIN**: geometric data, and very large naturally ordered tables (BRIN stores min/max per block range and is tiny).

## Key takeaways
- Composite indexes sort by the first key, then by later keys within ties.
- Covering indexes contain the queried columns; PostgreSQL still needs sufficient visibility information.
- Partial indexes store only qualifying rows; other types serve expressions, documents or ordered block ranges.

## Further reading
- [PostgreSQL: Multicolumn indexes](https://www.postgresql.org/docs/current/indexes-multicolumn.html)
- [PostgreSQL: Index-only scans and covering indexes](https://www.postgresql.org/docs/current/indexes-index-only-scans.html)
- [PostgreSQL: Partial indexes](https://www.postgresql.org/docs/current/indexes-partial.html)
