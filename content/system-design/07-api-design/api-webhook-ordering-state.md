---
id: api-webhook-ordering-state
title: Out-of-order webhooks and current state
level: advanced
minutes: 2
summary: Reject stale object versions or serialise authoritative refreshes when notifications arrive out of order.
sourceLesson: api-webhooks-gateways
---

## Problem 4: ordering

Webhooks can arrive **out of order**. Retries, parallel workers and network variation mean `subscription.updated` can arrive before `subscription.created`. Stripe explicitly says it doesn't guarantee delivery order.

Strategies:

- **Use trustworthy per-object versions.** Atomically apply only newer versions. Timestamps work only if their ordering and tie-breaking are reliable for that object; event creation time is not automatically an object version.
- **Treat events as hints ("thin events").** On any event for object X, call `GET /objects/X` to fetch its current state. This avoids applying stale event payloads, but concurrent fetches can still complete out of order. Serialize refreshes per object or apply a trustworthy version check when storing the fetched state. Stripe's newer "thin" events take this approach: the payload contains little more than the id.
- **Strict per-key ordering** on the provider side (one in-flight delivery per object with ordered retries) trades throughput and head-of-line blocking for ordering. A consumer that acknowledges before asynchronous processing must preserve order there too.

| Problem | Consumer fix |
|---|---|
| Fake events | Verify HMAC (raw body) |
| Replays | Signed timestamp + tolerance |
| Duplicates | Dedupe on event id |
| Timeouts | Ack fast, process async |
| Out of order | Version check or re-fetch |
| Missed events | Reconcile via events API |

## Key takeaways
- Retries and parallel delivery can reverse event arrival order.
- Apply trustworthy newer object versions atomically; event timestamps are not automatically versions.
- Treat thin events as refresh hints and protect concurrent fetch completion order.
- Strict per-key ordering trades throughput for blocking and must continue through asynchronous processing.

## Further reading
- [Stripe docs: Receive Stripe events in your webhook endpoint](https://docs.stripe.com/webhooks)
