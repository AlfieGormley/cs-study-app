---
id: pg-booking-rollback-idempotency
title: Booking retries and rollback
level: intermediate
minutes: 3
sourceLesson: postgresql-in-practice
summary: Roll back if the reservation returns no row.
---

Use the ticket-shop `events` and `bookings` tables from the schema unit in a disposable database. Event 1 must exist with at least one seat. `bookings.event_id` references the event; `request_key` is NOT NULL and UNIQUE. Each new logical booking receives its own request key.

## Commit the whole booking or none

To reserve and record a booking atomically, use a transaction. This example is for a new request key and assumes the update returns one row:

```sql
-- Both database changes must commit.
BEGIN;

-- Only a row with seats can change.
UPDATE events
SET seats_left = seats_left - 1
WHERE id = 1 AND seats_left > 0
RETURNING id;

-- Proceed only if UPDATE returned a row.
INSERT INTO bookings
  (event_id, request_key)
VALUES (1, 'request-001')
RETURNING id;

COMMIT;
```

The application must inspect the update result. If it returns no rows, issue `ROLLBACK` and do not insert the booking. If the insert fails, roll back the transaction so the seat decrement is undone. An SQL error normally leaves the transaction aborted until rollback, unless you recover using a savepoint.

For a duplicate request key, roll back and then fetch the existing booking, checking that it belongs to the same intended request. Do **not** decrement a seat, use `ON CONFLICT DO NOTHING` for the booking and then commit regardless: the duplicate insert might do nothing while the extra decrement persists. A unique key is a building block for idempotency, not a complete workflow.

Keep transactions short. Do not hold the row lock while waiting for a customer or payment provider. External effects need their own retry design and checks to resolve uncertain payment outcomes; an SQL rollback does not undo a payment request to an external service.

## Key takeaways

- Roll back if the reservation returns no row.
- A duplicate insert must not leave an extra decrement committed.
- Database rollback cannot reverse an external payment.

## Further reading

- [PostgreSQL 18: sql insert](https://www.postgresql.org/docs/18/sql-insert.html)
- [PostgreSQL 18: tutorial transactions](https://www.postgresql.org/docs/18/tutorial-transactions.html)
- [PostgreSQL 18: sql savepoint](https://www.postgresql.org/docs/18/sql-savepoint.html)
