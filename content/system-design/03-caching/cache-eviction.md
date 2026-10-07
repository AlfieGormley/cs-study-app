---
id: cache-eviction
title: Eviction policies
level: intermediate
minutes: 12
summary: LRU, LFU, FIFO and TTL, how to implement them, and the cheap approximations that Redis, Memcached, Caffeine and Linux actually use.
---

A cache is smaller than the data behind it, so eventually it fills up. When a new item arrives and there is no room, the cache must choose a **victim** to throw out. The rule it uses is the **eviction policy** (or replacement policy).

The goal is to evict the item least likely to be needed again soon. Nobody knows the future, so every policy is a guess based on the past. The best guess depends on the access pattern.

Eviction (removing items because memory is full) is different from **expiry** (removing items because their time is up). Most caches do both.

## FIFO: first in, first out

Evict the item that was inserted earliest, regardless of how often it has been used.

- Trivial to implement: a queue.
- Ignores popularity. A key read 10,000 times a second is evicted just as readily as one read once.

FIFO is rarely used on its own for application caches, but variants like **CLOCK** and **SIEVE** build on its cheapness.

## LRU: least recently used

Evict the item that has gone longest without being accessed. The bet is temporal locality: what was used recently will be used again.

The classic implementation combines a **hash map** (key to node) with a **doubly linked list** ordered by recency. Both get and put have expected/amortized O(1) cost with ordinary hash-table assumptions.

```
 MRU                          LRU
 head <-> [D] <-> [A] <-> [C] <-> tail
           ^ just used      ^ evict next
```

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.cap = capacity
        self.data = OrderedDict()

    def get(self, key):
        if key not in self.data:
            return None
        # mark as most recently used
        self.data.move_to_end(key)
        return self.data[key]

    def put(self, key, value):
        self.data[key] = value
        self.data.move_to_end(key)
        if len(self.data) > self.cap:
            # evict least recently used
            self.data.popitem(last=False)
```

### Where LRU breaks: scans

LRU has a famous weakness. A one-off **scan** (a batch job reading a million keys once) pushes every key to the front, flushing the genuinely hot items out. After the scan, the cache is full of data nobody will ask for again. This is called **cache pollution**.

> [!example] LRU and a scan
> Capacity 3, contents `[A, B, C]` with A and B read constantly. A report reads X, Y, Z once each. LRU now holds `[X, Y, Z]`, and the next reads of A and B both miss.

Defences include segmented LRU (new items must prove themselves before entering the protected segment), LRU-K, 2Q and ARC, all of which consider more than one access.

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
- Add **jitter** (randomise each TTL by ±10%) so that keys loaded together do not all expire together (see lesson 7).

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

## What real systems do

Exact LRU needs a linked list with two pointers per key (16 bytes on a 64-bit machine) and a pointer update on every read, which also means a lock or atomic operation. At millions of keys and millions of reads per second, systems use **approximations**.

### Redis: sampled LRU and LFU

Redis does not keep a linked list. Each key stores a 24-bit field in its object header. In LRU mode it holds a coarse last-access clock. In LFU mode it holds an 8-bit frequency counter plus a 16-bit timestamp of the last decay.

When memory exceeds `maxmemory`, Redis:

1. Samples `maxmemory-samples` random keys (default **5**).
2. Adds the best candidates to a small **eviction pool** (16 entries) kept across rounds.
3. Evicts the best candidate in the pool.

With 5 samples, Redis's eviction is close to true LRU; with 10 it is nearly indistinguishable, at a little more CPU.

The **LFU** mode (since Redis 4.0) uses a probabilistic **logarithmic counter** in 8 bits. Each access increments it with a probability that falls as the counter grows, so 255 can represent around a million hits (tuned by `lfu-log-factor`, default 10). Elapsed decay is applied lazily when an object is accessed or considered for eviction (one per lfu-decay-time minute by default), rather than actively decrementing every idle key. New keys start at 5 rather than 0, so they are not evicted instantly.

To get a feel for the log counter, the Redis config file gives these figures for the default factor of 10:

| Hits | Counter |
|---|---|
| 100 | ~10 |
| 1,000 | ~18 |
| 100,000 | ~142 |
| 1,000,000 | 255 |

Below saturation, each increment happens with probability `1 / (max(counter − 5, 0) × lfu-log-factor + 1)`, so the counter climbs quickly at first and then ever more slowly.

Redis eviction policies, set via `maxmemory-policy`:

| Policy | Candidates | Rule |
|---|---|---|
| `noeviction` | none | Reject writes |
| `allkeys-lru` | all keys | Approx. LRU |
| `allkeys-lfu` | all keys | Approx. LFU |
| `volatile-lru` | keys with TTL | Approx. LRU |
| `volatile-lfu` | keys with TTL | Approx. LFU |
| `volatile-ttl` | keys with TTL | Soonest expiry |
| `*-random` | all / TTL | Random |

Redis 8.6 added `allkeys-lrm` and `volatile-lrm` (*least recently modified*), which only update the timestamp on writes, so keys that are read a lot but never updated can still be evicted.

> [!warning] The default is `noeviction`
> Out of the box, Redis does not evict. When its accounted memory is above the limit, memory-growing commands can fail with OOM while existing-key reads continue; maxmemory is not a strict RSS ceiling. For a pure cache you almost always want `allkeys-lru` or `allkeys-lfu`. The `volatile-*` policies evict nothing if no keys have a TTL.

### Memcached: segmented LRU per slab class

Memcached allocates memory in 1 MB **pages**, and assigns each page to a **slab class** that cuts it into fixed-size chunks (for example 96 B, 120 B, 152 B and so on, each class 1.25× the last by default). An item (key, value and a header of roughly 50 bytes) goes into the smallest chunk that fits it, so part of each chunk is usually wasted. Each class has its own LRU, split into **HOT, WARM and COLD** segments. New items enter HOT and flow down into COLD. Items that are hit again (while in HOT or COLD) move to WARM, where they are relatively protected. Items never hit again pass through COLD and out of the bottom, so a scan mostly churns COLD. A background "LRU crawler" also reclaims expired items.

A consequence: eviction is per slab class. If most of your memory was assigned to 1 KB chunks and your values shrink to 100 B, the small class can be evicting heavily while plenty of memory sits in the large class (Memcached has a slab rebalancer to help).

### Caffeine and W-TinyLFU

The Java library Caffeine uses **Window TinyLFU**. An adaptive LRU window admits new items. To enter the main cache, a candidate must have a higher estimated frequency than the item it would evict. Frequencies are kept in a compact **Count-Min Sketch** (a few bits per key) that is periodically halved. This is an **admission policy**: it decides not just what to evict but whether a new item is worth caching at all. It achieves near-optimal hit ratios across many traces.

### Operating systems: CLOCK

A traditional Linux reclaim design uses active/inactive LRU lists and referenced-bit information; calling it CLOCK is only an analogy, not its exact implementation. The textbook CLOCK algorithm works as follows. CLOCK arranges pages in a ring with a "referenced" bit. The hand sweeps round: a page with the bit set gets a second chance (bit cleared); a page with the bit clear is evicted. It approximates LRU with no list reordering on each access. Since Linux 6.1 the kernel also offers **MGLRU** (multi-generational LRU), which sorts pages into several age generations instead of two lists, and many distributions now enable it.

## Choosing a policy

1. **Start with LRU** (`allkeys-lru`). It is a good default for most web workloads.
2. Switch to **LFU** if scans or one-off reads are polluting the cache, or if there is a stable set of popular keys.
3. Always set **TTLs** on data that can go stale, independent of the eviction policy.
4. **Measure**: watch `evicted_keys` and the hit ratio in Redis `INFO stats`. Many evictions with a falling hit ratio means the cache is too small for the working set.

## Key takeaways
- Eviction is about capacity; expiry (TTL) is about freshness. You usually need both.
- LRU bets on recency and is O(1) with a hash map and linked list, but scans pollute it.
- LFU protects popular keys but needs decay so old favourites don't squat.
- Real systems approximate: Redis samples keys, Memcached uses segmented LRU per slab class, Caffeine uses W-TinyLFU, and Linux reclaim depends on its LRU/MGLRU configuration.
- Redis defaults to `noeviction`; set `allkeys-lru` or `allkeys-lfu` for a cache.

## Further reading
- [Key eviction — Redis docs](https://redis.io/docs/latest/develop/reference/eviction/)
- [Cache replacement policies — Wikipedia](https://en.wikipedia.org/wiki/Cache_replacement_policies)
- [TinyLFU: A Highly Efficient Cache Admission Policy (arXiv)](https://arxiv.org/abs/1512.00727)
- [Caffeine efficiency (W-TinyLFU) — GitHub wiki](https://github.com/ben-manes/caffeine/wiki/Efficiency)
- [Adaptive replacement cache — Wikipedia](https://en.wikipedia.org/wiki/Adaptive_replacement_cache)
- [Memcached wiki](https://github.com/memcached/memcached/wiki)
