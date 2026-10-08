---
id: cache-fundamentals
title: Why cache, and where
level: basic
minutes: 13
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

To judge whether a cache is working, you count how many lookups it answers. The **hit ratio** is the fraction of lookups served from the cache, and the **miss ratio** is the fraction that fall through to the backend:

```formula
h = hits / (hits + misses)
m = 1 − h
where
h: the hit ratio, a number between 0 (nothing served from cache) and 1 (everything served); often written as a percentage, so 0.9 = 90%
hits: the number of lookups that found the key in the cache, counted over some window such as a minute
misses: the number of lookups that did not find the key and had to go to the backend, counted over the same window
m: the miss ratio, the fraction of lookups that reach the backend; also between 0 and 1
In words: the hit ratio is the share of lookups the cache answered itself, and the miss ratio is everything else.
```

For example, 900 hits and 100 misses in a minute give a hit ratio of 900 / 1,000 = 0.9 (90%) and a miss ratio of 0.1 (10%). Count only lookups (reads), not writes.

The **average access time** follows from this. Every request first looks in the cache, so every request pays the cache lookup. Only the misses then go on to pay for the backend as well. Weighting the backend time by the fraction of requests that pay it gives:

```formula
T_avg = T_cache + (1 − h) × T_backend
where
T_avg: the average time to answer one read, in milliseconds (ms)
T_cache: the time for one cache lookup, hit or miss, in ms; for a remote cache such as Redis typically around 1 ms including the network trip
h: the hit ratio, between 0 and 1
(1 − h): the miss ratio, the fraction of reads that also go to the backend
T_backend: the time for the backend (for example the database) to answer one read, in ms
ms: milliseconds; 1 ms = 0.001 seconds
In words: everyone pays for the cache lookup; only the misses also pay for the database. The higher the hit ratio, the closer the average gets to the cache's own speed.
```

This simple model assumes a miss is a cache lookup followed by a backend read, one after the other. It ignores the small extra cost of writing the loaded value back into the cache, and it describes the *average* only. Slow outliers (tail latency) need percentiles, not this formula.

### A worked example

Redis takes 1 ms; the database takes 20 ms. At a 90% hit ratio:

```formula
T_avg = T_cache + (1 − h) × T_backend
T_avg = 1 ms + (1 − 0.9) × 20 ms
T_avg = 1 ms + 2 ms = 3 ms
where
T_avg: the average read time, in milliseconds (ms)
T_cache: the Redis lookup time, here 1 ms
h: the hit ratio, here 0.9 (90%)
T_backend: the database read time, here 20 ms
ms: milliseconds; 1 ms = 0.001 seconds
In words: at a 90% hit ratio, the average read costs the 1 ms lookup plus a tenth of the 20 ms database time, 3 ms in total.
```

The database sees only the misses. Its read rate is the total read rate times the miss ratio:

```formula
R_db = (1 − h) × R
R_db = (1 − 0.9) × 10,000 = 1,000
where
R_db: the number of reads that reach the database
h: the hit ratio, here 0.9 (90%)
R: the total number of reads, here 10,000
In words: with a 90% hit ratio, only one read in ten reaches the database, so 10,000 reads become 1,000 database reads.
```

The table repeats both calculations for other hit ratios.

| Hit ratio | Average latency | DB reads per 10k |
|---|---|---|
| No cache lookup | 20 ms | 10,000 |
| 0% (cache checked) | 21 ms | 10,000 |
| 80% | 1 + 0.2×20 = 5 ms | 2,000 |
| 90% | 1 + 0.1×20 = 3 ms | 1,000 |
| 99% | 1 + 0.01×20 = 1.2 ms | 100 |

Notice what happens between 90% and 99%. Latency only falls from 3 ms to 1.2 ms, but **database load falls tenfold**, from 1,000 to 100 reads. The useful number is often the miss ratio (1 − h), because that is what your backend actually sees. Going from 99% to 99.9% barely registers on a latency chart (1.2 ms to 1.02 ms), but it cuts backend load by another 10×.

This is also why losing a cache is so dangerous. If the database is sized for a 1% miss rate and the cache disappears, it suddenly receives 100× its usual traffic. Lesson 7 covers this failure mode.

### Stacked caches

When caches sit in layers, each one only sees the misses of the layer above. So the fraction of reads that gets all the way to the database is the product of the layers' miss ratios:

```formula
s_db = (1 − h_1) × (1 − h_2)
where
s_db: the share of all reads that reach the database, between 0 and 1
h_1: the hit ratio of the first (upper) layer, measured over the reads it sees
h_2: the hit ratio of the second layer, measured over only the reads the first layer missed
In words: the database sees what the first layer misses, and then only the part of that which the second layer also misses.
```

Suppose an in-process cache catches 50% of reads and Redis catches 90% of what is left:

```formula
s_db = (1 − h_1) × (1 − h_2)
s_db = (1 − 0.5) × (1 − 0.9)
s_db = 0.5 × 0.1 = 0.05
where
s_db: the share of all reads that reach the database
h_1: the in-process cache's hit ratio, here 0.5 (50%)
h_2: Redis's hit ratio on the reads that reach it, here 0.9 (90%)
In words: half the reads get past the in-process cache, and a tenth of those get past Redis, so 5% of reads reach the database.
```

Together they achieve a 95% hit ratio (1 − 0.05 = 0.95). The rule extends to any number of layers: multiply all their miss ratios. It assumes each layer's hit ratio is measured on the traffic that actually reaches it. Notice that Redis's *own* hit ratio looks lower than it would without the in-process layer, because the in-process cache has already taken the easiest, hottest keys. Judge each layer by what it saves the layer below, not by its ratio in isolation.

### Is caching worth it here?

A cache helps when:

1. Reads greatly outnumber writes for the same key.
2. The same keys are requested repeatedly (skewed access).
3. Slightly stale data is acceptable, or you can invalidate reliably.
4. The value is expensive to produce: a slow query, an aggregation, a rendered page, a remote API call.

A cache helps little or hurts when every request is for a different key (a long-tail scan), when data changes on almost every read, or when correctness requires the very latest value (a bank balance used to authorise a payment).

> [!warning] Misses can cost more than no cache
> A miss pays the cache round trip *plus* the backend. If your hit ratio is very low, you have added latency and a new failure point for almost no benefit.

How low is "very low"? Without a cache every read costs the backend time. With one, the average is the formula above. Setting the two equal gives the **break-even hit ratio**:

```formula
T_cache + (1 − h) × T_backend = T_backend
h_be = T_cache / T_backend
where
T_cache: the time for one cache lookup, in milliseconds (ms)
h: the hit ratio, between 0 and 1
T_backend: the time for one backend read, in ms
h_be: the break-even hit ratio; below it, the cache makes average latency worse than having no cache
ms: milliseconds; 1 ms = 0.001 seconds
In words: the cache pays for itself on latency once its hit ratio is bigger than the ratio of cache time to backend time.
```

For a 1 ms cache in front of a 20 ms database, the break-even hit ratio is 1 / 20 = 0.05, so 5%. Most real caches are far above this, but the same 1 ms cache in front of a fast backend (say 2 ms) needs a 50% hit ratio just to break even on latency. Latency is not the only reason to cache, though: even a low hit ratio still removes some backend load.

## Sizing: how big should it be?

You rarely need to cache everything. Because access is skewed, the required fraction of cached keys depends on the observed popularity distribution. The usual approach is:

1. Estimate the **working set**: the distinct keys touched in a typical window (an hour or a day).
2. Multiply by average value size plus overhead (measure key, value, allocator and metadata overhead with representative objects; no fixed per-key overhead applies universally).
3. Measure the hit ratio at a few sizes. The curve of hit ratio against cache size flattens out; stop where extra memory stops buying meaningful hits.

Steps 1 and 2 as a formula:

```formula
M = K × (S_v + S_o)
where
M: the memory needed for the cached data, in bytes (B)
K: the number of distinct keys in the working set
S_v: the average size of one cached value, in bytes
S_o: the average overhead per key (the key itself, metadata and allocator waste), in bytes; measure it for your cache and data
B: bytes; 1 KB = 1,000 B, 1 MB = 1,000,000 B, 1 GB = 1,000,000,000 B
In words: memory is the number of keys you need to hold times what each one costs, including its overhead.
```

For example, 5 million active users with a 2 KB profile, under an illustrative 100-byte-overhead assumption:

```formula
M = K × (S_v + S_o)
M = 5,000,000 × (2,000 B + 100 B)
M = 10,500,000,000 B ≈ 10.5 GB
where
M: the memory needed, in bytes (B)
K: the number of keys, here 5 million active users
S_v: the value size, here 2 KB = 2,000 B
S_o: the assumed overhead per key, here 100 B
B: bytes
GB: gigabytes; 1 GB = 1,000,000,000 B
≈: approximately equal to
In words: 5 million profiles of about 2 KB each need about 10 GB for the values plus about 0.5 GB of overhead.
```

This is payload sizing, not a node recommendation; add measured fragmentation, buffers, replication and snapshot headroom.

## Key takeaways
- Caches work because access is skewed and repeated (locality of reference).
- They cut latency, backend load and cost, at the price of staleness and complexity.
- Caches exist at every layer: browser, CDN, reverse proxy, in-process, distributed, and inside the database.
- Average access time is the cache lookup time plus the miss ratio times the backend time. Watch the **miss ratio**: it is what your backend sees.
- Moving from 90% to 99% hit ratio cuts backend load by 10×, so losing the cache can overwhelm the database.
- Cached data must be disposable: losing it should make things slower, never wrong.

## Further reading
- [Cache (computing) — Wikipedia](https://en.wikipedia.org/wiki/Cache_(computing))
- [Caching overview — AWS](https://aws.amazon.com/caching/)
- [Latency numbers every programmer should know](https://gist.github.com/jboner/2841832)
- [PostgreSQL resource consumption (shared_buffers)](https://www.postgresql.org/docs/current/runtime-config-resource.html)
- [Locality of reference — Wikipedia](https://en.wikipedia.org/wiki/Locality_of_reference)
