---
id: cs1-notify-isolation-dedup-campaigns
title: Isolate critical traffic and reduce duplicate notifications
level: intermediate
minutes: 4
summary: Separate worker pools and reserve shared provider capacity for critical work.
sourceLesson: cs1-notification-system
---

## Deep dive 1: Priority and isolation

A 50-million-user marketing campaign must not delay a password reset code. Achieve that with **isolation**, not just ordering:

- **Separate topics or queues per priority** (`critical`, `high`, `low`), each with its **own worker pool**. This avoids head-of-line blocking in the critical pool; shared stores, networks and provider quotas still need capacity protection.
- **Reserved provider capacity.** Providers rate-limit you (e.g. SMS throughput per sender number, APNs and FCM throttling per app). Reserve a share of each provider's capacity for critical traffic so campaigns can't consume it all.
- **Throttle campaigns at the source.** The campaign scheduler expands a segment into messages gradually (say, 20k/s) rather than dumping 50M into the queue at once. At 20k/s, 50M messages take about 42 minutes (50,000,000 / 20,000 per second = 2,500 s); that makes expansion load explicit; only an expansion rate no higher than downstream reserved provider capacity keeps queue lag bounded and stays within provider limits. Expand the segment in pages (cursor over the user table or a precomputed segment file) so the scheduler can pause, resume after a crash without resending, and be cancelled if the campaign has a mistake.

A single queue with a priority field is weaker: a consumer working through a 50M-message backlog won't see a new critical message until it reaches it, unless the broker supports true priority ordering, and even then the providers are shared.

## Deep dive 2: Deduplication and idempotency

Duplicates come from three places:

1. **Producer retries**: the order service times out and calls the API again.
2. **Queue redelivery**: Kafka and SQS are at-least-once; a worker that crashes after processing but before committing its offset sees the message again.
3. **Provider retries**: a timeout calling Twilio, where the SMS was in fact sent.

Defences, layered:

- **Idempotency key at the API**: atomically insert a unique key with the notification record and outbox entry in the same durable store. A repeat returns the existing ID. A Redis `SET NX` followed separately by enqueueing can lose the notification if the process crashes between them.
- **Per-destination send records**: key by notification, channel and destination (including device), claim an attempt with a recoverable lease/state machine, and mark it sent only after provider acknowledgement. Use a provider-enforced idempotency key when available. A pre-send `sent` flag can lose work; a post-send flag alone leaves an ambiguous crash window.
- **Content-level dedup**: also suppress near-identical notifications to the same user within a short window ("Sam liked your photo" five times becomes one, or an aggregated "Sam and 4 others liked your photo"). Hold low-priority social events for a short window (say a minute) keyed by `user_id + event type + object`, then send one aggregated message. APNs supports coalescing with `apns-collapse-id`. FCM `collapse_key` replaces a matching message that has not yet been delivered; it does not itself replace every already displayed notification. Use platform display identifiers where replacement of visible alerts is required.

A per-user frequency cap for social alerts can bound noise from distinct events even when none is a duplicate. Keep the individual events in the in-app inbox while grouping or suppressing external pushes. The cap needs explicit interval semantics, just like the rate limiter.

> [!warning] Exactly-once is not achievable end to end
> If the sender crashes after the provider accepted the SMS but before recording it, the retry sends it again. You can shrink this window, and some providers accept idempotency keys, but without a provider-enforced idempotency contract the ambiguous outcome remains. Finite TTLs and retry budgets can also leave messages undelivered. Decide explicitly which notification types tolerate duplicates.

## Key takeaways

- Separate worker pools and reserve shared provider capacity for critical work.
- Throttle campaign expansion and make cursor progress recoverable.
- Deduplicate at API, destination and content levels without promising exactly-once external effects.

## Further reading

- [AWS: transactional outbox pattern](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)
- [Firebase: collapsible message types](https://firebase.google.com/docs/cloud-messaging/customize-messages/collapsible-message-types)
- [Azure: priority queue pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/priority-queue)
