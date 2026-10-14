---
id: net-dns-cache-lifetimes
title: "TTL expiry and safe DNS changes"
level: basic
minutes: 5
summary: "Trace positive and negative cache expiry and plan a migration around existing cached answers."
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

**Negative answers are cached too.** If a name doesn't exist (`NXDOMAIN`), resolvers cache that for the zone's negative TTL: the smaller of the `SOA` record's own TTL and its `MINIMUM` field (RFC 2308). With an `SOA` TTL of 900 s and a `MINIMUM` of 3,600 s:

```formula
TTL_neg = min(TTL_SOA, MINIMUM)
TTL_neg = min(900 s, 3,600 s) = 900 s
where
TTL_neg: the negative TTL: how long a resolver may cache a "this name doesn't exist" (NXDOMAIN) answer, in seconds (s)
min: the minimum function: whichever of the values in the brackets is smaller
TTL_SOA: the TTL of the zone's SOA record itself, in seconds; 900 s in this example
MINIMUM: the last number stored inside the SOA record, which RFC 2308 uses as the negative-caching limit; 3,600 s in this example
s: second
In words: a "no such name" answer is cached for whichever is shorter, the SOA record's own TTL or its MINIMUM field, so 15 minutes here.
```

If you query a name before creating it, clients may keep getting "doesn't exist" for up to that long after you add it.

**The TTL counts down in caches.** A resolver that cached a 300 s record 200 s ago hands it out with a TTL of 100:

```formula
TTL_left = TTL − t_age
TTL_left = 300 s − 200 s = 100 s
where
TTL_left: the remaining time to live that the resolver hands out with its cached answer, in seconds (s)
TTL: the time to live the authoritative server set on the record, in seconds; here 300 s
t_age: how long ago the resolver cached the record, in seconds; here 200 s
s: second
In words: a cache passes on only the time its copy has left, not the original TTL.
```

So the TTL a client sees is the *remaining* lifetime, and every cache downstream of it expires at the same moment, not 300 s after it asked.

> [!warning] TTLs are a request, not a guarantee
> Some resolvers enforce a minimum TTL, some clients (old JVMs, some mobile OSes, connection pools) cache much longer than told, and long-lived TCP connections never re-resolve at all. Many resolvers also implement **serve-stale** (RFC 8767): if the authoritative servers are unreachable, they keep answering from expired cache entries rather than failing. That's good for resilience, but it's another way old answers outlive their TTL. Plan for a long tail: after a DNS change, a small percentage of traffic often keeps hitting the old address for hours.

### The TTL-lowering playbook

If you're migrating a service to new IPs:

1. Days before, lower the TTL from, say, 86,400 s to 60 s.
2. Wait at least the *old* TTL (24 hours) so normally expiring caches no longer retain an answer with the old long TTL; caches need not refresh until queried.
3. Change the record. Most clients move within a minute or two.
4. Keep the old servers running until traffic drains.
5. Raise the TTL again.

Why step 2 waits the *old* TTL: a cache that fetched the record just before you lowered the TTL keeps its long-lived copy until

```formula
t_expire = t_fetch + TTL_old
t_expire = 08:59 + 86,400 s
t_expire = 08:59 + 24 h
where
t_expire: the clock time at which that cached copy finally expires; here 08:59 the next day
t_fetch: the clock time at which the cache fetched the record; here 08:59, one minute before the TTL was lowered at 09:00
TTL_old: the TTL the record had when it was fetched, 86,400 seconds (s), which is 24 hours (h)
s: second
h: hour, 3,600 seconds
In words: lowering the TTL doesn't reach copies already cached; each one lives out the old TTL from the moment it was fetched.
```

Skipping step 2 is a classic mistake: caches still holding the 24-hour record won't look again for up to a day.

## Key takeaways

- Cached replies carry the remaining TTL, not a fresh copy of the original lifetime.
- Negative caching uses the smaller of the SOA TTL and its MINIMUM field.
- Lower a TTL before a migration and wait the old lifetime; serve-stale and long-lived connections still create a tail.

## Further reading

- [Negative caching (RFC 2308)](https://www.rfc-editor.org/rfc/rfc2308)
- [Serving stale DNS data (RFC 8767)](https://www.rfc-editor.org/rfc/rfc8767)
