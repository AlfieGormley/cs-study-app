---
id: cs1-notify-volume-channel-cost
title: Estimate notification volume, burst and channel cost
level: intermediate
minutes: 5
summary: Separate channel mix from total volume and campaign bursts.
sourceLesson: cs1-notification-system
---

A notification platform serves very different needs: login codes, order updates, social alerts and large campaigns. The main design problem is deciding which work may wait, which may be dropped, and which channels may be used.

## Separate the workload by policy

Internal services submit a template, recipient, category, priority, allowed channels and expiry. The platform applies current preferences, quiet hours and frequency caps, then tracks acceptance separately from delivery and opening.

An OTP has a short useful lifetime. Marketing can usually be paced over a longer period. Separate queues and workers are useful, but provider quotas, networks and shared stores also need capacity reserved for urgent work.

## Volume does not determine channel cost

Treat user counts, notifications per user, channel shares and campaign deadlines as explicit scenario inputs. The same daily volume can create very different bursts depending on when a campaign is released.

SMS can dominate cost even when it is a small share of messages. Its cost depends on destination, provider, sender, fees and billable segments, not just notification count. Longer text or different encoding can require more segments. Obtain a current quote for a real budget; this lesson does not supply a provider price.

Reduce unnecessary sends and duplicate attempts. A push-first policy with later SMS escalation may help an appropriate workflow, but only with current permission, a valid destination, a useful remaining lifetime and an explicit duplicate-risk policy. Lack of an open event does not prove lack of delivery or attention.

## Retention and recovery

Delivery logs grow with attempts as well as notifications. Include status events, indexes, copies and the required audit and recovery period. Choose retention for product and regulatory needs rather than assuming an arbitrary log duration.

Consent and suppression rules vary by message category and jurisdiction. Build a current policy into send-time checks and verify the applicable requirements against authoritative guidance.

## Key takeaways

- Separate urgent work, campaign bursts and each channel’s constraints.
- Price SMS by billable segments and current provider terms.
- Reduce unnecessary sends without weakening permission or recovery checks.

## Further reading

- [Twilio: SMS encoding and segment limits](https://www.twilio.com/docs/glossary/what-sms-character-limit)
- [Azure: priority queue pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/priority-queue)
