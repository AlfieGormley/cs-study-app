---
id: cs1-notify-accept-outbox-pipeline
title: Accept recoverable work into an asynchronous pipeline
level: intermediate
minutes: 3
summary: 202 means accepted work rather than confirmed delivery.
sourceLesson: cs1-notification-system
---

The sizing scenario reaches billions of notifications a day across push, SMS, email and in-app channels. This unit connects the producer contract to recoverable queued work, preferences and delivery records.

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
- Campaigns use a separate endpoint that takes an **audience segment** and a schedule, rather than millions of individual calls.

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

## Key takeaways

- 202 means accepted work rather than confirmed delivery.
- Claim idempotency with the accepted record and outbox in one durable transaction.
- Keep channel senders and provider callbacks as separately recoverable stages.

## Further reading

- [AWS: transactional outbox pattern](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)
- [RFC 9110: 202 Accepted](https://www.rfc-editor.org/rfc/rfc9110.html#section-15.3.3)
