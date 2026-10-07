---
id: cache-fundamentals
title: Why cache, and where
level: basic
minutes: 10
summary: What a cache buys you, the layers it can live in from browser to buffer pool, and the hit-ratio maths that tells you whether it is working.
---

A **cache** is a small, fast store that keeps copies of data that lives somewhere slower or more expensive. You put one in front of a source of truth so that repeated requests for the same thing don't pay the full cost every time.

Caching helps when a workload has reuse or skew. Some workloads approximate a Zipf-like popularity pattern, but a fixed 80/20 split is not universal; measure the actual access distribution. In workloads with temporal locality, a value read once is likely to be read again soon. This is called **locality of reference**: *temporal* locality (the same item again) and *spatial* locality (nearby items).

## What a cache buys you

There are three separate benefits, and it helps to know which one you are after.

- **Lower latency.** A local memory lookup can avoid network and backend work. Exact latency depends on hardware, software, payload and load; universal nanosecond/millisecond benchmarks are absent because no matched measurements are supplied.
- **Less load on the backend.** Every hit is a request your database never sees. A 95% hit ratio means the database handles 1 in 20 reads.
- **Lower cost.** Serving bytes from a CDN edge or from RAM is often far cheaper than recomputing a page or paying for database capacity.

The price you pay is **staleness** and **complexity**. A cache holds a copy, and copies can disagree with the original. Most of this module is about managing that cost.

> [!note] A cache is not a database
> Treat cached data as disposable. If the cache is wiped, the system should get slower, not wrong. If losing the cache loses data, you have built a database without a database's guarantees.

## The layers where caches live

A single web request can pass through half a dozen caches before it reaches the disk.

```
 Browser cache     (per user, HTTP headers)
      |
 CDN edge          (shared, near the user)
      |
 Reverse proxy     (Varnish / Nginx)
      |
 App server        (in-process memory)
      |
 Distributed cache (Redis / Memcached)
      |
 Database          (buffer pool, page cache)
      |
 Disk
```

Each layer sits closer to the user than the one below it. Caching closer to the user saves more latency but gives you less control over invalidation.

| Layer | Main saving | Who controls it |
|---|---|---|
| Browser | Network request | Browser and response policy |
| CDN edge | Origin trip | Provider configuration |
| Reverse proxy | Application work | Service operator |
| In-process | Network and decoding work | Application |
| Redis / Memcached | Database work | Cache operator |
| DB buffer pool | Storage reads | Database |

### Browser cache

The browser stores responses keyed by URL and obeys `Cache-Control`, `ETag` and friends. It is local to a browser profile, not necessarily one application account. A long freshness lifetime permits reuse; it does not guarantee retention. Supporting browsers can honor Clear-Site-Data on a later response, but there is no universal immediate remote purge of every browser. That is why static assets use **fingerprinted file names** such as `app.3f9a1c.js`. A new version is a new URL, so the old cached copy simply stops being requested.

### CDN edge

A CDN keeps copies in hundreds of points of presence (PoPs) worldwide, so a user in Sydney fetches from Sydney rather than from Virginia. It is a **shared** cache, so it must never store one user's private response and hand it to another. CDNs are covered in the networking module; here, remember that they are just another HTTP cache with a purge API.

### Reverse proxy

Varnish, Nginx (`proxy_cache`) or a cloud load balancer can cache full HTTP responses in front of your app servers. This is very effective for pages that are the same for every anonymous visitor, such as a news homepage.

### Application cache

This is the cache you code against. There are two flavours:

- **In-process** (a dictionary, Caffeine in Java, `functools.lru_cache` in Python). Fastest possible, with no network hop and no serialisation. But each server has its own copy, so 50 servers means 50 copies that can disagree, and memory is limited to one process.
- **Remote / distributed** (Redis, Memcached). A shared service (possibly with multiple replicas), accessed over the network at deployment-dependent latency. Survives app deploys and scales independently.

Many systems use both: a tiny in-process cache with a short TTL (say 1–5 seconds) in front of Redis, to absorb very hot keys.

### Database buffer pool

Databases cache too. PostgreSQL keeps recently used 8 KB pages in `shared_buffers` and also relies on the operating system's page cache. PostgreSQL's docs suggest starting `shared_buffers` at about 25% of RAM on a dedicated server. MySQL's InnoDB has the **buffer pool**, which on a dedicated host is often given up to about 80% of RAM. Cached pages avoid storage reads, but the speedup depends on query execution, hardware and the rest of the workload.

> [!tip] The "free" cache
> Before adding Redis, check that your database's working set fits in RAM. Sizing the buffer pool correctly is often the cheapest caching win available.

## Hit ratio maths

The **hit ratio** `h` is the fraction of lookups served from the cache:

```
h = hits / (hits + misses)
```

The **average access time** is a weighted sum. On a miss you usually pay the cache lookup *and* the backend:

```
T_avg = T_cache + (1 - h) * T_backend
```

### A worked example

Redis takes 1 ms; the database takes 20 ms.

| Hit ratio | Average latency | DB reads per 10k |
|---|---|---|
| No cache lookup | 20 ms | 10,000 |
| 0% (cache checked) | 21 ms | 10,000 |
| 80% | 1 + 0.2×20 = 5 ms | 2,000 |
| 90% | 1 + 0.1×20 = 3 ms | 1,000 |
| 99% | 1 + 0.01×20 = 1.2 ms | 100 |

Notice what happens between 90% and 99%. Latency only falls from 3 ms to 1.2 ms, but **database load falls tenfold**, from 1,000 to 100 reads. The useful number is often the **miss ratio** `(1 - h)`, because that is what your backend actually sees. Going from 99% to 99.9% barely registers on a latency chart (1.2 ms to 1.02 ms), but it cuts backend load by another 10×.

This is also why losing a cache is so dangerous. If the database is sized for a 1% miss rate and the cache disappears, it suddenly receives 100× its usual traffic. Lesson 7 covers this failure mode.

### Stacked caches

When caches sit in layers, each one only sees the misses of the layer above. Suppose an in-process cache catches 50% of reads and Redis catches 90% of what is left:

```
DB share = (1 - 0.5) * (1 - 0.9)
         = 0.5 * 0.1 = 0.05
```

Together they achieve a 95% hit ratio. Notice that Redis's *own* hit ratio looks lower than it would without the in-process layer, because the in-process cache has already taken the easiest, hottest keys. Judge each layer by what it saves the layer below, not by its ratio in isolation.

### Is caching worth it here?

A cache helps when:

1. Reads greatly outnumber writes for the same key.
2. The same keys are requested repeatedly (skewed access).
3. Slightly stale data is acceptable, or you can invalidate reliably.
4. The value is expensive to produce: a slow query, an aggregation, a rendered page, a remote API call.

A cache helps little or hurts when every request is for a different key (a long-tail scan), when data changes on almost every read, or when correctness requires the very latest value (a bank balance used to authorise a payment).

> [!warning] Misses can cost more than no cache
> A miss pays the cache round trip *plus* the backend. If your hit ratio is very low, you have added latency and a new failure point for almost no benefit.

## Sizing: how big should it be?

You rarely need to cache everything. Because access is skewed, the required fraction of cached keys depends on the observed popularity distribution. The usual approach is:

1. Estimate the **working set**: the distinct keys touched in a typical window (an hour or a day).
2. Multiply by average value size plus overhead (measure key, value, allocator and metadata overhead with representative objects; no fixed per-key overhead applies universally).
3. Measure the hit ratio at a few sizes. The curve of hit ratio against cache size flattens out; stop where extra memory stops buying meaningful hits.

For example, 5 million active users with a 2 KB profile is about 10 GB of values plus ~0.5 GB of overhead, under an illustrative 100-byte-overhead assumption. This is payload sizing, not a node recommendation; add measured fragmentation, buffers, replication and snapshot headroom.

## Key takeaways
- Caches work because access is skewed and repeated (locality of reference).
- They cut latency, backend load and cost, at the price of staleness and complexity.
- Caches exist at every layer: browser, CDN, reverse proxy, in-process, distributed, and inside the database.
- `T_avg = T_cache + (1 - h) × T_backend`. Watch the **miss ratio**: it is what your backend sees.
- Moving from 90% to 99% hit ratio cuts backend load by 10×, so losing the cache can overwhelm the database.
- Cached data must be disposable: losing it should make things slower, never wrong.

## Further reading
- [Cache (computing) — Wikipedia](https://en.wikipedia.org/wiki/Cache_(computing))
- [Caching overview — AWS](https://aws.amazon.com/caching/)
- [Latency numbers every programmer should know](https://gist.github.com/jboner/2841832)
- [PostgreSQL resource consumption (shared_buffers)](https://www.postgresql.org/docs/current/runtime-config-resource.html)
- [Locality of reference — Wikipedia](https://en.wikipedia.org/wiki/Locality_of_reference)
