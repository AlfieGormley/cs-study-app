---
id: cs2-ticket-booking
title: Ticket booking (Ticketmaster)
level: advanced
minutes: 15
summary: Design a ticketing platform that never double-sells a seat, covering seat holds with expiry, the concurrency control that makes booking safe, and virtual waiting rooms for flash-sale traffic.
---

Ticket booking combines two problems that pull in opposite directions. **Correctness**: at most one active booking owns seat 14F for an event. **Extreme, spiky load**: millions of fans arrive in the same minute for 60,000 seats. The famous failure was the November 2022 Taylor Swift Eras Tour presale. About 1.5 M verified fans had been sent codes, but Ticketmaster said its systems saw around 3.5 B requests, four times its previous peak. The figures come from company statements at the time, so treat them as approximate.

The interview insight is that you **don't** scale the booking core to millions of visitors. You **shape the traffic** so the core only ever sees what it can handle, and make that core strictly correct.

## Requirements

### Functional
- Browse events and view the seat map with live-ish availability.
- Select seats and **hold** them for a few minutes while paying.
- Pay and confirm. Tickets are issued.
- Holds expire automatically and seats return to the pool.
- For on-sales, a fair **queue** decides who gets to shop, and in what order.

### Non-functional
- **No double-booking, ever.** This is the hard constraint.
- Browsing can be eventually consistent (a seat map a few seconds stale is fine). Holding and booking must be strongly consistent.
- Survive **100x+** normal traffic for an hour, without collapse.
- Fairness and bot resistance.
- Booking p99 latency of a second or two. Payment latency is mostly outside our control.

## Back-of-the-envelope

```
Stadium: 60,000 seats, avg order 4 seats
  -> ~15,000 successful orders
Assumed fans at on-sale: 2-14 M
Waiting room polls every 30 s:
  2 M / 30 = ~67,000 req/s (edge only)
Seat-map views while shopping:
  50,000 shoppers x 1 refresh/5 s
  = 10,000 req/s (cacheable)
Hold attempts: if admitted shoppers
  try ~2 holds/min:
  50,000 x 2 / 60 = ~1,700 holds/s
```

What matters:

- **Under the assumed four-seat order size, demand is about 133–933 times the 15,000 available orders.** Most visitors will leave without tickets. The system's job is to make that happen fairly and cheaply.
- The hold/booking core needs only **thousands of writes a second** at peak, if admissions are throttled. Whether one event partition can sustain this depends on its measured contention, transaction duration, indexes and replication.
- The waiting room has to absorb **tens of thousands of requests a second**, so serve it from the edge or CDN with almost no origin calls.

## API design

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

```
UPDATE seats
SET status='HELD', hold_id=:h,
    hold_expires_at=now()+interval '8 min'
WHERE event_id=:e AND seat_id IN (:s)
  AND (status='AVAILABLE'
       OR (status='HELD'
           AND hold_expires_at < now()))
```

If the affected row count is less than the number of seats requested, **roll back** and return 409 with the seats that were taken. The database's row-level atomicity guarantees only one transaction moves a given row out of AVAILABLE. There's no separate lock service and no read-then-write race.

Deduplicate and validate the seat-ID list, check the exact affected count, and roll back the whole group on conflict. Both set-based updates and explicit locks can deadlock; use consistent acquisition order and bounded transaction retries. PostgreSQL `now()` is fixed at transaction start: for strict expiry deadlines, lock first, then evaluate a fresh database timestamp in a short transaction.

Note the `hold_expires_at < now()` clause. An expired hold is treated as available **when attempting a new hold**, so correctness never depends on a background sweeper running on schedule. The sweeper only tidies up, which keeps the seat map accurate.

### Option B: pessimistic locking
`SELECT ... FOR UPDATE` on the seat rows, check, then update. This is correct, but locks are held across round trips. Under contention, waiters pile up, and multi-seat orders can deadlock unless you **always lock in a consistent order** (for example, sorted by `seat_id`).

### Option C: Redis holds
`SET seat:{e}:{s} {hold} NX PX 480000` for each seat gives very fast holds with built-in expiry. But Redis is now a second source of truth that must agree with the database. If Redis fails over and loses a recent write (replication is asynchronous), two users can hold the same seat. Use Redis as a **fast pre-filter**, and still make the final, authoritative transition in the database with a conditional update.

> [!warning] Hold expiry vs slow payment
> Atomically move all seats of a still-valid owned hold into PAYMENT_PENDING before authorisation. A longer deadline reduces expiry races but cannot eliminate arbitrary provider delays. After authorisation, conditionally reserve the seats for the order with matching hold ID and state, and durably enqueue capture. Retry capture using its stable PSP operation key; mark the order confirmed only after success. An unknown capture outcome must be reconciled before releasing seats. A definitive failure follows a fenced cancellation/void workflow. PAYMENT_PENDING needs its own recovery process, not blind expiry by the ordinary HELD sweeper.

### General admission
For standing tickets there are no seat ids, just a count. A single `remaining` counter row becomes a hot spot under thousands of decrements a second. **Split** the inventory into N buckets (say 50 rows of 400 tickets each), pick a random bucket and decrement it with `WHERE remaining >= :qty`, falling back to other buckets. With evenly distributed traffic, load per bucket can fall toward 1/N; shared bottlenecks and near-empty buckets reduce the gain. Orders larger than every individual remainder may need atomic multi-bucket allocation.

## Deep dive 2: the virtual waiting room

Without a queue, 2 M people hammer the booking API. The database melts, everyone gets errors, and bots that retry fastest win. A waiting room turns a **thundering herd into a metered stream**.

### How it works
1. Before the sale, fans land on a **static waiting page** served from the CDN.
2. At on-sale time, everyone already waiting gets a **random position**, like a lottery. This removes the incentive to refresh at exactly 10:00:00.000. Later arrivals join the back in arrival order.
3. An **admission controller** releases users at a rate matched to downstream capacity, for example 2,000 per minute, adjusted from live booking latency and error rates.
4. An admitted user receives a **signed, short-lived access token** (a JWT carrying user id, event id and expiry). The booking API and the edge verify it statelessly, with issuer, audience, event, expiry and user/session binding checked. Restrict direct-origin access too; a signature alone does not prevent token sharing or replay.
5. Queue status polling ("you are number 48,213, about 24 min") is answered at the edge from a periodically published counter, not by origin per user.

Cloudflare Waiting Room and Queue-it are commercial versions of this pattern.

### Sizing the admission rate
If mean admitted-user residence is about 5 minutes to shop and pay, and the core comfortably handles 50,000 concurrent shoppers, then Little's law estimates a steady-state admission rate; keep safety margin and adapt to bursts:

```
admit rate = concurrency / time
           = 50,000 / 5 min
           = 10,000 users/min
```

### Bots and fairness
- Pre-registration plus lottery ("Verified Fan"), so only vetted accounts enter the queue.
- One queue position per account, card and device fingerprint.
- CAPTCHA or proof-of-work at the queue entrance, not at checkout, which is too late.
- Per-account ticket limits enforced in the hold transaction.

## Deep dive 3: the seat map

The seat map is read 10–100× more than it's written. Serve it from a cache (Redis, or a per-section document) refreshed every 1–2 s from the inventory database or its change stream. It *will* sometimes show a seat as available that was just taken. That's fine, because the hold's conditional update is the real check, and the UI handles the 409 gracefully ("someone just grabbed that one").

For huge on-sales, offer **"best available"** instead of free picking. The server chooses contiguous seats from a pre-computed list, which cuts contention, because users stop fighting over the same front-row seats.

## Bottlenecks and trade-offs

- **Hot partition**: one event lives on one shard by design, so everything hits that shard during its on-sale. Sub-partitioning by section can spread load, but cross-section orders then require a cross-shard protocol or a product restriction. Keep admissions within measured capacity.
- **Hold duration**: long holds feel kind but lock up inventory, causing "sold out" followed by seats reappearing later. An illustrative range is 5–10 minutes. Little's law sizes the cost: if 600 four-seat holds per minute are destined to be abandoned and each remains allocated for its entire eight-minute lifetime, they occupy 600 x 4 x 8 = 19,200 seats on average in steady state. If counting only time after abandonment, use the remaining lifetime instead. A short initial hold, extended when checkout starts, keeps that down.
- **Strict queue fairness vs throughput**: admitting exactly in order needs a central sequencer. Batched admission (top 2,000 every minute) is nearly as fair and far simpler.
- **Payment provider limits**: the PSP may cap your authorisations per second. The admission rate must respect the *slowest* downstream dependency.

## Evolving at 10x

- **Pre-scale** before known on-sales. Load-test with recorded traffic shapes, and keep the edge configuration (token checks, static pages) able to serve everything if origin is struggling.
- **Lotteries instead of races** for the biggest events: register over days, draw winners, give each a time-boxed purchase window. Peak load becomes a schedule.
- **In-memory inventory**: one single-threaded actor per event section can serialize holds without database row locks. Durable acknowledgments, replicated recovery, fenced ownership and cross-section coordination remain necessary. It's the LMAX-style pattern for extreme contention.
- **Multi-region**: one option is a home write region per event with safe failover; cross-region consensus is another, while catalogue browsing and the waiting room are global.

## Key takeaways
- Don't scale the booking core to the crowd. Use a CDN-served waiting room with random initial positions and signed admission tokens, and admit users at a rate set by downstream capacity (Little's law).
- Make the seat state machine authoritative in one strongly consistent store, with conditional updates (`WHERE status='AVAILABLE' OR hold expired`). All-or-nothing multi-seat holds roll back on any conflict.
- Treat expired holds as available when attempting a new hold, so correctness never depends on a sweeper.
- Close the hold-vs-payment race by authorising, then conditionally marking SOLD with the matching hold id, then durably attempting capture. Reconcile unknown outcomes before releasing inventory, and confirm only after success. Make checkout and PSP operations idempotent within their contracts.
- Use caches freely for seat maps and catalogue pages, and never for the final allocation decision.

## Further reading
- [Cloudflare Waiting Room (developer docs)](https://developers.cloudflare.com/waiting-room/)
- [Building Cloudflare Waiting Room (Cloudflare blog)](https://blog.cloudflare.com/cloudflare-waiting-room/)
- [Ticketmaster system design breakdown (Hello Interview)](https://www.hellointerview.com/learn/system-design/problem-breakdowns/ticketmaster)
- [Explicit locking (PostgreSQL docs)](https://www.postgresql.org/docs/current/explicit-locking.html)
- [Optimistic concurrency control (Wikipedia)](https://en.wikipedia.org/wiki/Optimistic_concurrency_control)
- [How to do distributed locking (Martin Kleppmann)](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html)
