---
id: api-idempotency-atomic-recovery
title: Atomic claims and crash recovery
level: intermediate
minutes: 3
summary: Prevent concurrent duplicates and resume multi-step effects without guessing remote outcomes.
sourceLesson: api-idempotency
---

## Implementing it correctly

The naïve version has a race. Two retries arrive at the same time on different servers. Both check "does K exist?", both see "no", and both charge the card.

The fix is to **claim the key atomically before doing the work**:

```
1. INSERT INTO idem_keys
     (key, account, req_hash,
      status='started')
   -- unique on (account, key)
   -- if conflict: go to step 5
2. Do the work (charge card)
3. UPDATE idem_keys SET
     status='done', code=201,
     body='{...}'
4. Return 201
5. Existing row?
   - req_hash differs -> 422
   - status 'started' -> 409
   - status 'done'    -> replay
```

Key details:

- **Scope keys per account** (or per API key). Otherwise two customers who happen to pick the same key collide.
- **Fingerprint the operation** (method/route and semantically relevant parameters as well as the body) to reject key reuse for a different intent; canonicalization and key scope must be defined.
- **Handle crashes in step 2.** If the server dies after charging but before step 3, the row is stuck in `started`. Recovery needs either authoritative downstream reconciliation that accounts for still-pending work, or making step 2 itself idempotent under the downstream's key scope and retention contract. A timeout or an eventually consistent not-found result alone does not authorise another charge.

## Atomic phases

Brandur Leach, formerly of Stripe, describes going further for multi-step operations, implemented in Postgres. The work is split into **atomic phases**, each a single database transaction, with a **recovery point** recorded after each one. A retry resumes from the last recovery point rather than starting over.

```
started
  | tx1: create charge row
  v
charge_created
  | call card network
  |  (pass idem key downstream)
  v
card_charged
  | tx2: mark paid, enqueue email
  v
finished
```

Foreign calls (to the payment downstream) happen *between* transactions. Repeating a call is safe only when that downstream enforces the forwarded key under a documented scope and retention contract. Side effects like emails are enqueued atomically with the state change (the **transactional outbox** pattern). The relay can deliver twice; exactly-once external effects additionally require recipient-side deduplication or an idempotent sending API.

For a local credit, insert a unique processed-message id and update the balance in the same database transaction. A duplicate id prevents the credit from committing twice. Acknowledging the message after that commit allows crash redelivery without repeating the local effect.

## Key takeaways
- Claim a scoped key atomically before work and fingerprint the operation.
- Local recovery points do not atomically commit a remote charge; use downstream idempotency or reconciliation.
- Commit a deduplication marker with a local effect in one transaction.
- An outbox protects local recording; its relay still needs recipient deduplication for external effects.

## Further reading
- [Brandur Leach: Implementing Stripe-like idempotency keys in Postgres](https://brandur.org/idempotency-keys)
- [AWS Builders' Library: Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)
