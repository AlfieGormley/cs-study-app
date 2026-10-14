---
id: rel-adaptive-throttle-bounded-flow
title: Adaptive throttling and bounded backpressure
level: intermediate
minutes: 3
summary: Reduce offered load upstream and bound every queue between producers and consumers.
sourceLesson: rel-overload-protection
---

The server-side admission unit rejected excess work at the service. Client-side throttling can prevent some rejected work from reaching it at all. Backpressure then carries a slow consumer’s capacity limit towards producers instead of silently accumulating an unbounded queue.

### Client-side throttling

The Google SRE book describes **adaptive throttling**: each client counts the requests it has tried to make and the requests the backend accepted, over the last two minutes, and rejects new requests locally with this probability:

```formula
P_rej = max(0, (R − KA) / (R + 1))
P_rej = max(0, (100 − 2 × 30) / 101)
P_rej = 40 / 101 ≈ 0.40
where
P_rej: the probability that the client rejects a new request itself, without sending it, from 0 to 1
max: the larger of the two values, so P_rej is never below 0
R: requests, the number of requests the application attempted, including ones the client rejected locally, here 100
A: accepts, the number of requests the backend accepted, here 30
K: a tuning multiplier, usually 2
≈: approximately equal to (rounded)
In words: while the backend accepts at least half the requests (with K = 2), nothing is dropped locally; when it accepts only 30 of 100, the client drops about 40% of new requests itself.
```

With the tuning multiplier set to two, once the backend is rejecting more than half the requests, the client starts dropping some itself, and those rejected requests don't even cost the backend a network round trip. In steady state the client sends roughly twice the accepted request count when the multiplier is two, enough to notice quickly when the backend recovers. Lower K is more aggressive; higher K wastes more backend effort on rejections. The +1 in the denominator only stops division by zero when the client has sent nothing yet.

## Backpressure at the service level

**Backpressure** means a slow consumer signals upstream to slow down instead of silently buffering. Unbounded queues are the enemy: they turn an overload into ever-increasing latency and eventually an out-of-memory crash.

- **Bounded queues**: when full, reject or block the producer.
- **Protocol signals**: HTTP `429` with `Retry-After`, gRPC `RESOURCE_EXHAUSTED`, TCP flow control windows, Reactive Streams' `request(n)`.
- **Pull-based consumption**: Kafka consumers pull at their own pace, so the broker never pushes faster than they can handle; lag grows instead (which you alert on).

Backpressure must propagate all the way to something that can actually slow down: a user, a batch job, or a queue with spare capacity. Otherwise it just moves the overflow somewhere else.

## How the patterns fit together

```
Request
  ▼
[Load shedder] reject if over capacity
  ▼
[Bulkhead]  per-dependency pool
  ▼
[Breaker]   fail fast if open
  ▼
[Timeout + budgeted retry]
  ▼
Dependency
  ✗ → fallback (degrade)
```

## Key takeaways

- Adaptive throttling tracks all application attempts, including locally rejected ones, and backend accepts.
- Use bounded queues and propagate pressure to a producer that can slow down.
- Pull consumers can accumulate lag; durable queues still have finite capacity and retention. Combine these controls with admission, bulkheads and breakers.

## Further reading

- [Using load shedding to avoid overload (AWS Builders' Library)](https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/)
- [Handling overload (Google SRE book)](https://sre.google/sre-book/handling-overload/)
