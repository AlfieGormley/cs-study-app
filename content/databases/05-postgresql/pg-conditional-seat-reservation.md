---
id: pg-conditional-seat-reservation
title: Reserve the last seat safely
level: intermediate
minutes: 3
sourceLesson: postgresql-in-practice
summary: Put the availability check inside the UPDATE so two buyers cannot both win the last seat.
---

The ticket-shop fixture has `events(id bigint PRIMARY KEY, seats_left integer NOT NULL CHECK (seats_left >= 0))`, plus the name, start time and JSONB columns introduced in the schema unit. Use the returned event-table ID; the fresh ticket-shop fixture below assumes event 1 exists.

## Make the decision inside the write

An unsafe application reads `seats_left = 1`, checks it in application code and later writes `seats_left = 0`. Two clients can both read 1 and both claim success. Wrapping that read and write in a default transaction alone does not fix the race, because each SELECT simply reads the latest committed value without reserving anything.

Instead, combine the condition and change in one statement:

```sql
-- Only a row with seats can change.
UPDATE events
SET seats_left = seats_left - 1
WHERE id = 1 AND seats_left > 0
RETURNING id, seats_left;
-- No returned row means no reservation.
```

A returned row means a seat was reserved. No returned row means no matching event with available seats, so the application must check the row count before telling the customer anything.

Why only one buyer can win: an UPDATE locks each row it changes until its transaction ends. Under Read Committed, the default, a second transaction updating the same row waits for that lock. When the first commits, the second re-evaluates its `WHERE` condition against the newly committed row. Starting with one seat, the first changes 1 to 0, the second rechecks `seats_left > 0`, finds it false and updates nothing.

At Repeatable Read the waiting transaction does not recheck. Once the first commits, it fails with "could not serialize access due to concurrent update", and the application must retry the whole transaction. Both levels prevent the double booking; they differ in what the loser sees.

> [!analogy] Real-world analogy: one ticket left at the box office
> Two fans see "1 left" on a website and both drive to the box office. If each one's decision was made at home, both believe they have a ticket. If the clerk only hands over a ticket after checking the drawer at the moment of sale, the second fan is told "sold out".
>
> **How it maps:** deciding at home is reading `seats_left` in application code and writing later. The clerk checking the drawer during the sale is the `WHERE seats_left > 0` condition inside the UPDATE. Queueing at the single window is the row lock that makes the second transaction wait.
>
> **Where it stops:** the clerk sees the drawer change as it happens. A waiting transaction under Read Committed rechecks only that row's new committed version, and under Repeatable Read it gets an error instead of a "sold out" answer.

PostgreSQL 18 also lets `RETURNING` name the old and new values, for example `RETURNING old.seats_left, new.seats_left`, which is handy for audit messages. Earlier versions return only the new values from an UPDATE.

## Key takeaways

- Combine the availability test and the decrement in one UPDATE.
- At Read Committed a waiting updater rechecks the committed row; at Repeatable Read it gets a serialization error instead.
- Check the returned row count before claiming success.

## Further reading

- [PostgreSQL 18: transaction isolation](https://www.postgresql.org/docs/18/transaction-iso.html)
- [PostgreSQL 18: UPDATE](https://www.postgresql.org/docs/18/sql-update.html)
- [PostgreSQL 18: explicit locking](https://www.postgresql.org/docs/18/explicit-locking.html)
- [PostgreSQL 18: returning data from modified rows](https://www.postgresql.org/docs/18/dml-returning.html)
