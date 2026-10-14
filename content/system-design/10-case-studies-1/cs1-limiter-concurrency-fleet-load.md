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
| Central Redis | Accurate, +1 hop |
| Local only | Fast, inaccurate |
| Fail open | Available, abusable |
| Fail closed | Safe, fragile |

Also mention that rate limiting is not load shedding. Stripe, for example, runs request-rate and concurrency limiters per user *and* fleet-wide load shedding mechanisms that drop low-priority traffic when the whole system is under strain. Per-key limits don't protect you when a million well-behaved clients all arrive at once.

Rate is also not the same as work in progress. Little's law, a general result for any stable queueing system, links them:

```formula
L = λ × W
L = (100 / (60 s)) × 20 s ≈ 33
where
L: the average number of requests in flight (started but not finished)
λ: lambda, the average rate of accepted arrivals, here 100 per minute = 100 / 60 s ≈ 1.67 per second
W: the average time each request takes, in seconds, here 20 s
s: seconds
≈: approximately equal to
In words: in-flight work equals how fast requests arrive times how long each one stays.
```

So a customer within a 100/min limit on a 20-second report endpoint holds about 33 requests in flight, even though the rate limit is respected. Little's law holds only for long-run averages in a stable system (one that keeps up with its arrivals). A **concurrency limiter** (a cap on in-flight requests per customer, say 10) bounds that directly.

## At 10x scale

At 10 million checks/s:

- A central Redis call per request may become expensive; shard count follows a representative script benchmark. Move to **two-tier limiting**: gateways enforce locally with leased tokens and sync with Redis every ~100 ms.
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
