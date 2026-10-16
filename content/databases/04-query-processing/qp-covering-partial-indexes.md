---
id: qp-covering-partial-indexes
title: Covering and partial indexes
level: advanced
minutes: 3
sourceLesson: qp-index-tuning
summary: Covering and partial indexes with worked examples and explicit assumptions.
---

These examples use PostgreSQL 18. SQL Fundamentals supplies the shop relations: `customers(id, name, email, city, country)`, `orders(id, customer_id, status, ordered_on, total)`, `products(id, price)` and `order_items(order_id)`. IDs join orders to customers and items to orders. Dates use `date`, IDs use `integer`, and totals use `numeric`. Each query fragment uses these names; ellipses and standalone WHERE clauses need the surrounding SELECT shown by their context.

All historical plan fragments and timings in this unit are **illustrative inputs**, not reproduced benchmarks or promises. Their row/page counts describe a hypothetical dataset; actual plans vary with statistics, indexes, settings, cache state and PostgreSQL version. Assume serial execution unless a parallel worker process is shown.

## Covering indexes and index-only scans

If every column a query needs is in the index, Postgres can answer from the index alone: an **Index Only Scan**. `INCLUDE` adds columns to the index's leaf entries without making them part of the key:

```sql
-- Store payload needed by this report.
CREATE INDEX orders_cust_cov_idx
  ON orders (customer_id)
  INCLUDE (ordered_on, total);

SELECT customer_id, ordered_on, total
FROM orders
WHERE customer_id BETWEEN 1 AND 2000;
```

There's a catch. The index doesn't record whether each row version is visible to your transaction, so Postgres must check the table **unless** the page is marked all-visible in the **visibility map**. VACUUM can set those bits; unchanged all-visible pages then permit the heap check to be skipped. Here is the query (20,162 rows) straight after updating 2% of the table, and again after a VACUUM:

| State | Heap Fetches | Buffers | Time |
|---|---|---|---|
| Just after updating 20,000 rows | 20,592 | 20,661 | 27.6 ms |
| After VACUUM | 0 | 81 | 1.1 ms |

The 20,000 updated rows were spread across nearly every page, so nearly every page lost its all-visible bit. The "index-only" scan went back to the heap for every row and became 25 times slower. Index-only scans work best on tables that are mostly read, or where autovacuum keeps up.

## Partial indexes

If queries only ever look at a small subset of rows, index only that subset:

```sql
-- Keep only pending entries in the index.
CREATE INDEX orders_pending_idx
  ON orders (ordered_on)
  WHERE status = 'pending';
```

```
Limit  (actual rows=20.00)
-> Index Scan using orders_pending_idx
Execution Time: 0.049 ms
```

The partial index holds 30,066 entries and is 272 kB. The full index on `ordered_on` is 6.9 MB. It's cheaper to maintain too: a shipped-order insert adds no entry to it.

The planner uses a partial index only when it can **prove** the query's WHERE clause implies the index's predicate. `WHERE status = 'pending'` matches. `WHERE status = $1` with a parameter usually doesn't, because the planner can't prove `$1` is 'pending' when building a generic plan.

## Key takeaways
- Covering columns enable index-only access only when visibility checks can avoid heap fetches.
- A partial index is usable only when the planner can establish its predicate; a generic unknown parameter can prevent that proof.

## Further reading
- [Multicolumn indexes — PostgreSQL docs](https://www.postgresql.org/docs/18/indexes-multicolumn.html)
- [Index-only scans and covering indexes — PostgreSQL docs](https://www.postgresql.org/docs/18/indexes-index-only-scans.html)
- [Partial indexes — PostgreSQL docs](https://www.postgresql.org/docs/18/indexes-partial.html)
- [Combining multiple indexes — PostgreSQL docs](https://www.postgresql.org/docs/18/indexes-bitmap-scans.html)
- [Operator classes — PostgreSQL docs](https://www.postgresql.org/docs/18/indexes-opclass.html)
- [Use The Index, Luke: SQL indexing for developers](https://use-the-index-luke.com/)
- [Heap-only tuples (HOT) — PostgreSQL docs](https://www.postgresql.org/docs/18/storage-hot.html)

