---
id: msg-external-idempotency-publish-retries
title: Idempotency keys and producer retry limits
level: advanced
minutes: 2
summary: Protect external effects and recognise the finite scope of broker-side deduplication.
sourceLesson: msg-delivery-semantics
---

When a consumer calls another system, its local transaction cannot include that remote effect. The provider must recognise repeated attempts, and the caller must respect how long that recognition lasts.

## Idempotency keys for side effects

When the effect is a call to an external system (charging a card, sending an SMS), pass an **idempotency key** derived from the message. Stripe API v1, for example, accepts an `Idempotency-Key` header and returns the original result for a repeated key; it keeps keys for at least 24 hours. The external system does the dedup for you, but only within its own retention window, so a retry after pruning may be a fresh request. If the earlier outcome is uncertain, reconcile it before retrying outside that window.



## Producer-side duplicates

Duplicates also start at the producer. A publish times out, the producer retries, and the broker ends up with two copies.

- **SQS FIFO** deduplicates on `MessageDeduplicationId` (or a SHA-256 of the body with content-based deduplication) for a **5-minute** window.
- **Kafka idempotent producer** (default since 3.0): each producer has a producer ID and a per-partition sequence number. The broker rejects duplicates and out-of-order sequence numbers. This removes retry duplicates **within one producer session**, but a restarted producer gets a new ID.

## Key takeaways

- An external provider’s idempotency key must represent the same business operation on every attempt.
- A local claim row cannot alone make a remote effect atomic; retries still need the same provider key.
- Broker deduplication and provider keys have finite boundaries; uncertain outcomes beyond them need reconciliation.

## Further reading

- [Making retries safe with idempotent APIs (Amazon Builders' Library)](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)
- [Stripe idempotent requests](https://docs.stripe.com/api/idempotent_requests)
