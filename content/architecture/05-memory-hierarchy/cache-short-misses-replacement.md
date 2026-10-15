---
id: cache-short-misses-replacement
title: Classify misses and choose victims
level: intermediate
minutes: 3
sourceLesson: cache-arch-organisation
summary: Use first touch and a same-capacity fully associative LRU reference to distinguish the three Cs.
---

This unit builds on the earlier cache lessons and focuses on classify misses and choose victims. Keep each example’s stated hardware geometry and model assumptions when applying its result.

## The three Cs of misses

Classifying misses tells you what would fix them:

- **Compulsory miss** (cold miss): the first access to a line. Prefetching can turn a first demand access into a hit; changing line size or avoiding accesses also changes the count.
- **Capacity miss**: the working set is bigger than the cache. In the conventional three-C classification, a previously seen line also misses in a fully associative LRU reference cache of the same capacity and line size. Fix with a bigger cache or better locality (loop blocking).
- **Conflict miss**: a previously seen line misses here but hits in that fully associative reference cache, often because competing lines share a set. Fix with more associativity, or by changing addresses (padding).

Multicore systems add a fourth C, **coherence** misses, when another core invalidated your copy (see the coherence lesson).

## Replacement: choosing a victim

In a set-associative cache, allocating a new line into a full set requires a victim; a bypassed or no-write-allocate access need not allocate.

- **LRU**: evict the least recently used way. Exact LRU for 8 ways needs to track an ordering of 8 items per set, which is costly.
- Pseudo-LRU (tree-PLRU): for a power-of-two number of ways, a binary tree with one bit fewer than the number of ways in each set (7 bits for 8 ways) points roughly away from recent accesses. It uses less state than a full ordering, but can choose a different victim from true LRU.
- RRIP-style policies: give each line a small "re-reference prediction" counter to distinguish likely distant reuse from likely near reuse. A streaming line can receive a less favourable prediction than a reused line; those predictions do not guarantee a particular victim order on every trace. Such policies can resist scans; a particular processor’s policy requires implementation documentation.
- **Random replacement** (pseudo-random): choose a victim using a random or pseudo-random mechanism. This can avoid maintaining a recency order; effectiveness is trace-dependent.

## Key takeaways
- Use first touch and a same-capacity fully associative LRU reference to distinguish the three Cs.
- Replacement approximations and RRIP-style predictions are policies, not universal processor guarantees.

## Further reading
- [CMU: Cache memories](https://www.cs.cmu.edu/afs/cs/academic/class/15213-m19/www/lectures/12-cache-memories.pdf)
- [Cache placement policies — Wikipedia](https://en.wikipedia.org/wiki/Cache_placement_policies)
- [CPU cache — Wikipedia](https://en.wikipedia.org/wiki/CPU_cache)
- [Pseudo-LRU — Wikipedia](https://en.wikipedia.org/wiki/Pseudo-LRU)
- [CPU caches, Ulrich Drepper (LWN)](https://lwn.net/Articles/252125/)
- [Computer Systems: A Programmer's Perspective (CS:APP)](https://csapp.cs.cmu.edu/)
