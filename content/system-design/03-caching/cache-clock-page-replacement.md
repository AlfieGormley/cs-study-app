---
id: cache-clock-page-replacement
title: Trace the CLOCK second-chance algorithm
level: intermediate
minutes: 1
summary: Follow a CLOCK hand through reference bits and distinguish the textbook algorithm from Linux reclaim.
sourceLesson: cache-eviction
---

An operating-system page cache also needs victims. CLOCK approximates recency using one reference bit per page, avoiding a list update on every access.

### Operating systems: CLOCK

A traditional Linux reclaim design uses active/inactive LRU lists and referenced-bit information; calling it CLOCK is only an analogy, not its exact implementation. The textbook CLOCK algorithm works as follows. CLOCK arranges pages in a ring with a "referenced" bit. The hand sweeps round: a page with the bit set gets a second chance (bit cleared); a page with the bit clear is evicted. It approximates LRU with no list reordering on each access. Current Linux kernels also offer **MGLRU** (multi-generational LRU), which sorts pages into several age generations instead of two lists. Whether it is enabled depends on kernel configuration and runtime settings.

## Key takeaways
- A referenced page gets a second chance: clear its bit and continue sweeping.
- The first page encountered with a clear reference bit is evicted.
- CLOCK is a teaching model; Linux reclaim uses its configured LRU or multi-generational LRU implementation.

## Further reading
- [Multi-gen LRU — Linux kernel documentation](https://docs.kernel.org/admin-guide/mm/multigen_lru.html)
- [Cache replacement policies — Wikipedia](https://en.wikipedia.org/wiki/Cache_replacement_policies)
