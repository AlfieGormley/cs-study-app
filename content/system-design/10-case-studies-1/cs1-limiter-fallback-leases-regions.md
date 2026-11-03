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
- **Local fallback.** Each gateway keeps an approximate in-memory bucket per key, with an explicitly accounted share. When Redis is unreachable, use that instead of nothing.

Dividing an allowance into fixed gateway shares bounds the total only when membership, ownership and resets preserve those shares. Uneven routing can strand allowance on idle gateways, and switching from central state to fresh local buckets can grant extra work unless the transition is accounted for.

## Deep dive 4: Scaling the hot path

At a million checks a second, even one Redis round trip per request adds up. Options:

- **Local pre-check.** Gateways cache "this key is over limit until a given deadline" after a rejection, so a client hammering you is rejected locally without touching Redis.
- **Batching / token leasing.** A gateway takes, say, 10 tokens at a time from Redis and spends them locally. Fully spending each batch can reduce central calls roughly tenfold, but unused reservations can reject requests elsewhere without exceeding the quota. Only lease for keys whose limit is much larger than the total that could be leased out at once : with 200 gateways leasing 10 each, a 100/min customer's whole allowance would be stranded on 10 gateways while requests on the other 190 are rejected.
- **Hot keys.** One huge customer can concentrate load on one Redis shard. Splitting the key into sub-buckets (`key#0..key#7`, each with 1/8 of the limit, picked at random) spreads it. The cost is accuracy: a request can be rejected by an empty sub-bucket while others still have tokens, so this only suits customers whose traffic is large enough to average out.

A small quota may be entirely reserved by a few gateways while requests arriving elsewhere are rejected. Leases must subtract from the central allowance atomically and must not be reclaimed while an old holder could still spend them. Smaller leases or direct checks reduce stranded capacity.

## Deep dive 5: Multiple regions

Should a global limit of 1,000/min be enforced across US and EU together? Assume a cross-region round trip of about 100 ms in this scenario. Putting that round trip on each check would exceed the stated 1–2 ms overhead target. Actual network latency depends on deployment. Options:

- **Per-region limits**: give each region a share (e.g. proportional to its traffic). Simple, slightly unfair if traffic shifts.
- **Async sync**: each region enforces locally and gossips counts to the others every second or so. The global limit can be exceeded by roughly the traffic other regions admit during one sync interval. The amount depends on admission rates, burst allowances and delay; during a partition the delay can grow without bound unless local admission is capped or stopped.

Static regional shares can preserve a global quota if their allowances sum to the limit and redistribution cannot double-allocate. Asynchronous full-quota replicas instead need explicit overshoot and partition bounds.

> [!analogy] Real-world analogy: Tickets at the wrong desk
> Several desks reserve batches from one shared supply. One desk can run out while another still holds unused tickets.
>
> **How it maps:** Token leases reduce trips to shared state but can strand a small allowance away from arriving requests.
>
> **Where it stops:** A network failure cannot safely prove that an old desk stopped spending; lease expiry and reassignment need explicit accounting.

## Key takeaways

- Choose fail-open or fail-closed from the consequence of excess work.
- Lease only when allowance is large enough to avoid stranding small quotas.
- Regional shares and asynchronously replicated full quotas have different overshoot guarantees.

## Further reading

- [Stripe: rate and concurrency limiting](https://stripe.com/blog/rate-limiters)
- [Cloudflare: measured sliding-counter approximation](https://blog.cloudflare.com/counting-things-a-lot-of-different-things/)
