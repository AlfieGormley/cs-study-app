---
id: cs1-notification-system
title: Design a notification system
level: intermediate
minutes: 17
summary: Design a multi-channel notification platform (push, SMS, email, in-app) with templating, user preferences, priority queues, deduplication, retries and provider failover.
---

Almost every product sends notifications: password reset codes, "your order has shipped", "Sam liked your photo", weekly digests, marketing campaigns. Rather than every team integrating with Apple, Google, Twilio and an email provider separately, companies build one notification platform that every service calls.

The interesting problems aren't sending a message, which is one API call to a provider. They are: never letting a marketing blast delay a login code, minimising duplicate alerts, respecting what users have opted out of, and coping when a provider has an outage.

## Step 1: Requirements

**Functional**

- Internal services send notifications to users via **push** (iOS, Android), **SMS**, **email** and **in-app**.
- Messages are built from **templates** with parameters and localisation (`order_shipped`, `en-GB`).
- **User preferences**: opt in/out per category (security, social, marketing) and per channel; quiet hours in the user's time zone.
- **Scheduling**: send now, or at a given time (including "9 am local time" for each recipient).
- **Bulk campaigns**: send to a segment of millions of users.
- **Tracking**: sent, delivered, opened, failed.

**Non-functional**

- **Priority-aware latency**: a one-time passcode (OTP) within a few seconds; social notifications within a minute; marketing within hours is fine.
- **Reliable**: durable retries within a bounded TTL and attempt budget, with deduplication to reduce repeats. Neither delivery nor duplicate-free presentation is guaranteed.
- **Scalable** to billions per day, with large bursts from campaigns.
- **Resilient** to provider outages and rate limits.
- **Compliant**: unsubscribe must work; marketing consent rules (GDPR, PECR in the UK, TCPA in the US) must be honoured.

## Step 2: Estimates

Assume **200 million daily active users** and on average **5 notifications per user per day**.

```
Total:   200M x 5 = 1B/day
Average: 1B / 10^5 s ≈ 10,000/s
```

Channel mix, say 85% push, 12% email, 3% SMS:

```
Push:  850M/day ≈ 8,500/s
Email: 120M/day ≈ 1,200/s
SMS:    30M/day ≈   300/s
```

Campaigns create bursts on top: sending to 50M users within an hour adds ~14,000/s. With a normal 3x daily peak of ~30k/s, design for **30–50k/s** peaks.

For an illustrative cost model, assume $0.01 per single-segment SMS, excluding other fees: 30M/day costs $300,000/day, or $109.5M per 365-day year. Actual rates depend on destination, provider, sender and segment count. Reducing unnecessary SMS and duplicates matters.

> **Content gap:** no current provider quote or production throughput benchmark is supplied. Rates and capacity here are scenario assumptions, not measured service characteristics.

Storage for the notification log at ~500 B per record:

```
1B x 500 B = 500 GB/day
90-day retention ≈ 45 TB
```

## Step 3: API

```
POST /v1/notifications
{
  "idempotencyKey": "order-8812-shipped",
  "userId": "u_123",
  "template": "order_shipped",
  "params": {"orderId": "8812"},
  "category": "transactional",
  "priority": "high",
  "channels": ["push", "email"],
  "sendAt": null,
  "ttlSeconds": 86400
}
-> 202 Accepted {notificationId}
```

Notes:

- **202 Accepted** explicitly represents work accepted for asynchronous processing. A 200 response can also describe a successful enqueue operation under another API contract; it does not inherently mean delivered.
- `idempotencyKey` is required. The order service might retry; the same key must not produce a second notification.
- `ttlSeconds` says when the notification becomes pointless. Stop initiating retries at expiry, request provider-side expiry where supported, and enforce OTP validity on the server: an already queued SMS may still arrive late.
- Campaigns use a separate endpoint that takes a **segment** and a schedule, rather than millions of individual calls.

## Step 4: Data model

```
devices
  user_id, device_id (PK)
  platform (ios|android|web)
  push_token, app_version
  last_seen

preferences
  user_id, category, channel (PK)
  enabled, updated_at
  + timezone, quiet_hours per user

templates
  name, channel, locale, version (PK)
  subject, body (with placeholders)

notifications (log)
  user_id, created_at, notification_id (PK)
  idempotency_key, template, channel
  status, attempts, provider_msg_id
  created_at, sent_at, delivered_at
```

Devices and preferences are read on every send, so cache them (Redis, or in-memory in workers) keyed by `user_id`. The notification log is write-heavy and queried by `user_id` and time ("what did we send this user?"), which suits Cassandra or DynamoDB partitioned by `user_id` with a time-ordered sort key.

## Step 5: High-level design

```
 Producers (auth, orders,
 social, campaign scheduler)
          |
          v
 Notification API
 (validate, idempotency)
          |
          v
 Kafka: critical | high | low
          |
          v
 Processor workers
 (prefs, caps, template)
          |
   +------+------+------+
   v      v      v      v
  push   sms   email  in-app
 queue  queue  queue  queue
   |      |      |      |
   v      v      v      v
 APNs/  Twilio/ SES/  websocket
 FCM    Vonage  SendGrid / inbox
```

1. The **API** validates the request, atomically claims the idempotency key and writes an `accepted` record plus an outbox event; a relay publishes that event to the priority topic.
2. **Processor workers** load the user's preferences and devices, drop channels the user has opted out of, apply frequency caps and quiet hours, render the template for each channel and locale, and enqueue one message per channel.
3. **Channel senders** call the providers, record the result, and handle retries.
4. **Webhooks** from providers (delivery receipts, bounces, unsubscribes) flow back into the log and the preferences store.

Each stage is separately scalable, and a slow email provider primarily backs up its own queue. Shared databases, networks and quotas also need isolation.

## Deep dive 1: Priority and isolation

A 50-million-user marketing campaign must not delay a password reset code. Achieve that with **isolation**, not just ordering:

- **Separate topics or queues per priority** (`critical`, `high`, `low`), each with its **own worker pool**. This avoids head-of-line blocking in the critical pool; shared stores, networks and provider quotas still need capacity protection.
- **Reserved provider capacity.** Providers rate-limit you (e.g. SMS throughput per sender number, APNs and FCM throttling per app). Reserve a share of each provider's capacity for critical traffic so campaigns can't consume it all.
- **Throttle campaigns at the source.** The campaign scheduler expands a segment into messages gradually (say, 20k/s) rather than dumping 50M into the queue at once. At 20k/s, 50M messages take about 42 minutes; that keeps queue lag predictable and stays within provider limits. Expand the segment in pages (cursor over the user table or a precomputed segment file) so the scheduler can pause, resume after a crash without resending, and be cancelled if the campaign has a mistake.

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

> [!warning] Exactly-once is not achievable end to end
> If the sender crashes after the provider accepted the SMS but before recording it, the retry sends it again. You can shrink this window, and some providers accept idempotency keys, but without a provider-enforced idempotency contract the ambiguous outcome remains. Finite TTLs and retry budgets can also leave messages undelivered. Decide explicitly which notification types tolerate duplicates.

## Deep dive 3: Retries and failures

Classify every provider response:

| Response | Action |
|---|---|
| 2xx accepted | Record provider acceptance, not delivery/read |
| Retryable errors / ambiguous timeout | Back off; reconcile or use provider idempotency, then apply duplicate-risk policy |
| Invalid token / number | Don't retry; clean up |
| Unsubscribed / blocked | Don't retry; update prefs |

- **Exponential backoff with jitter**: wait ~1 s, 2 s, 4 s, 8 s... each randomised, so thousands of failed messages don't retry in lockstep and hammer a recovering provider.
- **Respect the TTL**: if the notification's `ttlSeconds` has passed, drop it instead of retrying. A late OTP is worse than none.
- **Dead-letter queue**: after N attempts, move the message to a DLQ for inspection rather than retrying forever.
- **Token hygiene**: APNs tells you when a device token is no longer valid (HTTP 410 for an unregistered device), and FCM returns an `UNREGISTERED` error. Deactivate the affected registration; for APNs, compare its invalidation timestamp with the latest registration so an old response cannot invalidate a newer registration. Apply FCM token-lifecycle guidance separately.
- **Circuit breakers and failover**: if one SMS provider's error rate spikes, open a circuit breaker and route to a secondary provider. Email can similarly fail over between configured providers. Secondary routes need approved senders, capacity and appropriate consent; ambiguous primary outcomes can cause duplicates across providers. Push can't fail over (only Apple can deliver to iPhones), so you queue and retry.

## Deep dive 4: Preferences, caps and quiet hours

Check preferences **at send time**, not when the request is accepted. A scheduled notification created last week must respect an opt-out made yesterday.

- **Categories**: the product may require essential security notifications; marketing must be opt-in in many jurisdictions; social is user-controlled.
- **Frequency caps**: "no more than 3 marketing pushes per user per day". This is a rate limiter keyed by `user_id:category`; choose explicit calendar-day or rolling-window semantics. A token bucket controls bursts and refill rate, not necessarily a strict daily maximum.
- **Quiet hours**: if a low-priority push would land at 3 am in the user's time zone, delay it to 8 am. Critical messages bypass quiet hours.
- **"9 am local" scheduling**: don't create a timer per user. Bucket recipients by IANA time-zone identifier and calculate the next local 9 am using current time-zone rules; a UTC offset alone does not capture daylight-saving changes. A 50M-user send then becomes scheduled regional waves across the day, which also smooths provider load.
- **Unsubscribe**: provide the opt-out mechanism required for the message and jurisdiction. Gmail requires one-click unsubscribe for marketing/subscription mail from senders exceeding its bulk threshold (over 5,000 messages/day to personal Gmail accounts). RFC 8058 defines the mechanism. This design targets prompt suppression within seconds; applicable legal deadlines and exceptions differ.

## Deep dive 5: Templates and tracking

Templates are versioned per channel and locale, because the same `order_shipped` event becomes a 4 KB-limited push payload, a single-part SMS of up to 160 GSM-7 septets or 70 UTF-16 code units (some characters use multiple units); concatenated messages usually allow 153 or 67 units per part and a rich HTML email. Render in the processor workers, validate parameters at the API (a missing `orderId` should fail fast with a 400, not produce "Your order {orderId} has shipped" for a million users), and keep old versions so in-flight messages render consistently.

Tracking uses provider callbacks: Twilio status webhooks, SES events, APNs/FCM responses. App events can report push opens. Email pixels and link redirects provide imperfect engagement signals: image blocking, proxy prefetching and automated link scans can distort them. Authenticate callbacks, deduplicate events and handle out-of-order updates. APNs acceptance is not a delivery/read receipt; preserve distinct status meanings in the log.

## Bottlenecks and trade-offs

- **Provider rate limits**, not your own servers, are usually the ceiling. Know them and shape traffic to them.
- **Preference lookups** at 50k/s need caching; accept that a preference change can take a few seconds to apply, with a freshly checked suppression state before marketing sends. Cache invalidation alone does not eliminate races with in-flight sends.
- **Fan-out from campaigns** can swamp shared stores. Throttle at the scheduler.
- **Cost vs reach**: SMS can reach many users without an installed app, but needs a reachable SMS-capable number and incurs charges. Push generally has low marginal provider cost but still has infrastructure costs and requires a usable app/device registration. A common pattern is *escalation*: send push, and only if it isn't opened within N minutes, send SMS.

## At 10x scale

At 10 billion notifications/day (~100k/s average, ~500k/s peak):

- **Partition everything by `user_id`**: Kafka partitions, the log, and preference caches, to improve locality. Kafka ordering is per partition within a topic; separate priorities/channels, parallel senders and providers do not guarantee end-to-end user-visible order.
- **Regional deployments** close to users and providers, with each region sending for its own users.
- **Multiple providers per channel** with weighted routing based on cost, latency and live error rates.
- **Aggregation and digests** become essential for user experience: batch low-value social notifications into periodic summaries, which also cuts volume dramatically.
- **Smarter send-time**: pick the hour each user is most likely to engage, spreading campaigns naturally over the day.

## Key takeaways

- Accept requests asynchronously (202) with a mandatory idempotency key and a TTL.
- Isolate priorities with separate queues, worker pools and reserved provider capacity so campaigns can't delay OTPs.
- Layer deduplication: idempotency keys at the API, per-channel send records, content-level collapsing. Exactly-once external effects require a provider-enforced contract; do not promise them from local deduplication alone.
- Retry only retryable errors, with exponential backoff and jitter, honour the TTL, and dead-letter what keeps failing.
- Check preferences, caps and quiet hours at send time; target prompt suppression and account for already in-flight sends.
- Provider limits and costs, not your servers, usually shape the design.

## Further reading

- [Apple: sending notification requests to APNs](https://developer.apple.com/documentation/usernotifications/sending-notification-requests-to-apns)
- [Firebase Cloud Messaging documentation](https://firebase.google.com/docs/cloud-messaging)
- [Firebase: best practices for FCM registration token management](https://firebase.google.com/docs/cloud-messaging/manage-tokens)
- [AWS Builders' Library: timeouts, retries and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
- [Azure Architecture Center: priority queue pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/priority-queue)
- [RFC 8058: one-click unsubscribe](https://www.rfc-editor.org/rfc/rfc8058)
