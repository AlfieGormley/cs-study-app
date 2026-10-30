---
id: cache-slabs-and-admission
title: Protect hot data with segments and admission
level: intermediate
minutes: 3
summary: Explain Memcached slab pressure and compare segmented LRU with Caffeine’s frequency-based admission.
sourceLesson: cache-eviction
---

A cache can choose where an item fits and whether it deserves protected capacity at all. Segments and admission decisions help avoid replacing a hot set with a stream of one-off reads.

### Memcached: segmented LRU per slab class

Memcached 1.6.39 defaults to 1 MiB (1,048,576-byte) **pages**, and assigns each page to a **slab class** that cuts it into fixed-size chunks. The chunk sizes step up by a fixed ratio: by default each class's chunks are about 1.25 times the size of the class below (set by Memcached's `-f` option), rounded up for alignment, giving classes such as 96 B, 120 B, 152 B and so on.

An item (key, value and a build-dependent header) goes into the smallest chunk that fits it, so part of each chunk is usually wasted. A smaller ratio wastes less space per item but needs more classes.

> [!analogy] Real-world analogy: a car park with fixed bay sizes
> A car park paints sections of bays for motorbikes, cars or vans as each kind of vehicle arrives, until the whole car park is painted. Each vehicle takes the smallest bay it fits, so a small car in a van bay wastes space.
>
> **How it maps:** The car park is Memcached's memory, the painted sections are pages assigned to slab classes, bay sizes are chunk sizes, and parking in the smallest bay that fits is placing an item in the smallest chunk that holds it.
>
> **Where it stops:** If everyone switches to motorbikes, the motorbike section fills and turns people away while van bays sit empty. Memcached has the same problem (below), but its slab rebalancer can gradually repaint sections, and a cache evicts an old item rather than turning the new one away.

Each class has its own LRU, split into **HOT, WARM and COLD** segments. New items enter HOT and flow down into COLD. Items that are hit again (while in HOT or COLD) move to WARM, where they are relatively protected. Items never hit again pass through COLD and out of the bottom, so a scan mostly churns COLD. A background "LRU crawler" also reclaims expired items.

A consequence: eviction is per slab class. If most of your memory was assigned to 1 KB chunks and your values shrink to 100 B, the small class can be evicting heavily while plenty of memory sits in the large class (Memcached has a slab rebalancer to help).

### Caffeine and W-TinyLFU

The Java library Caffeine uses **Window TinyLFU**. An adaptive LRU window admits new items. The main-cache admission decision compares the candidate’s estimated frequency with the victim’s. In Caffeine 3.2.3 a higher frequency is accepted; warmer candidates can also be accepted with a small random probability to resist hash-collision attacks. Frequencies are kept in a compact **Count-Min Sketch** (few-bit counters in shared hashed buckets) that is periodically halved. This is an **admission policy**: it decides not just what to evict but whether a new item is worth caching at all. Its authors report strong hit ratios across their benchmark traces; results depend on workload and implementation.

## Key takeaways
- Memcached allocates items into size classes, so one class can be under eviction pressure while another has spare capacity.
- HOT, WARM and COLD segments give reused items more protection than new or one-off items.
- Caffeine’s W-TinyLFU compares estimated frequency before admitting a candidate to the main cache.

## Further reading
- [Memcached modern LRU](https://memcached.org/blog/modern-lru/)
- [Memcached wiki](https://github.com/memcached/memcached/wiki)
- [TinyLFU: A Highly Efficient Cache Admission Policy](https://arxiv.org/abs/1512.00727)
- [Caffeine 3.2.3 admission implementation](https://raw.githubusercontent.com/ben-manes/caffeine/v3.2.3/caffeine/src/main/java/com/github/benmanes/caffeine/cache/BoundedLocalCache.java)
- [Memcached 1.6.39 slab implementation](https://raw.githubusercontent.com/memcached/memcached/1.6.39/slabs.c)
- [Caffeine efficiency (W-TinyLFU)](https://github.com/ben-manes/caffeine/wiki/Efficiency)
