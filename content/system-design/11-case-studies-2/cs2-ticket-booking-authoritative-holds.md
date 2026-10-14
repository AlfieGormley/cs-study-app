---
id: cs2-ticket-booking-authoritative-holds
title: Authoritative ticket holds
level: advanced
minutes: 4
summary: Atomically claim whole seat groups and fence release and allocation decisions.
sourceLesson: cs2-ticket-booking
---

## API design

This is an illustrative endpoint contract, not a runnable HTTP request. Arrows distinguish responses from submitted fields.

```
GET  /v1/events/{id}
GET  /v1/events/{id}/seats?section=A
  -> [{seat_id, status}]  (cached ~2 s)

POST /v1/events/{id}/holds
  Authorization: <queue access token>
  {seat_ids:[...]}
  -> 201 {hold_id, expires_at}
  -> 409 {unavailable:[...]}

POST /v1/holds/{hold_id}/checkout
  Idempotency-Key: <uuid>
  {payment_method}
  -> {order_id, status}

DELETE /v1/holds/{hold_id}
```

> **Content gap:** no production ticketing benchmark or implementation is supplied. Capacity targets and timing budgets are hypothetical, and payment recovery requires the additional durable state described below.

Holds are **all-or-nothing**. Four seats together, or none. The checkout carries an **idempotency key**, with atomic server-side deduplication, a unique hold-to-order mapping and PSP idempotency/reconciliation to prevent duplicate orders and reduce duplicate payment effects.

## Data model

This is a schema sketch: PK marks the primary key. It omits executable type declarations and migrations.

```
seats(event_id, seat_id,      PK both
      section, row, price_tier,
      status,   -- AVAILABLE/HELD/SOLD
      hold_id, hold_expires_at,
      order_id, version)

holds(hold_id PK, event_id, user_id,
      seat_ids, expires_at, state)

orders(order_id PK, user_id, event_id,
       hold_id UNIQUE, amount, state,
       idempotency_key UNIQUE)
```

Partition `seats` by `event_id`. Every booking transaction touches a single event, so inventory stays on one shard if holds and orders are colocated by event too. The external PSP still requires a recoverable workflow rather than one database transaction. The `UNIQUE` constraint on `orders.hold_id` is a belt-and-braces guard: one hold can produce at most one order.

## High-level architecture

Follow the arrows as data paths; the drawing is not a deployment specification.

```
   Fans (millions)
        |
        v
+----------------+
| CDN / edge     |  static pages,
| waiting room   |  queue status
+----------------+
        | admitted (signed token)
        v
+----------------+   +-----------+
| Booking API    |-->| Seat-map  |
| (stateless)    |   | cache     |
+----------------+   +-----------+
   |          |
   v          v
+---------+ +---------+ +-------+
|Inventory| |Checkout |>|Payment|
|   DB    |<|service  | | (PSP) |
+---------+ +---------+ +-------+
   ^
   |  expiry sweeper (tidy-up)
```

## Deep dive 1: holding a seat without double-booking

A seat goes through a small state machine:

```
AVAILABLE --hold--> HELD --pay--> SOLD
    ^                 |
    +---expire/cancel-+
```

### Option A: conditional update (optimistic)
This is the workhorse. Use a set-based conditional update inside a short transaction (the placeholders below are schematic):

```sql
-- Each matching row is claimed atomically.
UPDATE seats
SET status='HELD', hold_id=:h,
    hold_expires_at=now()+interval '8 min'
WHERE event_id=:e AND seat_id IN (:s)
  AND (status='AVAILABLE'
       OR (status='HELD'
           AND hold_expires_at < now()));
```

If the affected row count is less than the number of seats requested, **roll back** and return 409 with the seats that were taken. The database's row-level atomicity guarantees only one transaction moves a given row out of AVAILABLE. There's no separate lock service and no read-then-write race.

Deduplicate and validate the seat-ID list, check the exact affected count, and roll back the whole group on conflict. Both set-based updates and explicit locks can deadlock; use consistent acquisition order and bounded transaction retries. PostgreSQL `now()` is fixed at transaction start: for strict expiry deadlines, lock first, then evaluate a fresh database timestamp in a short transaction.

Note the `hold_expires_at < now()` clause. An expired hold is treated as available **when attempting a new hold**, so correctness never depends on a background sweeper running on schedule. The sweeper only tidies up, which keeps the seat map accurate.

### Option B: pessimistic locking
`SELECT ... FOR UPDATE` on the seat rows, check, then update. This is correct, but locks are held across round trips. Under contention, waiters pile up, and multi-seat orders can deadlock unless you **always lock in a consistent order** (for example, sorted by `seat_id`).

### Option C: Redis holds
`SET seat:{e}:{s} {hold} NX PX 480000` for each seat gives very fast holds with built-in expiry (`NX` sets the key only if it does not already exist; `PX 480000` expires it after 480,000 milliseconds, which is 8 minutes). But Redis is now a second source of truth that must agree with the database. If Redis fails over and loses a recent write (replication is asynchronous), two users can hold the same seat. Use Redis as a **fast pre-filter**, and still make the final, authoritative transition in the database with a conditional update.

## Key takeaways
- Allocate all requested seats or roll back the group.
- Reclaim expired HELD rows during allocation so correctness does not depend on a sweeper.
- Redis can pre-filter; authoritative conditional database transitions decide ownership.

## Further reading
- [Explicit locking (PostgreSQL docs)](https://www.postgresql.org/docs/current/explicit-locking.html)
- [Optimistic concurrency control (Wikipedia)](https://en.wikipedia.org/wiki/Optimistic_concurrency_control)
- [How to do distributed locking (Martin Kleppmann)](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html)
