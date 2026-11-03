---
id: cs1-notify-retry-token-failover
title: Handle retryable failures and invalid registrations
level: intermediate
minutes: 3
summary: Classify provider acceptance, invalid destinations and ambiguous outcomes separately.
sourceLesson: cs1-notification-system
---

## Deep dive 3: Retries and failures

Classify every provider response:

| Response | Action |
|---|---|
| 2xx accepted | Record provider acceptance, not delivery/read |
| Retryable errors / ambiguous timeout | Back off; reconcile or use provider idempotency, then apply duplicate-risk policy |
| Invalid token / number | Don't retry; clean up |
| Unsubscribed / blocked | Don't retry; update prefs |

- **Exponential backoff with jitter**: wait ~1 s, 2 s, 4 s, 8 s... each randomised, so thousands of failed messages don't retry in lockstep and hammer a recovering provider .
- **Respect the TTL**: if the notification's `ttlSeconds` has passed, drop it instead of retrying. A late OTP is worse than none.
- **Dead-letter queue**: after a fixed number of attempts (say 5), move the message to a DLQ for inspection rather than retrying forever.
- **Token hygiene**: APNs tells you when a device token is no longer valid (HTTP 410 for an unregistered device), and FCM returns an `UNREGISTERED` error. Deactivate the affected registration; for APNs, compare its invalidation timestamp with the latest registration so an old response cannot invalidate a newer registration. Apply FCM token-lifecycle guidance separately.
- **Circuit breakers and failover**: if one SMS provider's error rate spikes, open a circuit breaker and route to a secondary provider. Email can similarly fail over between configured providers. Secondary routes need approved senders, capacity and appropriate consent; ambiguous primary outcomes can cause duplicates across providers. Remote notifications to native Apple apps use APNs; switching an intermediary provider does not bypass an APNs outage. Queue eligible work within its TTL and recover through the app's own sync path.

With "full jitter" as described on the [AWS Architecture Blog](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/), the retry ceiling grows after repeated retryable failures, up to a maximum. Independently choose a delay within that ceiling, respect any provider minimum wait, and stop when the attempt or time budget is exhausted.

Jitter reduces synchronisation in expectation. It does not guarantee uniformly spaced retries or eventual success.

## Key takeaways

- Classify provider acceptance, invalid destinations and ambiguous outcomes separately.
- Retry with jitter inside TTL and attempt budgets.
- Use APNs invalidation timestamps and provider-specific token rules.
- Failover requires usable registered senders, consent and spare capacity.

## Further reading

- [Apple: APNs requests and responses](https://developer.apple.com/library/archive/documentation/NetworkingInternet/Conceptual/RemoteNotificationsPG/CommunicatingwithAPNs.html)
- [Firebase: registration token management](https://firebase.google.com/docs/cloud-messaging/manage-tokens)
- [AWS: exponential backoff and jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)
