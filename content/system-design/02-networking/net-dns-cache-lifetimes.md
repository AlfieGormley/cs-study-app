---
id: net-dns-cache-lifetimes
title: "TTL expiry and safe DNS changes"
level: basic
minutes: 5
summary: "Predict how positive and negative answers expire in caches and plan a migration around copies that are already cached."
sourceLesson: net-dns
---
DNS caching reduces query load, but a changed authoritative answer does not instantly reach cached copies. These examples separate ordinary expiry from clients or resolvers that retain old destinations longer.

## TTLs and caching

Every record carries a **TTL** (time to live) in seconds. Any resolver can cache the answer for that long.

Illustrative zone-file fragment, not a complete zone:

```dns
; 300 is the cache lifetime in seconds.
www.example.com. 300 IN A 203.0.113.10
```

Caching is why DNS scales: a popular resolver answers millions of queries for `google.com` from memory. But it creates the central DNS trade-off:

| Short TTL (30–60 s) | Long TTL (hours–days) |
|---|---|
| Fast failover and changes | Slow to change |
| More queries, more latency | Fewer queries, faster |
| More load on your DNS | Resilient if DNS is down |

**Negative answers are cached too.** If a name doesn't exist (`NXDOMAIN`), resolvers cache that "no" for the zone's negative TTL: the smaller of the `SOA` record's own TTL and the `MINIMUM` field inside it (RFC 2308). With an `SOA` TTL of 900 s and a `MINIMUM` of 3,600 s, the smaller value wins, so a resolver may repeat "doesn't exist" for up to 15 minutes. If anyone queries a name before you create it, the resolvers they used can keep denying it for that long after you add it, while resolvers that never cached the miss see it at once.

**The TTL counts down in caches.** A resolver hands out a cached record with only the time it has *left*, not the original TTL. If it cached a 300 s record 200 s ago, it answers with a TTL of 100. Every downstream cache (a laptop, a browser) therefore expires at the same moment as the resolver's copy: layers of caching don't stack their lifetimes on top of each other. After a change, well-behaved caches have all dropped the old answer within one TTL of the last time any cache fetched it from the authoritative servers.

> [!analogy] Real-world analogy: A use-by date printed on a carton
> A dairy prints a use-by date on each carton as it leaves. The wholesaler, the corner shop and your fridge all keep that same carton until that date; passing it along the chain does not print a fresh date. If the dairy shortens its shelf life tomorrow, cartons already out there keep their old, later dates.
>
> **How it maps:** the dairy is the authoritative server, the use-by date is the record's TTL and each place holding the carton is a cache. Passing on the remaining time, not a new lifetime, is why layers of caching expire together, and why lowering a TTL cannot reach copies that are already cached.
>
> **Where it stops:** an expired DNS answer is not spoiled; the cache simply asks again, and some resolvers deliberately keep serving an expired answer when the authoritative servers can't be reached. Some clients also ignore the TTL altogether, which no carton can do.

> [!warning] TTLs are a request, not a guarantee
> Some resolvers enforce a minimum TTL, some clients (old JVMs, some mobile OSes, connection pools) cache much longer than told, and long-lived TCP connections never re-resolve at all. Many resolvers also implement **serve-stale** (RFC 8767): if the authoritative servers are unreachable, they keep answering from expired cache entries rather than failing. That's good for resilience, but it's another way old answers outlive their TTL. Plan for a long tail: after a DNS change, a small percentage of traffic often keeps hitting the old address for hours.

### The TTL-lowering playbook

If you're migrating a service to new IPs:

1. Days before, lower the TTL from, say, 86,400 s to 60 s.
2. Wait at least the *old* TTL (24 hours) so normally expiring caches no longer retain an answer with the old long TTL; caches need not refresh until queried.
3. Change the record. Most clients move within a minute or two.
4. Keep the old servers running until traffic drains.
5. Raise the TTL again.

Why step 2 waits the *old* TTL: lowering the TTL only changes answers handed out *after* the change. A cache that fetched the record one minute before you lowered it still holds a copy stamped with the 24-hour lifetime, and keeps using it until that lifetime runs out, roughly a day later.

Skipping step 2 is a classic mistake: caches still holding the 24-hour record won't look again for up to a day.

## Key takeaways

- Cached replies carry the remaining TTL, not a fresh copy of the original lifetime.
- Negative caching uses the smaller of the SOA TTL and its MINIMUM field.
- Lower a TTL before a migration and wait the old lifetime; serve-stale and long-lived connections still create a tail.

## Further reading

- [Negative caching (RFC 2308)](https://www.rfc-editor.org/rfc/rfc2308)
- [Serving stale DNS data (RFC 8767)](https://www.rfc-editor.org/rfc/rfc8767)
