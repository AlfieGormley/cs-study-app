---
id: api-webhook-durable-delivery
title: Durable webhook processing and retries
level: advanced
minutes: 3
summary: Acknowledge persisted events quickly, deduplicate effects and isolate provider delivery workloads.
sourceLesson: api-webhooks-gateways
---

A valid notification can still be duplicated, delayed or missed. Treat signature verification as the start of a durable processing path, then account for both consumer and provider failures.

## Problem 3: delivery failures and retries

Your endpoint will sometimes be down, slow or buggy. Many providers retry failed delivery with backoff, so duplicates are possible. Bounded retry windows do not guarantee that every event is eventually delivered. Stripe retries for up to **3 days** in live mode (far less in test mode); GitHub doesn't retry failed deliveries automatically, but lets you redeliver them from the UI or API.

What this means for you as a consumer:

- **Respond 2xx quickly**, within a few seconds. Providers time out (GitHub asks for a 2xx within 10 seconds) and treat slow responses as failures. Providers with automatic retries can then send duplicates; GitHub instead supports explicit redelivery.
- **Do the work asynchronously.** Verify the signature, write the event to a queue or table, return `200`, then process. Your downstream outage then doesn't become a webhook failure.
- **Be idempotent.** You *will* receive the same event more than once. Deduplicate on the authenticated event identity, in the same transaction as a local database side effect. External effects need downstream idempotency or reconciliation; a local transaction cannot atomically commit a remote API call.

This SQL fragment needs the actual order predicate and a branch on the inserted-row count. The following is transaction pseudocode, not a complete handler.

```sql
BEGIN;
-- Commit event identity with its local
-- effect.
INSERT INTO processed_events(id)
  VALUES ('evt_1Nq')
  ON CONFLICT DO NOTHING;
-- if 0 rows inserted: duplicate,
--   COMMIT and return
UPDATE orders SET paid = true ...;
COMMIT;
```

As a **provider**, you need:

- A durable outbox of events, a delivery worker pool, and per-endpoint retry schedules (e.g. 1 min, 5 min, 30 min, 2 h, 8 h...).
- **Auto-disable** endpoints that fail for days, and email the owner.
- **Isolation** between customers, so one customer's slow endpoint doesn't block deliveries to everyone else.
- An **events API** (`GET /events`) so consumers can reconcile anything missed. Webhooks should be a notification channel, not the only source of truth.

## Key takeaways
- Persist a verified event before acknowledging, then process asynchronously.
- Commit local deduplication with the effect; remote effects need their own protection.
- Provider retries are bounded and provider-specific, so reconcile gaps rather than waiting indefinitely.
- Providers need durable outboxes, per-endpoint schedules and isolation from slow customers.

## Further reading
- [Stripe docs: Receive Stripe events in your webhook endpoint](https://docs.stripe.com/webhooks)
- [GitHub docs: Best practices for using webhooks](https://docs.github.com/en/webhooks/using-webhooks/best-practices-for-using-webhooks)
- [Standard Webhooks specification](https://github.com/standard-webhooks/standard-webhooks/blob/main/spec/standard-webhooks.md)
