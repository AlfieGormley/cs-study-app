---
id: cache-short-amat-dirty-victims
title: Account for dirty eviction penalties
level: intermediate
minutes: 3
sourceLesson: cache-arch-write-amat
summary: Unbuffered dirty write-backs add cost only for the dirty fraction of victims.
---

This unit builds on the earlier cache lessons and focuses on account for dirty eviction penalties. Keep each example’s stated hardware geometry and model assumptions when applying its result.

Use the serial blocking convention from the AMAT lessons: every access pays its cache lookup; a miss then pays an additional penalty. This unit adds a dirty-victim cost without overlapping write-back and fetch.

## Dirty evictions in the penalty

With write-back and no buffering, a miss that evicts a dirty line must write it back first, so the average miss penalty grows by the dirty fraction times the write-back cost. If 40% of victims are dirty and a write-back costs as much as a fetch (100 cycles):

```formula
t_penalty = t_fetch + d t_wb
t_penalty = 100 cycles + 0.4 × 100 cycles
t_penalty = 140 cycles
AMAT = t_hit + m t_penalty
AMAT = 4 cycles + 0.05 × 140 cycles
AMAT = 11 cycles
where
t_penalty: the average extra time of one miss, in clock cycles
t_fetch: the time to fetch the missing line, here 100 cycles
d: the fraction of evicted victim lines that are dirty, here 0.4
t_wb: the time to write one dirty line back first, here 100 cycles
AMAT: average memory access time, in clock cycles
t_hit: the L1 hit time, here 4 cycles
m: the L1 miss rate, here 0.05
cycles: clock cycles
In words: 4 in 10 misses must first write a dirty line back, adding 40 cycles to the average miss and 2 cycles to the average access.
```

A **write-back buffer** can hold the dirty victim while its write-back overlaps the fetch or later execution. The benefit depends on scheduling, available bandwidth, and buffer space; it is not guaranteed to recover a particular AMAT.

## Key takeaways
- Unbuffered dirty write-backs add cost only for the dirty fraction of victims.
- A write-back buffer can overlap traffic, subject to capacity and bandwidth.

## Further reading
- [CMU: Cache memories](https://www.cs.cmu.edu/afs/cs/academic/class/15213-m19/www/lectures/12-cache-memories.pdf)
- [Intel: Memory cache control](https://cdrdv2-public.intel.com/874249/253668-090-sdm-vol-3a.pdf)
- [Average memory access time — Wikipedia](https://en.wikipedia.org/wiki/Average_memory_access_time)
- [Cache (computing): writing policies — Wikipedia](https://en.wikipedia.org/wiki/Cache_(computing))
- [Cache inclusion policy — Wikipedia](https://en.wikipedia.org/wiki/Cache_inclusion_policy)
- [Write buffer — Wikipedia](https://en.wikipedia.org/wiki/Write_buffer)
- [Memory part 2: CPU caches, Ulrich Drepper (LWN)](https://lwn.net/Articles/252125/)
