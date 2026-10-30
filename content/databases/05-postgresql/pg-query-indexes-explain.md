---
id: pg-query-indexes-explain
title: Choose indexes and read the plan
level: intermediate
minutes: 5
sourceLesson: postgresql-in-practice
summary: Match the index method and column order to the query, then check the plan on realistic data.
---

Use the ticket-shop fixture: `bookings` has an identity primary key `id`, an `event_id` foreign key, a unique `request_key`, and a `created_at timestamptz` column. Create the tables in the schema unit first; populate representative data for meaningful performance measurements.

## Match an index to the request

Suppose an admin page needs an event's latest bookings:

```sql
-- Filter by event, then read newest first.
CREATE INDEX bookings_event_recent
ON bookings (event_id, created_at DESC);

SELECT id, created_at
FROM bookings
WHERE event_id = 1
ORDER BY created_at DESC
LIMIT 20;
```

This B-tree index puts the equality filter first and the requested ordering second. Postgres can jump to one event's entries, read them already in newest-first order and stop after 20, without sorting all that event's bookings. Column order matters: an index on `(created_at, event_id)` keeps entries in time order across all events, so one event's bookings are scattered through it.

In a test run on PostgreSQL 18 with 400,000 bookings spread over 52 events, this query touched only about a dozen pages (index plus table) and needed no Sort. With the index dropped, the planner scanned the whole 2,942-page table and sorted that event's roughly 7,700 matching rows to keep the newest 20.

The index costs storage, and writes must keep it up to date. Adding one to every column is rarely a good trade.

> [!analogy] Real-world analogy: a filing cabinet with a drawer per event
> Picture a cabinet with one drawer per event, each drawer's folders filed newest first. To fetch an event's latest 20 bookings, you open one drawer and lift out the front 20 folders. A cabinet filed purely by date would make you search every drawer for that event's folders.
>
> **How it maps:** the drawer is the leading `event_id` column; the folder order inside it is `created_at DESC`. Lifting the front 20 is the Index Scan feeding `LIMIT 20` with no Sort.
>
> **Where it stops:** a B-tree is a tree of index pages, not drawers, and the planner may still decide a plain table scan is cheaper. Postgres can also read an index backwards: the same index served `ORDER BY created_at ASC` for one event with an Index Scan Backward.

PostgreSQL 18 added **skip scan**: a multicolumn B-tree can sometimes serve a condition on a later column alone by searching once per distinct leading value. In the test above, a filter on `created_at` alone used this index with 53 index searches, one for each event plus one. That works well when the leading column has only a few different values; with many, a separate index on the later column is still the better fit.

Different index methods suit different operators:

- **B-tree** is the usual choice for equality, ranges and ordered retrieval.
- **GIN** supports inverted lookups, including many JSONB and full-text search operations.
- **GiST** suits overlap and nearness questions, such as range types and geometric data.
- **BRIN** stores summaries over page ranges; it can be compact and useful when values correlate with physical order, such as append-heavy timestamp data. Candidate pages still need rechecking.

A sequential scan is not automatically bad: reading most rows, or a tiny table, can be cheaper than visiting an index and fetching rows from the table heap. On the tiny example table, the planner ignores the index and sorts.

## Read the plan

Use the **Query Processing & Optimisation** lessons for deeper plan analysis. Start with this diagnostic on representative data:

```sql
-- This executes the SELECT below.
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, created_at
FROM bookings
WHERE event_id = 1
ORDER BY created_at DESC
LIMIT 20;
```

`EXPLAIN` estimates a plan; its `ANALYZE` option actually executes it. In PostgreSQL 18, `EXPLAIN ANALYZE` reports buffers even without the `BUFFERS` option; writing it keeps the command working the same way on older versions. Costs are planner units, not milliseconds. Compare estimated versus actual row counts, inspect repeated loops, and look at buffer activity before changing settings. A shared-buffer read can still be served from the OS page cache, so it is not proof of a physical disk read. Do not add up inclusive timings of parents and children.

> [!warning] ANALYZE has two meanings
> `ANALYZE bookings` updates planner statistics. `EXPLAIN ANALYZE` runs the supplied query and measures execution, including writes if the query modifies data. Use a disposable database for write experiments; even rollback does not undo sequence increments or external side effects.

## Key takeaways

- Put equality columns first and the ordering column next in a composite B-tree.
- Choose the index method by operator: B-tree, GIN, GiST or BRIN.
- PostgreSQL 18 skip scan helps only when the leading column has few different values.
- A tiny or unselective query can still favour a sequential scan.
- EXPLAIN ANALYZE executes; buffer reads need not be disk reads.

## Further reading

- [PostgreSQL 18: index types](https://www.postgresql.org/docs/18/indexes-types.html)
- [PostgreSQL 18: multicolumn indexes](https://www.postgresql.org/docs/18/indexes-multicolumn.html)
- [PostgreSQL 18: indexes and ORDER BY](https://www.postgresql.org/docs/18/indexes-ordering.html)
- [PostgreSQL 18: using EXPLAIN](https://www.postgresql.org/docs/18/using-explain.html)
- [PostgreSQL 18: EXPLAIN](https://www.postgresql.org/docs/18/sql-explain.html)
- [PostgreSQL 18: BRIN indexes](https://www.postgresql.org/docs/18/brin.html)
- [PostgreSQL 18 release notes](https://www.postgresql.org/docs/18/release-18.html)
