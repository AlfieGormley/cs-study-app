---
id: cache-frequency-and-expiry
title: Separate frequency eviction from TTL expiry
level: intermediate
minutes: 3
summary: Compare LFU popularity with TTL freshness, including decaying counts and active expiry.
sourceLesson: cache-eviction
---

Eviction makes room under memory pressure; expiry stops reuse after a lifetime. Frequency-based eviction needs to adapt when yesterday’s popular item stops being useful.

## LFU: least frequently used

Evict the item with the fewest accesses. This protects consistently popular keys from scans, since a key read once never outranks a key read a thousand times.

LFU has its own problems:

- **Stale popularity.** A key that was hugely popular last week keeps a high count and squats in the cache. Real LFU implementations **decay** counts over time.
- **New items struggle.** A brand-new key starts at count 1 and is the first candidate for eviction, even if it is about to become hot.
- **Cost.** Exact LFU needs a counter per key and a structure ordered by count. O(1) designs exist, but they are fiddlier than LRU.

## TTL: time to live

A **TTL** says how long an entry may be served before it is considered expired, regardless of memory pressure. It is a freshness rule, not a capacity rule, but it frees memory too.

- Short TTLs limit residence of an individual copy, at the cost of misses; delayed or lagging-source fills can still supply older data.
- Long TTLs (hours) give high hit ratios but serve stale data longer.
- Add **TTL jitter** (randomise each TTL by up to ±10%) so that keys loaded together do not all expire together (see the later avalanche unit).

How does Redis actually remove expired keys? Two ways:

1. **Lazily**: when a client touches an expired key, Redis deletes it and reports a miss.
2. **Actively**: A background active-expiry cycle samples TTL-bearing keys under a CPU budget. Sampling and timing vary by Redis version, hz/dynamic-hz and active-expire-effort; inspect that version rather than relying on universal batch sizes or thresholds.

So an expired key can still occupy memory for a short time after its TTL; it will never be *returned*, though.

## Comparison

| Policy | Evicts | Good at | Weak at |
|---|---|---|---|
| FIFO | Oldest insert | Simplicity | Ignores use |
| LRU | Least recent | Recency | Scans |
| LFU | Least frequent | Stable hot set | Shifting trends |
| TTL | Expired | Freshness | Not capacity-aware |

To diagnose missing hot keys, compare `expired_keys` with `evicted_keys` in Redis `INFO stats`. Many expiries, few evictions and spare memory point to TTL policy rather than capacity pressure.

## Key takeaways
- LFU protects frequently used items but needs decay and a way for new items to become established.
- TTL limits an entry’s residence, rather than guaranteeing the age of data supplied by a delayed or lagging fill.
- Redis removes expired entries on access and through a budgeted active-expiry cycle; expiry and capacity pressure need different diagnosis.

## Further reading
- [EXPIRE — Redis documentation](https://redis.io/docs/latest/commands/expire/)
- [Key eviction — Redis docs](https://redis.io/docs/latest/develop/reference/eviction/)
