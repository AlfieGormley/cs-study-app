---
id: db-index-scan-budgets
title: Full scans and index lookups
level: basic
minutes: 3
summary: Predict how a full table scan grows with table size and why a selective index lookup barely does.
sourceLesson: db-indexing
---

Without a suitable access path, a database may need a full scan; partition pruning, zone maps or other mechanisms can sometimes reduce it. An **index** is an extra data structure, kept in sync with the table, that lets the database jump straight to the matching rows. Indexes can substantially reduce work for selective queries, but add storage and write cost.

## The cost of not having one

A full scan reads every page of the table, however few rows match. Its cost therefore follows the size of the table, not the size of the answer: double the table and the scan reads twice as many pages.

For a sense of scale, take a 100-million-row `orders` table on 8 KB pages with about 100 rows per page. That is about a million pages, roughly 8 GB. If the storage streams it at an assumed 1 GB/s with nothing cached, one scan takes around 8 seconds, even if the query returns a single row. A B-tree lookup for one key touches 3–4 pages instead, well under a millisecond when they are cached.

```formula reference
t_scan ≈ S / v
where
t_scan: the time to read the whole table once, in seconds (s)
S: the table's size on disk, in gigabytes (GB)
v: the storage's sustained sequential read speed, in gigabytes per second (GB/s)
≈: approximately equal to; caching, concurrent load and parallel workers change the real figure
In words: a full scan takes roughly the table's size divided by how fast the storage can stream it, so it grows in step with the table.
```

The estimate assumes the whole scan is sequential and nothing is cached; real scans can be faster if pages are in memory or several workers share the scan, and slower if the disk is busy.

> [!analogy] Real-world analogy: the index at the back of a book
> To find every mention of "Leeds" in a book with no index, you read every page. A book twice as long takes twice as long. With an index at the back, you look up "Leeds" in an alphabetical list and turn straight to pages 41 and 207.
>
> **How it maps:** Reading every page is the full table scan. The book's index is the database index: sorted keys with pointers to where each row lives, so the lookup cost barely changes as the book grows.
>
> **Where it stops:** A database index must be updated on every insert, update and delete that touches its columns, which a printed index never is. And if you need most of the pages anyway, reading the book straight through beats flipping back and forth, which is why a planner sometimes chooses a scan over an index.

## Predict the effect of growth

- **Unindexed filter**: the query's time grows roughly in proportion to the table, so a report that takes one second today takes about two once the table has doubled.
- **Selective indexed lookup**: a B-tree gains roughly one level each time the data grows by a factor of hundreds, so the lookup cost stays nearly flat (the next lesson explains why).
- **Broad indexed query**: if the condition matches a large share of rows, the index no longer saves pages, and the planner may rightly prefer the scan (see the index maintenance lesson).

`EXPLAIN` shows which path the planner chose: a `Seq Scan` node reads the whole table, while an `Index Scan`, `Index Only Scan` or bitmap scan uses the index.

## Key takeaways
- Scan cost grows with the pages read rather than the few rows you hoped to return.
- A selective index lookup stays cheap as the table grows; a scan does not.
- Indexes trade a faster access path for extra storage and write maintenance.

## Further reading
- [www.postgresql.org: indexes](https://www.postgresql.org/docs/current/indexes.html)
- [PostgreSQL: Using EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html)
