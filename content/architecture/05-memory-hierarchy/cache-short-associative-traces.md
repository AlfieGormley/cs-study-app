---
id: cache-short-associative-traces
title: Trace conflicts and associativity
level: intermediate
minutes: 3
sourceLesson: cache-arch-organisation
summary: Two lines sharing one direct-mapped slot can evict each other while other slots are empty.
---

This unit builds on the earlier cache lessons and focuses on trace conflicts and associativity. Keep each example’s stated hardware geometry and model assumptions when applying its result.

## Direct-mapped: simple but fragile

Each line has exactly one home. Lookup needs one candidate tag comparison in this model, reducing comparison hardware. The weakness is conflict: two hot lines whose addresses share an index keep evicting each other, even if the rest of the cache is empty.

Take a tiny 128-byte cache with 16-byte lines (8 lines) and this trace, with an initially empty cache, demand-only reads and no interference:

```
 0x00 0x04 0x80 0x00 0x84 0x10 0x90 0x10
```

Direct-mapped, 8 sets: offset 4 bits, index 3 bits. `0x00` and `0x80` both have index 0 (tags 0 and 1); `0x10` and `0x90` both have index 1.

| Addr | Set | Tag | Result |
|---|---|---|---|
| 0x00 | 0 | 0 | miss |
| 0x04 | 0 | 0 | hit |
| 0x80 | 0 | 1 | miss (evicts 0) |
| 0x00 | 0 | 0 | miss (evicts 1) |
| 0x84 | 0 | 1 | miss |
| 0x10 | 1 | 0 | miss |
| 0x90 | 1 | 1 | miss |
| 0x10 | 1 | 0 | miss |

1 hit in 8, with six of the eight lines sitting empty the whole time.

## Set-associative: the usual compromise

Make the same 128 bytes 2-way: 4 sets of 2 ways. Now the index is 2 bits; the tag occupies the address width minus 6 bits (2 tag bits if addresses are 8 bits). `0x00` (tag 0) and `0x80` (tag 2) both go to set 0, but there are two ways, so they coexist. With LRU replacement:

| Addr | Set | Tag | Result |
|---|---|---|---|
| 0x00 | 0 | 0 | miss |
| 0x04 | 0 | 0 | hit |
| 0x80 | 0 | 2 | miss |
| 0x00 | 0 | 0 | hit |
| 0x84 | 0 | 2 | hit |
| 0x10 | 1 | 0 | miss |
| 0x90 | 1 | 2 | miss |
| 0x10 | 1 | 0 | hit |

4 hits in 8. The remaining misses are all first-time (compulsory) misses. Making it fully associative would not help this trace any further.

The price of associativity is hardware: one tag comparator per way, all working in parallel, a multiplexer to choose the hitting way, and replacement state. More ways usually means slightly higher hit time and power. Exact associativities depend on the named cache.

> A generic L1/L2/L3 associativity table is omitted because the earlier ranges were not verified against a representative set of specified processors.

## Key takeaways
- Two lines sharing one direct-mapped slot can evict each other while other slots are empty.
- More ways allow several such lines to coexist, at a hardware cost.

## Further reading
- [CMU: Cache memories](https://www.cs.cmu.edu/afs/cs/academic/class/15213-m19/www/lectures/12-cache-memories.pdf)
- [Cache placement policies — Wikipedia](https://en.wikipedia.org/wiki/Cache_placement_policies)
- [CPU cache — Wikipedia](https://en.wikipedia.org/wiki/CPU_cache)
- [Pseudo-LRU — Wikipedia](https://en.wikipedia.org/wiki/Pseudo-LRU)
- [CPU caches, Ulrich Drepper (LWN)](https://lwn.net/Articles/252125/)
- [Computer Systems: A Programmer's Perspective (CS:APP)](https://csapp.cs.cmu.edu/)
