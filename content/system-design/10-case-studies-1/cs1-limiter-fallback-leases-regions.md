---
id: cs1-limiter-fallback-leases-regions
title: Bound fallback, leases and regional quota shares
level: intermediate
minutes: 4
summary: Choose fail-open or fail-closed from the consequence of excess work.
sourceLesson: cs1-rate-limiter
---

## Deep dive 3: Failure and degradation

For ordinary availability-first quotas, limiter failure should not take the whole API down. Security-sensitive checks can require a stricter fallback.

- **Fail open.** If Redis times out (set an aggressive timeout like 5–10 ms), allow the request and emit a metric. Briefly over-admitting is better than rejecting all traffic.
- **Fail closed** only for limits that protect something critical, such as login attempts (brute-force protection) or expensive operations.
- **Local fallback.** Each gateway keeps an approximate in-memory bucket per key, sized as below. When Redis is unreachable, use that instead of nothing.

```formula
local = limit / G
local = 1,000/min / 50 = 20/min
where
local: the limit one gateway enforces on its own
limit: the global limit for the key
G: the number of gateways sharing the key's traffic, here an assumed 50
min: minute (/min means per minute)
In words: each gateway takes an equal slice of the global limit; it is only approximate, because a client's traffic is rarely spread evenly over gateways.
```

## Deep dive 4: Scaling the hot path

At a million checks a second, even one Redis round trip per request adds up. Options:

- **Local pre-check.** Gateways cache "this key is over limit until a given deadline" after a rejection, so a client hammering you is rejected locally without touching Redis.
- **Batching / token leasing.** A gateway takes, say, 10 tokens at a time from Redis and spends them locally. Ten times fewer Redis calls, at the cost of slight inaccuracy (unused leased tokens). Only lease for keys whose limit is much larger than the total that could be leased out at once (worked out below): with 200 gateways leasing 10 each, a 100/min customer's whole allowance would be stranded on 10 gateways while requests on the other 190 are rejected.
- **Hot keys.** One huge customer can concentrate load on one Redis shard. Splitting the key into sub-buckets (`key#0..key#7`, each with 1/8 of the limit, picked at random) spreads it. The cost is accuracy: a request can be rejected by an empty sub-bucket while others still have tokens, so this only suits customers whose traffic is large enough to average out.

The leasing rule and the sub-bucket split, as sums:

```formula
leased = G × lease
leased = 200 × 10 = 2,000 ≫ 100
sub = limit / 8
where
leased: the most tokens that could be held by gateways at once
G: the number of gateways, here 200
lease: tokens each gateway takes per Redis call, here 10
≫: much greater than
sub: the limit given to each of the 8 sub-buckets a hot key is split into
limit: the customer's total limit
In words: if the gateways together could lease far more than a customer's limit, leasing strands the allowance; splitting a hot key eight ways gives each piece an eighth of the limit.
```

## Deep dive 5: Multiple regions

Should a global limit of 1,000/min be enforced across US and EU together? Assume a cross-region round trip of about 100 ms in this scenario. Putting that round trip on each check would exceed the stated 1–2 ms overhead target. Actual network latency depends on deployment. Options:

- **Per-region limits**: give each region a share (e.g. proportional to its traffic). Simple, slightly unfair if traffic shifts.
- **Async sync**: each region enforces locally and gossips counts to the others every second or so. The global limit can be exceeded by roughly the traffic other regions admit during one sync interval. For a client sending near its limit that's a few percent; a client blasting all regions at once can overshoot by more, so pair this with a per-region burst cap.

Static regional shares can preserve a global quota if their allowances sum to the limit and redistribution cannot double-allocate. Asynchronous full-quota replicas instead need explicit overshoot and partition bounds.

## Key takeaways

- Choose fail-open or fail-closed from the consequence of excess work.
- Lease only when allowance is large enough to avoid stranding small quotas.
- Regional shares and asynchronously replicated full quotas have different overshoot guarantees.

## Further reading

- [Stripe: rate and concurrency limiting](https://stripe.com/blog/rate-limiters)
- [Cloudflare: measured sliding-counter approximation](https://blog.cloudflare.com/counting-things-a-lot-of-different-things/)
