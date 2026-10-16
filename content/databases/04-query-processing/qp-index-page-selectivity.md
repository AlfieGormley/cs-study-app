---
id: qp-index-page-selectivity
title: Selectivity means pages as well as rows
level: advanced
minutes: 5
sourceLesson: qp-index-tuning
summary: Selectivity means pages as well as rows with worked examples and explicit assumptions.
---

These examples use PostgreSQL 18. SQL Fundamentals supplies the shop relations: `customers(id, name, email, city, country)`, `orders(id, customer_id, status, ordered_on, total)`, `products(id, price)` and `order_items(order_id)`. IDs join orders to customers and items to orders. Dates use `date`, IDs use `integer`, and totals use `numeric`. Each query fragment uses these names; ellipses and standalone WHERE clauses need the surrounding SELECT shown by their context.

All historical plan fragments and timings in this unit are **illustrative inputs**, not reproduced benchmarks or promises. Their row/page counts describe a hypothetical dataset; actual plans vary with statistics, indexes, settings, cache state and PostgreSQL version. Assume serial execution unless a parallel worker process is shown.

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

Matching 3.7% of the rows touched 7,306 of 7,353 heap pages, nearly all of them. Orders for a given quarter are spread uniformly through the table (physical-order correlation near 0), so almost every 8 KiB page contains a few. You can predict that: if matching rows are scattered at random, the chance that a page has none at all is tiny.

```formula
m = r_page × s
m = 136 × 0.037 ≈ 5
p_none = (1 − s)^{r_page}
p_none = 0.963^{136} ≈ 0.006
P_hit ≈ P × (1 − p_none)
P_hit ≈ 7,353 × 0.994 ≈ 7,309
where
m: the average number of matching rows on each heap page
r_page: the number of rows on each heap page, about 136 for `orders`
s: the selectivity: the fraction of rows that match, here 0.037 (3.7%) for one quarter
p_none: the probability that a page holds no matching row, if each row matches independently at random; one factor of (1 − s) per row on the page, all multiplied together
P: the number of heap pages in the table, 7,353
P_hit: the expected number of heap pages holding at least one matching row
≈: approximately equal to
In words: with about 5 matches per page on average, only about 1 page in 170 escapes, so the index scan still visits about 99.4% of the pages.
```

The prediction, about 7,309 pages, is close to the 7,306 the plan reported. The model assumes matches are scattered at random; any clustering by date lowers the page count. A bitmap scan visits matching heap pages in physical order. Whether it beats a sequential scan when nearly every page is touched must be measured; the illustrative timing is not a general guarantee. But the benefit of an index depends on **how many pages** the matching rows occupy, not just how many rows match.

If rows were physically clustered by this date column (for example, an append-only log written in date order), the same quarter would occupy about 4% of the pages, and the index would win by far more.

> [!note] Bitmap scans
> A **Bitmap Index Scan** collects the locations of all matches into an in-memory bitmap of pages; the **Bitmap Heap Scan** then reads those pages in physical order. It's the planner's middle ground between an index scan (good for a few rows) and a seq scan (good for many). Bitmaps from different indexes can be combined with `BitmapAnd` and `BitmapOr`.

## Key takeaways
- Scattered matches can touch most pages even at low row selectivity.
- Bitmap scans gather tuple locations and visit heap pages in physical order; compare their cost with a full scan.

## Further reading
- [Multicolumn indexes — PostgreSQL docs](https://www.postgresql.org/docs/18/indexes-multicolumn.html)
- [Index-only scans and covering indexes — PostgreSQL docs](https://www.postgresql.org/docs/18/indexes-index-only-scans.html)
- [Partial indexes — PostgreSQL docs](https://www.postgresql.org/docs/18/indexes-partial.html)
- [Combining multiple indexes — PostgreSQL docs](https://www.postgresql.org/docs/18/indexes-bitmap-scans.html)
- [Operator classes — PostgreSQL docs](https://www.postgresql.org/docs/18/indexes-opclass.html)
- [Use The Index, Luke: SQL indexing for developers](https://use-the-index-luke.com/)
- [Heap-only tuples (HOT) — PostgreSQL docs](https://www.postgresql.org/docs/18/storage-hot.html)

