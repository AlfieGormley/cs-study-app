---
id: msg-consumer-dedup-transactions
title: Make database consumer effects idempotent
level: advanced
minutes: 3
summary: Use absolute state, atomic deduplication and versions to tolerate retries and replay.
sourceLesson: msg-delivery-semantics
---

Delivery can repeat even when the application must apply an effect once. Keep the evidence that an effect happened beside the effect itself, so neither can commit alone.

## Idempotent consumers

An operation is **idempotent** if applying it twice has the same effect as applying it once. Design consumers so a redelivered message does no harm.

### 1. Naturally idempotent operations

Some operations are idempotent by construction:

| Not idempotent | Idempotent |
|---|---|
| `balance += 10` | `SET status='SHIPPED'` |
| `INSERT` new row | `UPSERT` by natural key |
| Send email | Provider-enforced dedup key |

Prefer **absolute state** ("order 17 is shipped") over **deltas** ("add one to shipped count") in message design where you can.



### 2. Deduplication by message ID

When the operation is not naturally idempotent, record which messages you have processed, **in the same transaction as the effect**:

This SQL fragment assumes `processed_messages.id` is a primary key and account 42 exists. The application must roll back a failed transaction before acknowledging a duplicate.

```sql
BEGIN;
-- Claim the ID beside its database effect.
INSERT INTO processed_messages(id)
  VALUES ('msg-8f3a'); -- PK: fails if seen
-- This addition is safe only with the
-- claim.
UPDATE accounts SET balance = balance + 10
  WHERE id = 42;
-- Commit both the claim and effect
-- together.
COMMIT;
```

If the message is redelivered, the insert violates the primary key, the transaction rolls back, and the consumer acks the duplicate. Because the dedup record and the effect commit atomically, there is no window where one exists without the other.

> [!warning] Dedup outside the transaction is racy
> "Check Redis for the ID, do the work, then write the ID to Redis" fails two ways: a crash after the work but before the Redis write causes a duplicate, and two consumers receiving the same message concurrently both see "not processed". Use an atomic claim (a unique insert, or Redis `SET key NX`) and make the effect itself safe to retry.

The ID must be stable across retries. Use a producer-assigned ID (an event ID or a business-operation key; orderId + eventType is only sufficient if that event type can occur once per order), **not** the broker's delivery ID, which may change on redelivery.

Keep deduplication state for the full permitted duplicate horizon, including delayed retries, archives and replay duration. Permanent business records may be appropriate when no reliable finite bound exists.



### 3. Version checks

For state updates, include a version or sequence number and apply only if it is newer:

The named values are application-bound parameters, not standalone PostgreSQL syntax. Inspect affected rows: a stale or equal version makes no change.

```sql
-- Replace only an older absolute snapshot.
UPDATE profiles SET email = :email,
       version = :v
 WHERE id = :id AND version < :v;
```

For absolute state snapshots with a single ordered version domain, this rejects stale updates. It does not safely skip missing deltas; initialise absent rows and coordinate versions across writers.

## Key takeaways

- Absolute state writes can be naturally idempotent, subject to stale updates and external side effects.
- Store a stable event or operation ID in the same database transaction as a non-idempotent effect.
- Deduplication retention must cover every permitted retry and replay, rather than only normal redelivery.
- Version checks protect snapshots from older writes; they do not safely skip missing deltas.

## Further reading

- [Idempotent Receiver (Enterprise Integration Patterns)](https://www.enterpriseintegrationpatterns.com/patterns/messaging/IdempotentReceiver.html)
- [Making retries safe with idempotent APIs (Amazon Builders' Library)](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)
- [PostgreSQL constraints](https://www.postgresql.org/docs/current/ddl-constraints.html)
