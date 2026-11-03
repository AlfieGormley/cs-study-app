---
id: cs1-limiter-concurrency-fleet-load
title: Protect in-flight work and total fleet capacity
level: intermediate
minutes: 3
summary: Per-client rates cannot bound all fleet traffic or long-running work.
sourceLesson: cs1-rate-limiter
---

Earlier units bound request counts for each client. A service can still overload when many compliant clients arrive together, or when a few allowed requests run for a long time. This unit separates admission rate from resource occupancy.

## Bottlenecks and trade-offs

| Choice | Trade-off |
|---|---|
| Central Redis | Shared atomic decisions; network and failover costs |
| Local only | Fast; global accuracy needs reserved shares |
| Fail open | Preserves admission; can allow excess work |
| Fail closed | Bounds admission; can reject legitimate work |

Also mention that rate limiting is not load shedding. Stripe, for example, runs request-rate and concurrency limiters per user *and* fleet-wide load shedding mechanisms that drop low-priority traffic when the whole system is under strain. Per-key limits don't protect you when a million well-behaved clients all arrive at once.

Rate is also not the same as work in progress. Little's law, a general result for any stable queueing system, links them:

```formula reference
L = λW
where
L: mean number of requests in the chosen system, including waiting if it is within that boundary
λ: long-run accepted arrival rate, in requests per second
W: mean time each request spends inside the same boundary, in seconds
In words: in a stable system, average work present grows with both the arrival rate and the time each request stays; a rate cap alone is not an instantaneous concurrency cap.
```

So a customer averaging 100 accepted requests per minute, each spending 20 seconds in the measured system, has about 33 requests present on average, even though the rate limit is respected. Little's law holds only for long-run averages in a stable system (one that keeps up with its arrivals). A **concurrency limiter** (a cap on in-flight requests per customer, say 10) bounds that directly.

## At 10x scale

At 10 million checks/s:

- A central Redis call per request may become expensive; shard count follows a representative script benchmark. Move to **two-tier limiting**: gateways enforce locally with durably reserved token batches. Choose replenishment frequency from measured demand; a periodic count sync alone is not equivalent to safe leasing.
- Push coarse limits (per-IP DDoS protection) to the **edge/CDN** so abusive traffic never reaches your data centre.
- Use **per-region** limits, with periodic rebalancing of each region's share.
- Treat rule changes as a deployment: version them, roll them out gradually, and have a kill switch, because a wrong rule can reject all traffic instantly.

## Key takeaways

- Per-client rates cannot bound all fleet traffic or long-running work.
- Little’s law relates stable long-run averages, not instantaneous concurrency.
- Use concurrency caps, load shedding and gradual rule deployments.

## Further reading

- [Stripe: rate and concurrency limiting](https://stripe.com/blog/rate-limiters)
- [MIT: Little’s law](https://web.mit.edu/1.041/www/lectures/L3-cumulative-diagram-2026sp.pdf)
