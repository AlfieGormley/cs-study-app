---
id: qp-page-costs
title: Pages, caches and scan costs
level: basic
minutes: 4
sourceLesson: qp-execution
summary: Pages, caches and scan costs with worked examples and explicit assumptions.
---

These examples use PostgreSQL 18. SQL Fundamentals supplies the shop relations: `customers(id, name, email, city, country)`, `orders(id, customer_id, status, ordered_on, total)`, `products(id, price)` and `order_items(order_id)`. IDs join orders to customers and items to orders. Dates use `date`, IDs use `integer`, and totals use `numeric`. Each query fragment uses these names; ellipses and standalone WHERE clauses need the surrounding SELECT shown by their context.

All historical plan fragments and timings in this unit are **illustrative inputs**, not reproduced benchmarks or promises. Their row/page counts describe a hypothetical dataset; actual plans vary with statistics, indexes, settings, cache state and PostgreSQL version. Assume serial execution unless a parallel worker process is shown.

## Pages: the unit of cost

Tables and indexes are stored in fixed-size **database pages** (normally 8 KiB in PostgreSQL 18; its block size is selected at build time). MySQL 8.0 InnoDB defaults to 16 KiB pages and permits other sizes when an instance is initialised. The `orders` table holds about 136 rows per page. The database reads whole pages, never single rows, so the main question for any plan is **how many pages does it touch, and are they in memory?**

MVCC means a scan must also establish whether each tuple version is visible to its snapshot. A sequential scan visits heap pages; an ordinary index scan follows index entries and then checks heap row versions. A covering index still needs heap visibility checks unless the visibility map says the page is all-visible.

To turn a row count into the number of pages a full scan must read, divide by how many rows fit on one page:

```formula
P = ⌈n_rows / r_page⌉
P = ⌈1,000,000 / 136⌉
P = ⌈7,352.9⌉ = 7,353
where
P: the number of database pages the table occupies, so the pages a simplified dense full scan visits; visits do not necessarily cause physical storage reads
n_rows: the number of rows in the table, here 1,000,000 orders
r_page: the average number of rows that fit on one page, here about 136 for `orders` (8 KiB pages holding rows of a few dozen bytes each, plus per-row and per-page overhead)
⌈ ⌉: ceiling: round up to the next whole number, because a part-filled last page is still a whole page to read
In words: a million orders at about 136 per page fill about 7,353 pages, and it is that page count, not the row count, that a full scan pays for.
```

That matches the 7,353 pages in the table at the top of this lesson. It assumes rows are packed evenly; real tables also contain free space and dead row versions, so the true page count is usually a little higher than this ideal.

- A page found in PostgreSQL's shared buffer cache is a **hit**. It avoids an operating-system read request; no fixed latency follows from the label.
- A page that isn't is a **read**. It might come from the operating system's cache or from storage; measure the latency rather than assigning a fixed time to either case.

Reading pages in order (a sequential scan) is cheaper per page than jumping around (random I/O), because the storage and the OS can read ahead. Postgres encodes that by charging `seq_page_cost = 1` per sequential page and `random_page_cost = 4` per random one by default. The cost-model unit shows how those numbers turn into a plan's cost.

## Key takeaways
- A page visit may hit shared buffers, the OS cache, or storage; buffer reads are not necessarily disk reads.
- The dense rows-per-page calculation estimates storage pages, while planner cost also includes CPU work and visibility checks.

## Further reading
- [Overview of PostgreSQL internals: the path of a query](https://www.postgresql.org/docs/18/query-path.html)
- [The PostgreSQL executor](https://www.postgresql.org/docs/18/executor.html)
- [Using EXPLAIN — PostgreSQL docs](https://www.postgresql.org/docs/18/using-explain.html)
- [Query plan — Wikipedia](https://en.wikipedia.org/wiki/Query_plan)
- [Parallel query — PostgreSQL docs](https://www.postgresql.org/docs/18/parallel-query.html)

