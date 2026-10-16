---
id: pg-conditional-seat-reservation
title: Reserve the last seat safely
level: intermediate
minutes: 2
sourceLesson: postgresql-in-practice
summary: Combine availability testing and decrement in one UPDATE.
---

The ticket-shop fixture has `events(id bigint PRIMARY KEY, seats_left integer NOT NULL CHECK (seats_left >= 0))`, plus the name, start time and JSONB columns introduced in the schema unit. Use the returned event-table ID; the fresh ticket-shop fixture below assumes event 1 exists.

## Make the decision inside the write

An unsafe application reads `seats_left = 1`, checks it in application code and later writes `seats_left = 0`. Two clients can both read 1 and both claim success. Wrapping that read and write in a default transaction alone does not fix the race.

Instead, combine the condition and change in one statement:

```sql
-- Only a row with seats can change.
UPDATE events
SET seats_left = seats_left - 1
WHERE id = 1 AND seats_left > 0
RETURNING id, seats_left;
-- No returned row means no reservation.
```

A returned row means a seat was reserved. No returned row means no matching event with available seats. Under Read Committed, transactions updating this same row concurrently wait for each other; after the first commits, the second rechecks the condition against the updated row. Starting with one seat, only one update can succeed.

## Key takeaways

- Combine availability testing and decrement in one UPDATE.
- At Read Committed a competing updater rechecks the updated row.
- Inspect the returned row count before claiming success.

## Further reading

- [PostgreSQL 18: transaction iso](https://www.postgresql.org/docs/18/transaction-iso.html)
- [PostgreSQL 18: sql update](https://www.postgresql.org/docs/18/sql-update.html)
- [PostgreSQL 18: explicit locking](https://www.postgresql.org/docs/18/explicit-locking.html)
