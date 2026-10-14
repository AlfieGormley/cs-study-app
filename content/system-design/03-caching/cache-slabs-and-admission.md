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

Memcached 1.6.39 defaults to 1 MiB (1,048,576-byte) **pages**, and assigns each page to a **slab class** that cuts it into fixed-size chunks (for example 96 B, 120 B, 152 B and so on, each class 1.25× the last by default). The chunk sizes grow geometrically:

```formula
S_{k+1} ≈ S_k × g
S_2 = 96 B × 1.25 = 120 B
S_3 = 120 B × 1.25 = 150 B → 152 B
where
S_k: the chunk size of slab class number k, in bytes (B)
S_{k+1}: the chunk size of the next class up
S_2, S_3: the chunk sizes of the second and third classes; the illustrative first class, S_1, is 96 B; its actual size depends on item-header size and configuration
g: the growth factor (Memcached's -f option), default 1.25
→: "is rounded up to"; the usual 64-bit build aligns chunk sizes to a multiple of 8 bytes
≈: approximately equal; alignment changes the exact next-class size
B: bytes
In words: each slab class's chunks are about 25% bigger than the class below, rounded up to a multiple of 8 bytes.
```

An item (key, value and a build-dependent header, roughly 50 bytes in this illustrative sizing) goes into the smallest chunk that fits it, so part of each chunk is usually wasted. A smaller growth factor wastes less space per item but needs more classes.

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
