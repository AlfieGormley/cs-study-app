---
id: pg-query-indexes-explain
title: Choose indexes and read the plan
level: intermediate
minutes: 4
sourceLesson: postgresql-in-practice
summary: A composite B-tree can match equality then ordering.
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

This B-tree index puts the equality filter first and the requested ordering second. Postgres can find one event's entries in the desired order without sorting all its bookings. The index costs storage and maintenance on writes; adding one to every column is rarely a good trade.

Different index methods suit different operators:

- **B-tree** is the usual choice for equality, ranges and ordered retrieval.
- **GIN** supports inverted lookups, including many JSONB and full-text search operations.
- **BRIN** stores summaries over page ranges; it can be compact and useful when values correlate with physical order, such as append-heavy timestamp data. Candidate pages still need rechecking.

A sequential scan is not automatically bad: reading most rows, or a tiny table, can be cheaper than visiting an index and fetching rows from the table heap. On this tiny example, do not expect the index to win.

Use the existing **Query Processing & Optimisation** lessons for deeper plan analysis. Start with this diagnostic on representative data:

```sql
-- This executes the SELECT below.
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, created_at
FROM bookings
WHERE event_id = 1
ORDER BY created_at DESC
LIMIT 20;
```

`EXPLAIN` estimates a plan; its `ANALYZE` option actually executes it. Costs are planner units, not milliseconds. Compare estimated versus actual row counts, inspect repeated loops, and look at buffer activity before changing settings. A shared-buffer read can still be served from the OS page cache, so it is not proof of a physical disk read. Do not add up inclusive timings of parents and children.

> [!warning] ANALYZE has two meanings
> `ANALYZE bookings` updates planner statistics. `EXPLAIN ANALYZE` runs the supplied query and measures execution, including writes if the query modifies data. Use a disposable database for write experiments; even rollback does not undo sequence increments or external side effects.

## Key takeaways

- A composite B-tree can match equality then ordering.
- A tiny table can still favour a sequential scan.
- EXPLAIN ANALYZE executes; buffer reads need not be disk reads.

## Further reading

- [PostgreSQL 18: indexes types](https://www.postgresql.org/docs/18/indexes-types.html)
- [PostgreSQL 18: indexes multicolumn](https://www.postgresql.org/docs/18/indexes-multicolumn.html)
- [PostgreSQL 18: indexes ordering](https://www.postgresql.org/docs/18/indexes-ordering.html)
- [PostgreSQL 18: using explain](https://www.postgresql.org/docs/18/using-explain.html)
- [PostgreSQL 18: sql explain](https://www.postgresql.org/docs/18/sql-explain.html)
- [PostgreSQL 18: brin](https://www.postgresql.org/docs/18/brin.html)
