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

- **Exponential backoff with jitter**: wait ~1 s, 2 s, 4 s, 8 s... each randomised, so thousands of failed messages don't retry in lockstep and hammer a recovering provider (formula below).
- **Respect the TTL**: if the notification's `ttlSeconds` has passed, drop it instead of retrying. A late OTP is worse than none.
- **Dead-letter queue**: after a fixed number of attempts (say 5), move the message to a DLQ for inspection rather than retrying forever.
- **Token hygiene**: APNs tells you when a device token is no longer valid (HTTP 410 for an unregistered device), and FCM returns an `UNREGISTERED` error. Deactivate the affected registration; for APNs, compare its invalidation timestamp with the latest registration so an old response cannot invalidate a newer registration. Apply FCM token-lifecycle guidance separately.
- **Circuit breakers and failover**: if one SMS provider's error rate spikes, open a circuit breaker and route to a secondary provider. Email can similarly fail over between configured providers. Secondary routes need approved senders, capacity and appropriate consent; ambiguous primary outcomes can cause duplicates across providers. Push can't fail over (only Apple can deliver to iPhones), so you queue and retry.

The backoff schedule, with "full jitter" as described on the [AWS Architecture Blog](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/):

```formula
cap_n = min(c, b × 2^n)
wait_n = U(0, cap_n)
where
n: the retry number, starting at 0 for the first retry
b: the base delay, here 1 second
2^n: n copies of 2 multiplied together (1, 2, 4, 8...), so the ceiling doubles on each retry
c: a maximum delay, so waits stop growing (say 60 seconds)
min: "the smaller of"
cap_n: the longest wait allowed before retry n
U(0, cap_n): a random time chosen evenly between 0 and cap_n
U: uniform random choice
wait_n: how long to actually wait before retry n
In words: double the ceiling on each retry, up to a cap, and wait a random time below it, so failed messages spread out instead of retrying together.
```

So ceilings run 1 s, 2 s, 4 s, 8 s and so on, and two messages that failed at the same moment almost never retry at the same moment.

## Key takeaways

- Classify provider acceptance, invalid destinations and ambiguous outcomes separately.
- Retry with jitter inside TTL and attempt budgets.
- Use APNs invalidation timestamps and provider-specific token rules.
- Failover requires usable registered senders, consent and spare capacity.

## Further reading

- [Apple: APNs requests and responses](https://developer.apple.com/library/archive/documentation/NetworkingInternet/Conceptual/RemoteNotificationsPG/CommunicatingwithAPNs.html)
- [Firebase: registration token management](https://firebase.google.com/docs/cloud-messaging/manage-tokens)
- [AWS: exponential backoff and jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)
