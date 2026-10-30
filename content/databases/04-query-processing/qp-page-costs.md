---
id: qp-page-costs
title: Pages, caches and scan costs
level: basic
minutes: 3
sourceLesson: qp-execution
summary: Why databases count pages rather than rows, what a buffer hit or read means, and why sequential pages are cheaper than random ones.
---

Examples use PostgreSQL 18 and the module's scaled-up shop tables (1,000,000 orders, 100,000 customers; the first lesson lists them). Plans are abbreviated and illustrative: real plans and timings depend on the data, statistics, settings, cache state and version. Assume serial execution.

## Pages: the unit of cost

Tables and indexes are stored in fixed-size **database pages** (normally 8 KiB in PostgreSQL 18; its block size is selected at build time). MySQL 8.0 InnoDB defaults to 16 KiB pages and permits other sizes when an instance is initialised. The `orders` table holds about 136 rows per page. The database reads whole pages, never single rows, so the main question for any plan is **how many pages does it touch, and are they in memory?**

MVCC means a scan must also establish whether each tuple version is visible to its snapshot. A sequential scan visits heap pages; an ordinary index scan follows index entries and then checks heap row versions. A covering index still needs heap visibility checks unless the visibility map says the page is all-visible.

A full scan's work therefore follows the table's size in pages, not its row count:

```formula reference
P = ⌈n_rows / r_page⌉
where
P: the number of pages the table occupies, which a simple full scan visits; visits do not necessarily cause physical storage reads
n_rows: the number of rows in the table
r_page: the average number of rows that fit on one 8 KiB page; about 136 for `orders`, whose rows are a few dozen bytes each plus per-row and per-page overhead
⌈ ⌉: ceiling: round up to the next whole number, because a part-filled last page still has to be read
In words: the pages a full scan reads are the row count divided by how many rows fit on a page. A million orders at about 136 per page fill about 7,353 pages, so rows twice as wide mean roughly twice as many pages for the same number of rows.
```

That is the ideal for evenly packed rows. Real tables also contain free space and dead row versions, so the true page count is usually a little higher.

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

