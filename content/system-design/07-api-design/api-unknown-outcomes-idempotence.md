---
id: api-unknown-outcomes-idempotence
title: Unknown outcomes and idempotent intent
level: intermediate
minutes: 2
summary: Distinguish delivery guarantees from business effects and favour naturally repeatable operations.
sourceLesson: api-idempotency
---

In a distributed system, every network call has three possible outcomes: success, failure, and **unknown**. The unknown case, a timeout, is the hard one. Did the server do the work or not?

An unknown outcome can be resolved by querying/reconciling operation status, or by retrying under an **idempotency contract**: repeating the logical operation has the same intended effect as doing it once. Do not blindly repeat an operation whose outcome remains ambiguous.

## Why "exactly once" is really "at least once + idempotent"

You can't guarantee a message is *delivered* exactly once over an unreliable network. You can only choose:

- **At most once**: never retry. Some requests are lost.
- **At least once**: retry until acknowledged. Some requests are duplicated.

One way to obtain an effectively-once business effect is at-least-once delivery plus atomic deduplication with the effect. Delivery, processing and external side effects are different guarantees. Systems such as Kafka idempotent producers and SQS FIFO have specific scopes and retention windows; no claim applies to every payment API or arbitrary external effect. (The messaging module goes deeper on delivery guarantees.)

## Naturally idempotent operations

Some operations are idempotent by design:

| Operation | Idempotent? |
|---|---|
| `SET balance = 110` | Yes |
| `balance = balance + 10` | No |
| `PUT /users/7 {...}` | Yes |
| `DELETE /users/7` | Yes |
| `POST /payments` | No |
| `INSERT ... ON CONFLICT DO NOTHING` | Yes |

Where you can, design operations to be naturally idempotent. Use absolute values instead of deltas. Let the client choose the resource id and use `PUT /orders/{client-uuid}` instead of `POST /orders`.

But many operations are inherently "do something": charge a card, send an email, ship a parcel. For those you need an **idempotency key**.

## Key takeaways
- Timeouts reveal no authoritative completion result; reconcile or use a retry contract.
- At-least-once delivery needs atomic deduplication to produce an effectively-once local effect.
- Absolute assignments and client-chosen resource identities can avoid non-idempotent deltas.

## Further reading
- [AWS Builders' Library: Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)
- [Stripe API: Idempotent requests](https://docs.stripe.com/api/idempotent_requests)
