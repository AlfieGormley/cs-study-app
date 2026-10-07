---
id: qp-index-tuning
title: Index tuning
level: advanced
minutes: 17
summary: Designing indexes for the queries you actually run. When the planner will use an index, column order in composite indexes, Postgres 18 skip scan, covering and partial indexes, expression indexes, bitmap scans, and what every index costs you.
---

> [!note] Content gap: benchmark provenance
> Reproducible measurement records for the original laptop timings were not available to this audit, so empirical performance claims are omitted. The plan numbers below are retained only as illustrative inputs for learning EXPLAIN, not verified measurements or promised speedups. Measure your own representative workload.


The System Design module's indexing lesson covers how B-trees and LSM trees work. This lesson takes the planner's point of view: given a query and its plan, which index would change the plan, and is the change worth what the index costs?

The examples below assume an illustrative 1,000,000-row `orders` table and PostgreSQL 18 plan features.

## Will the planner use the index?

An index lets Postgres jump to matching entries, but each match still needs its row fetched from the table (the **heap**). If the rows are scattered, each fetch can be a different page. The planner compares that random I/O with simply reading the whole table in order.

Three queries on `ordered_on` with an index on that column:

| Filter | Rows | Plan | Time |
|---|---|---|---|
| One day | 438 | Bitmap index scan | 0.5 ms |
| One quarter | 37,390 (3.7%) | Bitmap index scan | 9.3 ms |
| Since 2021 | 847,258 (85%) | Seq Scan | 51 ms |

The quarter is the interesting one. A sequential scan took 23 ms, so the index halved the time, but look at the plan:

```
Bitmap Heap Scan on orders
  (actual rows=37390.00)
  Heap Blocks: exact=7306
-> Bitmap Index Scan on orders_date_idx
```

Matching 3.7% of the rows touched 7,306 of 7,353 heap pages, nearly all of them. Orders for a given quarter are spread uniformly through the table (`correlation` near 0), so almost every 8 KB page contains a few. A bitmap scan visits matching heap pages in physical order. Whether it beats a sequential scan when nearly every page is touched must be measured; the illustrative timing is not a general guarantee. But the benefit of an index depends on **how many pages** the matching rows occupy, not just how many rows match.

If the table were physically ordered by date (as an append-only log usually is), the same quarter would occupy about 4% of the pages, and the index would win by far more.

> [!note] Bitmap scans
> A **Bitmap Index Scan** collects the locations of all matches into an in-memory bitmap of pages; the **Bitmap Heap Scan** then reads those pages in physical order. It's the planner's middle ground between an index scan (good for a few rows) and a seq scan (good for many). Bitmaps from different indexes can be combined with `BitmapAnd` and `BitmapOr`.

## Composite indexes: column order is everything

A frequent query: a customer's five most recent orders.

```sql
SELECT * FROM orders
WHERE customer_id = 42
ORDER BY ordered_on DESC
LIMIT 5;
```

With an index on `(customer_id, ordered_on)`:

```
Limit  (actual rows=5.00)
-> Index Scan Backward using
     orders_cust_date_idx on orders
     Index Cond: (customer_id = 42)
     Index Searches: 1
     Buffers: shared hit=5 read=3
Execution Time: 0.032 ms
```

The index holds customer 42's entries side by side, already sorted by date. Postgres descends once, walks backwards and stops after five. There's no Sort node at all.

Now the same columns the other way round, `(ordered_on, customer_id)`:

```
Limit  (actual rows=5.00)
-> Index Scan Backward using
     orders_date_cust_idx on orders
     Index Cond: (customer_id = 42)
     Index Searches: 1031
     Buffers: shared hit=2067 read=1047
Execution Time: 3.084 ms
```

Customer 42's entries are now scattered across every date. Postgres 18's **skip scan** rescues the query by descending into the index once per distinct date (1,031 descents before finding five matches). That's about 100 times slower and 390 times more buffers than the right index. Before Postgres 18, the planner would have had to read the whole index or the whole table instead.

> [!tip] Order the columns: equality, then sort, then range
> 1. Columns compared with `=` go first.
> 2. Then the `ORDER BY` column, so rows come out in order.
> 3. Then columns compared with ranges (`<`, `>`, `BETWEEN`).
>
> Equality on leading keys and a range on the next key establish the usual scan bounds. Later conditions can still be checked within the index, and PostgreSQL 18 skip scan may perform additional searches to narrow work further. Check the actual plan rather than treating the rule as absolute.

Skip scan helps only when the leading column has few distinct values. With 2,400 dates it gave 2,400 descents for a full lookup (6.4 ms). With a million distinct leading values it would be hopeless. Design for the query; don't rely on skip scan.

## Covering indexes and index-only scans

If every column a query needs is in the index, Postgres can answer from the index alone: an **Index Only Scan**. `INCLUDE` adds columns to the index's leaf entries without making them part of the key:

```sql
CREATE INDEX orders_cust_cov_idx
  ON orders (customer_id)
  INCLUDE (ordered_on, total);

SELECT customer_id, ordered_on, total
FROM orders
WHERE customer_id BETWEEN 1 AND 2000;
```

There's a catch. The index doesn't record whether each row version is visible to your transaction, so Postgres must check the table **unless** the page is marked all-visible in the **visibility map**. Only VACUUM sets those bits. Here is the query (20,162 rows) straight after updating 2% of the table, and again after a VACUUM:

| State | Heap Fetches | Buffers | Time |
|---|---|---|---|
| Just after updating 20,000 rows | 20,592 | 20,661 | 27.6 ms |
| After VACUUM | 0 | 81 | 1.1 ms |

The 20,000 updated rows were spread across nearly every page, so nearly every page lost its all-visible bit. The "index-only" scan went back to the heap for every row and became 25 times slower. Index-only scans work best on tables that are mostly read, or where autovacuum keeps up.

## Partial indexes

If queries only ever look at a small subset of rows, index only that subset:

```sql
CREATE INDEX orders_pending_idx
  ON orders (ordered_on)
  WHERE status = 'pending';
```

```
Limit  (actual rows=20.00)
-> Index Scan using orders_pending_idx
Execution Time: 0.049 ms
```

The partial index holds 30,066 entries and is 272 kB. The full index on `ordered_on` is 6.9 MB. It's cheaper to maintain too: an insert of a shipped order doesn't touch it.

The planner uses a partial index only when it can **prove** the query's WHERE clause implies the index's predicate. `WHERE status = 'pending'` matches. `WHERE status = $1` with a parameter usually doesn't, because the planner can't prove `$1` is 'pending' when building a generic plan.

## Expression indexes and operator classes

An index on `email` is useless for `WHERE lower(email) = ...`, because the index stores `email`, not `lower(email)`. Index the expression:

```sql
CREATE INDEX customers_lower_email_idx
  ON customers (lower(email));
```

| Index | Plan | Time |
|---|---|---|
| None | Seq Scan, 99,999 removed | 17 ms |
| On `lower(email)` | Index Scan | 0.02 ms |

ANALYZE also gathers statistics on indexed expressions, so the row estimate improves from the 0.5% default (500) to 1.

**Operator classes** matter for `LIKE`. In a database whose collation isn't `C`, a plain B-tree on a text column can't serve `LIKE 'abc%'`, because the collation's sort order doesn't keep prefixes together byte-wise. An index built with `text_pattern_ops` can:

```sql
CREATE INDEX customers_email_pattern_idx
  ON customers (email text_pattern_ops);
```

No B-tree helps with `LIKE '%abc'` (leading wildcard). For that, use a trigram index (`pg_trgm` with GIN).

## Combining indexes

Postgres can combine single-column indexes with bitmaps:

```
Bitmap Heap Scan on orders
  (actual rows=308.00)
-> BitmapAnd
   -> Bitmap Index Scan
        on orders_cust_cov_idx
        Index Cond: (customer_id < 500)
        (actual rows=4984.00)
   -> Bitmap Index Scan on orders_date_idx
        Index Cond:
          (ordered_on < '2020-06-01')
        (actual rows=63535.00)
Execution Time: 2.148 ms
```

It read 4,984 and 63,535 index entries to find 308 rows. A composite index designed for this exact query would do better, but bitmap combination means a few well-chosen single-column indexes can serve many query shapes reasonably. That's often the better trade when queries are ad hoc.

## What every index costs

| Index | Size |
|---|---|
| orders (the table) | 59 MB |
| orders_cust_cov_idx | 30 MB |
| orders_pkey | 21 MB |
| orders_cust_date_idx | 21 MB |
| orders_date_idx | 6.9 MB |
| orders_pending_idx | 272 kB |

The date index is a third the size of the others because Postgres 13+ **deduplicates** B-tree entries: 1,000,000 rows share only 2,400 distinct dates.

Costs to weigh:

- **Writes.** An INSERT maintains applicable indexes; a partial index excludes rows outside its predicate. Changing a column referenced by a non-summarising index, including an `INCLUDE` column, prevents a **HOT** (heap-only tuple) update. BRIN is a summarising-index exception; HOT also requires room on the original heap page.
- **Memory.** Indexes compete with table data for the buffer cache.
- **Vacuum.** Every index must be scanned when dead rows are cleaned up.
- **Planning.** More indexes mean more paths to consider, and more chances of a surprising choice.

Find indexes that are never used:

```sql
SELECT indexrelname, idx_scan,
  pg_size_pretty(
    pg_relation_size(indexrelid))
FROM pg_stat_user_indexes
WHERE idx_scan = 0;
```

Check over weeks of traffic, and on replicas, before dropping anything. Also look for **redundant** indexes: an index on `(customer_id)` is usually redundant next to one on `(customer_id, ordered_on)`, which serves the same lookups.

## A tuning workflow

1. Find the queries that matter with `pg_stat_statements`, ordered by `total_exec_time` (frequency x duration), not just the slowest single run.
2. Get `EXPLAIN (ANALYZE, BUFFERS)` on production-sized data.
3. Design an index for the query: equality columns, then sort, then range; add `INCLUDE` columns only if an index-only scan is worth the size.
4. Build it without blocking writes: `CREATE INDEX CONCURRENTLY`. It's slower, and if it fails it leaves an invalid index you must drop.
5. Re-run EXPLAIN and compare buffers and time. Watch write latency afterwards.

## Key takeaways
- The planner uses an index when the matching rows occupy few pages. Low correlation means even a small fraction of rows can touch most pages.
- In a composite index put equality columns first, then the ORDER BY column, then range columns. The wrong order can require far more index work, even with Postgres 18's skip scan.
- Index-only scans depend on the visibility map. Recent updates force heap fetches until VACUUM runs.
- Partial indexes are small and cheap for queries on a fixed subset; expression indexes serve functions like `lower(email)` and give the planner statistics.
- Every index costs write amplification, cache space, vacuum work and lost HOT updates. Drop the unused ones.

## Further reading
- [Multicolumn indexes — PostgreSQL docs](https://www.postgresql.org/docs/current/indexes-multicolumn.html)
- [Index-only scans and covering indexes — PostgreSQL docs](https://www.postgresql.org/docs/current/indexes-index-only-scans.html)
- [Partial indexes — PostgreSQL docs](https://www.postgresql.org/docs/current/indexes-partial.html)
- [Combining multiple indexes — PostgreSQL docs](https://www.postgresql.org/docs/current/indexes-bitmap-scans.html)
- [Operator classes — PostgreSQL docs](https://www.postgresql.org/docs/current/indexes-opclass.html)
- [Use The Index, Luke: SQL indexing for developers](https://use-the-index-luke.com/)
- [Heap-only tuples (HOT) — PostgreSQL docs](https://www.postgresql.org/docs/current/storage-hot.html)
