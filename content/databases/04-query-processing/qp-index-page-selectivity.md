---
id: qp-index-page-selectivity
title: Selectivity means pages as well as rows
level: advanced
minutes: 4
sourceLesson: qp-index-tuning
summary: Why an index helps only when the matching rows sit on few pages, and how scattered rows can make a small fraction of rows touch nearly every page.
---

Examples use PostgreSQL 18 and the module's scaled-up shop tables (1,000,000 orders, 100,000 customers; the first lesson lists them). Plans are abbreviated and illustrative: real plans and timings depend on the data, statistics, settings, cache state and version. Assume serial execution.

The System Design module's indexing lesson covers how B-trees and LSM trees work. This lesson takes the planner's point of view: given a query and its plan, which index would change the plan, and is the change worth what the index costs?

## Will the planner use the index?

An index lets Postgres jump to matching entries, but each match still needs its row fetched from the table (the **heap**). If the rows are scattered, each fetch can be a different page. The planner compares that random I/O with simply reading the whole table in order.

Three queries on `ordered_on` with an index on that column:

| Filter | Rows | Plan | Time |
|---|---|---|---|
| One day | 438 | Bitmap index scan | 0.5 ms |
| One quarter | 37,390 (3.7%) | Bitmap index scan | 9.3 ms |
| Since 2021 | 847,258 (85%) | Seq Scan | 51 ms |

The quarter is the interesting one. In this illustrative run a sequential scan took 23 ms, so the bitmap scan took well under half the time, but look at the plan:

```
Bitmap Heap Scan on orders
  (actual rows=37390.00)
  Heap Blocks: exact=7306
-> Bitmap Index Scan on orders_date_idx
```

Matching 3.7% of the rows touched 7,306 of 7,353 heap pages, nearly all of them. Orders for a given quarter are spread uniformly through the table (physical-order correlation near 0), so almost every 8 KiB page contains a few. You can predict that: if matching rows are scattered at random, the chance that a page has none at all is tiny.

```formula reference
p_none = (1 − s)^{r_page}
where
p_none: the probability that a page holds no matching row, if each row matches independently at random
s: the selectivity: the fraction of rows that match, here 0.037 (3.7%) for one quarter
r_page: the number of rows on each heap page, about 136 for `orders`
In words: a page escapes only if every one of its rows misses. With about five matching rows per page on average, only about 1 page in 170 escapes, so the scan still visits about 99.4% of the pages: about 7,309 of 7,353, close to the 7,306 the plan reported.
```

The model assumes matches are scattered at random; any clustering by date lowers the page count. A bitmap scan visits matching heap pages in physical order. Whether it beats a sequential scan when nearly every page is touched must be measured; the illustrative timing is not a general guarantee. But the benefit of an index depends on **how many pages** the matching rows occupy, not just how many rows match.

If rows were physically clustered by this date column (for example, an append-only log written in date order), the same quarter would occupy about 4% of the pages, and the index would win by far more.

> [!analogy] Real-world analogy: collecting red cars from a car park
> A valet is asked to fetch every red car. If red cars are scattered at random, there is one in almost every aisle of the car park, so the valet walks nearly every aisle even though only one car in 27 is red. If all the red cars had been parked together in one corner, the valet would visit one corner and be done.
>
> **How it maps:** cars are table rows, aisles are heap pages, and the red cars are the rows matching the filter. Scattered red cars are low physical-order correlation: a small fraction of rows still touches nearly every page. Parking them together is a table physically ordered by the filtered column, where the same rows occupy few pages.
>
> **Where it stops:** a valet sees the colour from a distance, while the database usually has to read a page to find out what is on it; the index tells it which pages hold matches, not how to avoid reading those pages.

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

