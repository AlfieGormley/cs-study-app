---
id: qp-explain-buffers
title: Buffers and a slow-query investigation
level: intermediate
minutes: 4
sourceLesson: qp-reading-explain
summary: Buffers and a slow-query investigation with worked examples and explicit assumptions.
---

These examples use PostgreSQL 18. SQL Fundamentals supplies the shop relations: `customers(id, name, email, city, country)`, `orders(id, customer_id, status, ordered_on, total)`, `products(id, price)` and `order_items(order_id)`. IDs join orders to customers and items to orders. Dates use `date`, IDs use `integer`, and totals use `numeric`. Each query fragment uses these names; ellipses and standalone WHERE clauses need the surrounding SELECT shown by their context.

All historical plan fragments and timings in this unit are **illustrative inputs**, not reproduced benchmarks or promises. Their row/page counts describe a hypothetical dataset; actual plans vary with statistics, indexes, settings, cache state and PostgreSQL version. Assume serial execution unless a parallel worker process is shown.

## Reading BUFFERS

Each buffer is one page, normally 8 KiB, so the counts convert to volumes. For `Buffers: shared hit=7011 read=342`:

```formula
V = n_buf × 8 KiB
V_hit = 7,011 × 8 KiB = 56,088 KiB
V_hit ≈ 54.8 MiB
V_read = 342 × 8 KiB = 2,736 KiB
V_read ≈ 2.7 MiB
where
V: the volume of data the buffer accesses represent
n_buf: the number of buffer (page) accesses in the count
V_hit: the volume served from Postgres's shared memory
V_read: the volume requested from the operating system
KiB: kibibyte, 1,024 bytes
MiB: mebibyte, 1,024 KiB
≈: approximately equal to
In words: about 55 MiB came from Postgres's own cache and under 3 MiB had to be requested from the operating system.
```

Repeated accesses to the same page count again each time, so this is a measure of work, not of distinct data.

- **hit**: already in shared buffers.
- **read**: requested from the operating system. It might still have come from the OS page cache, so a `read` is not necessarily a disk read. Enable `track_io_timing` to measure time spent in I/O calls. It still cannot tell whether those calls were served from the OS cache or physical storage.
- **dirtied / written**: pages this query modified or had to write out (for example, setting hint bits on freshly loaded rows).
- **temp read / written**: temporary files from spilling sorts and hashes.

Buffer access counts complement timing, but they are not independent of system state. The hit/read split depends on cache warmth, and repeated accesses may revisit the same page. The illustrative totals (3.6 million versus 19,000) suggest very different work, but do not imply that every access becomes a separate disk read on a cold cache.

## A method for slow queries

1. Get the real plan: `EXPLAIN (ANALYZE, BUFFERS)` against production-sized data. A plan from a 1,000-row dev table tells you little.
2. Note the total `Execution Time`.
3. Find the nodes with the largest **exclusive** time (subtract children, multiply by loops).
4. Walk up from the leaves looking for the first big estimate error.
5. Check the red flags table.
6. Change one thing (an index, ANALYZE, a rewrite), then re-run and compare buffers and time.

For long plans, paste the text into a visualiser such as [explain.depesz.com](https://explain.depesz.com/) or [explain.dalibo.com](https://explain.dalibo.com/), which compute exclusive times and highlight misestimates for you.

To catch slow plans in production without running EXPLAIN by hand, use the **auto_explain** module, which logs the plans of statements slower than a threshold, and **pg_stat_statements**, which records total time and calls for each query shape (queries that differ only in their constant values are counted together) so you know which queries to look at first.

> [!note] Other databases
> MySQL has `EXPLAIN ANALYZE` (8.0.18+) with a similar tree format. SQLite's `EXPLAIN QUERY PLAN` is much terser:
> `SCAN o`, then `SEARCH c USING INTEGER PRIMARY KEY (rowid=?)`, then `USE TEMP B-TREE FOR GROUP BY`. That was our cities query: a nested loop of primary-key lookups, with a temporary B-tree for the grouping.

## Caveats

- EXPLAIN ANALYZE doesn't send the result rows to the client, so network transfer time isn't included. Postgres 17 added a `SERIALIZE` option to measure the cost of converting rows to output format.
- Repeated runs change cache warmth. Compare multiple representative runs and inspect `read` versus `hit`; two runs do not establish production behaviour.
- Per-node timing has overhead. If the plan has millions of tiny loops, use `TIMING OFF` and rely on row counts and buffers.

## Key takeaways
- Buffer counters describe accesses, including repeated visits; shared reads can hit the OS cache.
- Compare representative plans and timings, including client costs omitted by EXPLAIN.

## Further reading
- [Using EXPLAIN — PostgreSQL docs](https://www.postgresql.org/docs/18/using-explain.html)
- [EXPLAIN command reference — PostgreSQL docs](https://www.postgresql.org/docs/18/sql-explain.html)
- [auto_explain — PostgreSQL docs](https://www.postgresql.org/docs/18/auto-explain.html)
- [pg_stat_statements — PostgreSQL docs](https://www.postgresql.org/docs/18/pgstatstatements.html)
- [PostgreSQL 18 release notes](https://www.postgresql.org/docs/18/release-18.html)
- [EXPLAIN QUERY PLAN — SQLite docs](https://www.sqlite.org/eqp.html)

