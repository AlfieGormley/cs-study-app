---
id: api-limiter-failure-placement
title: Limiter failures, local shares and placement
level: advanced
minutes: 3
summary: Choose fallback policies, watch shared-store bottlenecks and enforce limits at the appropriate edge.
sourceLesson: api-rate-limiting
---

## Practical concerns

- **Latency.** Every request now makes a Redis round trip; measure median and tail latency under representative contention.
- **Fail open or closed?** If Redis is down, do you reject everything (closed) or allow everything (open)? A service may **fail open** with a local fallback limiter when availability is more important than temporary quota precision. Security-critical limits (login attempts) may fail closed.
- **Hot keys.** One huge tenant's counter lives on one Redis shard. Shard by client id across a Redis Cluster, and consider local pre-aggregation.
- **Clock skew.** The script above trusts `now` from whichever API server called it. If those clocks disagree, a server whose clock runs behind sees negative elapsed time. Use a trusted shared time source (for example Redis `TIME` in a compatible scripting/replication mode). The sample keeps the stored timestamp from moving backwards; merely clamping elapsed time while storing a lower timestamp can mint extra tokens when time catches up. Large forward jumps still require an explicit clock policy.
- **Approximate local limiting.** At very high scale, each server can enforce its share of the limit locally and sync periodically. It's less precise but needs no per-request network hop. The share is shown below.

```formula
L_local = L / N
L_local = 1,000 / 20 = 50
where
L_local: the limit each server enforces on its own, per minute
L: the client's overall limit, here 1,000 per minute
N: the number of servers sharing it, here 20
In words: split the limit evenly between the servers; this matches the global limit only when the client's traffic is spread evenly across all of them.
```

> [!note] Measurement gap
> No benchmark establishes Redis latency, bytes per sorted-set member or a universal throughput cutoff here. These depend on deployment and data representation; measured capacity guidance is omitted.

## Where to enforce

Rate limiting usually lives at the **edge**: an API gateway, an Envoy sidecar, or a CDN (Cloudflare, AWS WAF). Enforcing it early means rejected requests cost almost nothing. Finer-grained, per-endpoint limits can live in the application.

Choose the **key** carefully: per API key or user for authenticated traffic; per IP for anonymous traffic (but remember many users can share one IP behind a corporate NAT or mobile carrier).

## Key takeaways
- Measure the shared store’s latency and hot-key behaviour.
- Choose fail-open or fail-closed policies by the protection being provided; local fallback is approximate.
- Equal local quota shares assume evenly distributed client traffic.
- Enforce early and choose identities carefully: many unrelated users share a NAT address.

## Further reading
- [Stripe blog: Scaling your API with rate limiters](https://stripe.com/blog/rate-limiters)
- [Redis: Rate limiting](https://redis.io/glossary/rate-limiting/)
