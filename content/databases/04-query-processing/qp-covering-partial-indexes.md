---
id: qp-covering-partial-indexes
title: Covering and partial indexes
level: advanced
minutes: 3
sourceLesson: qp-index-tuning
summary: How an index that holds every needed column can skip the table, why recent updates undo that until VACUUM runs, and when a partial index can be used.
---

Examples use PostgreSQL 18 and the module's scaled-up shop tables (1,000,000 orders, 100,000 customers; the first lesson lists them). Plans are abbreviated and illustrative: real plans and timings depend on the data, statistics, settings, cache state and version. Assume serial execution.

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

The 20,000 updated rows were spread across nearly every page, so nearly every page lost its all-visible bit. The "index-only" scan went back to the heap for every row and, in this illustrative run, became 25 times slower. Index-only scans work best on tables that are mostly read, or where autovacuum keeps up.

> [!analogy] Real-world analogy: a library search terminal
> A library's search terminal lists each book's title, author and year. To answer "which books by this author came out in 2001?" you can use the terminal alone, without walking to the shelves. But if a section is marked "recently reorganised, check the shelves", you must go and look at each book there.
>
> **How it maps:** the terminal's listing is a covering index whose `INCLUDE` columns hold everything the query needs. Answering from it alone is an Index Only Scan. The "check the shelves" mark is a heap page that is not all-visible in the visibility map, which forces a heap fetch for every row on it; VACUUM is the librarian clearing the marks once the shelves are settled.
>
> **Where it stops:** the library's mark means the listing might be out of date. The database's heap check is different: it asks whether each row version is visible to your transaction's snapshot, which an index entry cannot say on its own, even when it is perfectly up to date.

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

