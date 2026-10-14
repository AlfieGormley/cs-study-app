---
id: cache-purpose-and-locality
title: Choose workloads that benefit from caching
level: basic
minutes: 3
summary: Explain reuse, latency and backend-load savings, then decide when cached copies are appropriate.
sourceLesson: cache-fundamentals
---

A **cache** is a small, fast store that keeps copies of data that lives somewhere slower or more expensive. You put one in front of a source of truth so that repeated requests for the same thing don't pay the full cost every time.

Caching helps when a workload has reuse or skew. Some workloads approximate a Zipf-like popularity pattern, but a fixed 80/20 split is not universal; measure the actual access distribution. In workloads with temporal locality, a value read once is likely to be read again soon. This is called **locality of reference**: temporal locality (the same item again) and spatial locality (nearby items).

## What a cache buys you

There are three separate benefits, and it helps to know which one you are after.

- **Lower latency.** A local memory lookup can avoid network and backend work. Exact latency depends on hardware, software, payload and load; universal nanosecond/millisecond benchmarks are absent because no matched measurements are supplied.
- **Less load on the backend.** Every hit is a request your database never sees. A 95% hit ratio means the database handles 1 in 20 reads.
- **Lower cost.** Serving bytes from a CDN edge or from RAM is often far cheaper than recomputing a page or paying for database capacity.

The price you pay is **staleness** and **complexity**. A cache holds a copy, and copies can disagree with the original. Most of this module is about managing that cost.

> [!note] A cache is not a database
> Treat cached data as disposable. If the cache is wiped, the system should get slower, not wrong. If losing the cache loses data, you have built a database without a database's guarantees.

### Is caching worth it here?

A cache helps when:

1. Reads greatly outnumber writes for the same key.
2. The same keys are requested repeatedly (skewed access).
3. Slightly stale data is acceptable, or you can invalidate reliably.
4. The value is expensive to produce: a slow query, an aggregation, a rendered page, a remote API call.

A cache helps little or hurts when every request is for a different key (a long-tail scan), when data changes on almost every read, or when correctness requires the very latest value (a bank balance used to authorise a payment).

> [!warning] Misses can cost more than no cache
> A miss pays the cache round trip *plus* the backend. If your hit ratio is very low, you have added latency and a new failure point for almost no benefit.

## Key takeaways
- Reuse and skew let a small cache answer a large share of reads; measure the actual access distribution.
- Caching trades lower latency, backend work and cost for stale copies and more moving parts.
- Keep disposable copies in caches; payment authorisation and other correctness decisions still need authoritative checks.

## Further reading
- [Caching overview — AWS](https://aws.amazon.com/caching/)
- [Locality of reference — Wikipedia](https://en.wikipedia.org/wiki/Locality_of_reference)
- [Cache (computing) — Wikipedia](https://en.wikipedia.org/wiki/Cache_(computing))
