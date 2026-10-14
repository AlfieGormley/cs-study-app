---
id: cs1-notify-volume-channel-cost
title: Estimate notification volume, burst and channel cost
level: intermediate
minutes: 5
summary: Separate channel mix from total volume and campaign bursts.
sourceLesson: cs1-notification-system
---

Almost every product sends notifications: password reset codes, "your order has shipped", "Sam liked your photo", weekly digests, marketing campaigns. Rather than every team integrating with Apple, Google, Twilio and an email provider separately, companies build one notification platform that every service calls.

The interesting problems aren't sending a message, which is one API call to a provider. They are: never letting a marketing blast delay a login code, minimising duplicate alerts, respecting what users have opted out of, and coping when a provider has an outage.

## Step 1: Requirements

**Functional**

- Internal services send notifications to users via **push** (iOS, Android), **SMS**, **email** and **in-app**.
- Messages are built from **notification templates** with parameters and language localisation (`order_shipped`, `en-GB`).
- **User preferences**: opt in/out per category (security, social, marketing) and per channel; quiet hours in the user's time zone.
- **Scheduling**: send now, or at a given time (including "9 am local time" for each recipient).
- **Bulk campaigns**: send to an audience segment of millions of users.
- **Tracking**: sent, delivered, opened, failed.

**Non-functional**

- **Priority-aware latency**: a one-time passcode (OTP) within a few seconds; social notifications within a minute; marketing within hours is fine.
- **Reliable**: durable retries within a bounded TTL and attempt budget, with deduplication to reduce repeats. Neither delivery nor duplicate-free presentation is guaranteed.
- **Scalable** to billions per day, with large bursts from campaigns.
- **Resilient** to provider outages and rate limits.
- **Compliant**: unsubscribe must work; marketing consent rules (GDPR, PECR in the UK, TCPA in the US) must be honoured.

## Step 2: Estimates

Assume **200 million daily active users** and on average **5 notifications per user per day**.

```formula
total = 200M × 5 = 1B/day
avg = 1B / (10^5 s) ≈ 10,000/s
where
total: notifications per day
avg: average notifications per second
M: million (10^6)
B: billion (10^9)
day: one day; /day means per day
10^5: 100,000, the seconds in a day (86,400) rounded up
s: seconds; /s means per second
≈: approximately equal to (rounded)
In words: 200 million users receiving 5 notifications a day is a billion a day, about 10,000 a second on average.
```

Channel mix, say 85% push, 12% email, 3% SMS. Each channel's rate is its share of the total:

```formula
push = 0.85 × 10,000/s = 8,500/s
email = 0.12 × 10,000/s = 1,200/s
sms = 0.03 × 10,000/s = 300/s
where
push, email, sms: average sends per second on each channel (850 million, 120 million and 30 million a day)
0.85, 0.12, 0.03: each channel's share of all notifications (85%, 12%, 3%)
/s: per second
In words: most of the volume is push; SMS is only 300 a second, but it is the expensive one.
```

Campaigns create bursts on top. Sending to 50M users within an hour adds:

```formula
burst = 50,000,000 / (3,600 s) ≈ 14,000/s
peak = 3 × 10,000/s = 30,000/s
where
burst: extra sends per second from one campaign spread over an hour
3,600 s: the seconds in one hour
peak: the normal daily peak, three times the average
s: seconds; /s means per second
≈: approximately equal to (rounded)
In words: one 50-million-user campaign over an hour adds about 14,000 a second on top of a normal peak of about 30,000 a second.
```

So design for **30–50k/s** peaks.

For an illustrative cost model, assume $0.01 per single-segment SMS, excluding other fees:

```formula
daily = 30M × $0.01 = $300,000
yearly = $300,000 × 365 = $109.5M
where
daily, yearly: SMS spend per day and per 365-day year
M: million
$: US dollars
In words: 30 million texts a day at a cent each costs $300,000 a day, about $110 million a year.
```

So 30M/day costs $300,000/day, or $109.5M per 365-day year. Actual rates depend on destination, provider, sender and segment count. Reducing unnecessary SMS and duplicates matters.

> **Content gap:** no current provider quote or production throughput benchmark is supplied. Rates and capacity here are scenario assumptions, not measured service characteristics.

Storage for the notification log at ~500 B (bytes) per record:

```formula
daily = 1 bn × 500 B = 500 GB
kept = 500 GB × 90 = 45 TB
where
daily: new log data per day
kept: data held with 90-day retention (records older than 90 days deleted)
bn: billion (10^9) records per day
B: bytes
GB: gigabyte, 10^9 bytes
TB: terabyte, 10^12 bytes (1,000 GB)
In words: a billion 500-byte records a day is 500 GB a day, and keeping 90 days of them takes 45 TB.
```

## Key takeaways

- Separate channel mix from total volume and campaign bursts.
- Use an explicitly hypothetical per-segment SMS rate.
- Include log retention and duplicate reduction in the capacity and cost model.

## Further reading

- [Twilio: SMS encoding and segment limits](https://www.twilio.com/docs/glossary/what-sms-character-limit)
- [Azure: priority queue pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/priority-queue)
