---
id: db-index-scan-budgets
title: Estimate the cost of a table scan
level: intermediate
minutes: 3
summary: Calculate table pages and scan time, and compare the work with a selective indexed lookup.
sourceLesson: db-indexing
---

Without a suitable access path, a database may need a full scan; partition pruning, zone maps or other mechanisms can sometimes reduce it. An **index** is an extra data structure, kept in sync with the table, that lets the database jump straight to the matching rows. Indexes can substantially reduce work for selective queries, but add storage and write cost.

## The cost of not having one

Take a 100 million row `orders` table on 8 KB pages, about 100 rows per page: one million pages, or 8 GB. A full scan at 1 GB/s takes around 8 seconds. A B-tree lookup touches 3–4 pages: well under a millisecond if they're cached.

To estimate how long a full scan takes, work out how many pages the table fills, how many bytes that is, and divide by how fast the disk can stream them:

```formula
P = N_rows / r
S = P × B
t_scan = S / v
where
P: the number of pages the table occupies
N_rows: the number of rows in the table
r: the number of rows that fit on one page; about 100 for rows of roughly 80 bytes on an 8 KB page
S: the table's size on disk, in gigabytes (GB)
B: the page size, in kilobytes (KB); 8 KB in Postgres
t_scan: the time to read the whole table once, in seconds (s)
v: the disk's sequential read speed, in gigabytes per second (GB/s)
In words: a scan has to read every page, so its time grows in step with the table's size, however few rows you actually want.
```

With the numbers above:

```formula
P = 100,000,000 / 100 = 1,000,000
S = 1,000,000 × 8 KB = 8 GB
t_scan = 8 GB / (1 GB/s) = 8 s
where
P: the number of pages
S: the table's size on disk
t_scan: the time for one full scan
KB: kilobyte, 1,000 bytes (here rounded; Postgres pages are 8,192 bytes)
GB: gigabyte, 1,000,000,000 bytes
GB/s: gigabytes per second, a read speed
s: seconds
In words: reading a 100-million-row table end to end takes about 8 seconds, against well under a millisecond for an index lookup.
```

This assumes the whole scan is sequential and nothing is cached; real scans can be faster if pages are in memory and slower if the disk is busy.

## Key takeaways
- Scan cost grows with the pages read rather than the few rows you hoped to return.
- The worked eight-second estimate assumes uncached sequential reads at the stated speed.
- Indexes trade a faster access path for extra storage and maintenance.

## Further reading
- [www.postgresql.org: indexes](https://www.postgresql.org/docs/current/indexes.html)
- [PostgreSQL: Using EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html)
