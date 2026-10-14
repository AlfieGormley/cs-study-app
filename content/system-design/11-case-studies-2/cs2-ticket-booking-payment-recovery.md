---
id: cs2-ticket-booking-payment-recovery
title: Ticket checkout recovery
level: advanced
minutes: 3
summary: Keep inventory reserved through ambiguous payment outcomes with durable capture work.
sourceLesson: cs2-ticket-booking
---

> [!warning] Hold expiry vs slow payment
> Atomically move all seats of a still-valid owned hold into PAYMENT_PENDING before authorisation. A longer deadline reduces expiry races but cannot eliminate arbitrary provider delays. After authorisation, conditionally reserve the seats for the order with matching hold ID and state, and durably enqueue capture. Retry capture using its stable PSP operation key; mark the order confirmed only after success. An unknown capture outcome must be reconciled before releasing seats. A definitive failure follows a fenced cancellation/void workflow. PAYMENT_PENDING needs its own recovery process, not blind expiry by the ordinary HELD sweeper.

## The checkout boundary

The earlier seat-hold lesson defines the authoritative inventory transaction. Checkout adds an external service that cannot participate in that same ordinary SQL commit. Treat this as a recoverable protocol with explicit state, rather than keeping a row lock open during a network call.

First, authenticate the shopper and validate that the hold belongs to them. In a short transaction, re-check the exact seat set, owning hold, current state and fresh deadline. Transition the group to PAYMENT_PENDING and record a stable logical checkout identity before contacting the provider. An ordinary expiry sweep must not reclaim that state while an authorisation or capture is unresolved.

Authorisation is not final capture. A provider success can arrive after an HTTP timeout; a timeout is evidence of uncertainty rather than evidence that money did not move. Persist provider operation references and retry with the same stable key only within the provider's documented retention and parameter contract. Query or reconcile ambiguous older operations before making a fresh attempt.

After a definitive authorisation, conditionally reserve the same seats for the order and persist the capture job atomically with the order state. A unique hold-to-order mapping prevents a second order even when another request uses a different API key. The request-fingerprint check separately detects reuse of an existing key with a different payload. Event-ID deduplication does not replace unique references for the business operation.

The durable relay may send capture more than once after a crash. The provider's capture key must identify this one capture, while the database applies its success once. Confirm and issue tickets only after the required success evidence. If capture is definitely rejected, follow the fenced cancellation or void workflow. If its outcome remains unknown, retain an explicit recoverable state and investigate; releasing the seats immediately risks both a payment and a later sale to someone else.

Monitor ageing PAYMENT_PENDING orders, missing relay work, provider-key retention and mismatched settlement records. The state machine needs a liveness policy as well as allocation safety: a forgotten pending order can tie up inventory indefinitely.

## Key takeaways
- PAYMENT_PENDING needs recovery separate from ordinary hold expiry.
- Bind every transition to the owning hold and current state.
- Unique order references and stable provider keys protect different retry boundaries.

## Further reading
- [Explicit locking (PostgreSQL docs)](https://www.postgresql.org/docs/current/explicit-locking.html)
- [How to do distributed locking (Martin Kleppmann)](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html)
