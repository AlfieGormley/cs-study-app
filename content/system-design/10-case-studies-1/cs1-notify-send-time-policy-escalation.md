---
id: cs1-notify-send-time-policy-escalation
title: Apply send-time policy, tracking and channel escalation
level: intermediate
minutes: 5
summary: Re-check current permissions and TTL when delayed work executes.
sourceLesson: cs1-notification-system
---

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
- **Cost vs reach**: SMS can reach many users without an installed app, but needs a reachable SMS-capable number and incurs charges. Push generally has low marginal provider cost but still has infrastructure costs and requires a usable app/device registration. A common pattern is *channel escalation*: send push, and only if it isn't opened within a set time (say 10 minutes), send SMS.

## Recoverable channel escalation

After a push attempt, persist a delayed job for the SMS decision. At execution, check the latest open status, SMS permission, destination and TTL, then atomically claim a recoverable attempt. Two workers running a plain check-then-send can both send. The job must survive worker restarts; sleeping in a sender for ten minutes cannot provide that recovery. Local records reduce repeats, while provider idempotency or reconciliation is needed for ambiguous external outcomes.

## At 10x scale

At ten billion notifications a day, compute the average with the same rounded-day shortcut. Assume a campaign-inclusive peak factor of five for this scenario:

```formula
r_avg = 10 bn / (100,000 s) = 100,000/s
r_peak = 5 × r_avg = 500,000/s
where
r_avg: average notifications per second
r_peak: hypothetical campaign-inclusive peak per second
bn: billion, one thousand million
s: seconds; /s means per second
5: assumed peak factor; actual campaign scheduling can produce a different peak
In words: ten billion a day is about 100,000 a second on this shortcut; the assumed peak is five times that.
```

- **Partition everything by `user_id`**: Kafka partitions, the log, and preference caches, to improve locality. Kafka ordering is per partition within a topic; separate priorities/channels, parallel senders and providers do not guarantee end-to-end user-visible order.
- **Regional deployments** close to users and providers, with each region sending for its own users.
- **Multiple usable providers where the channel supports alternatives**, with weighted routing based on cost, latency and live error rates.
- **Aggregation and digests** become essential for user experience: batch low-value social notifications into periodic summaries, which also cuts volume dramatically.
- **Smarter send-time**: pick the hour each user is most likely to engage, spreading campaigns naturally over the day.

## Key takeaways

- Re-check current permissions and TTL when delayed work executes.
- Use IANA time zones rather than fixed UTC offsets for local schedules.
- Track acceptance, delivery and opens as distinct, imperfect signals.
- Persist escalation jobs and suppress unnecessary SMS before starting the attempt.

## Further reading

- [RFC 8058: one-click unsubscribe](https://www.rfc-editor.org/rfc/rfc8058.html)
- [Gmail: sender guidelines](https://support.google.com/mail/answer/81126)
- [Twilio: SMS encoding and segment limits](https://www.twilio.com/docs/glossary/what-sms-character-limit)
