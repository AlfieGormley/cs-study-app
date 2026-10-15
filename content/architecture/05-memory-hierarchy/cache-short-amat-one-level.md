---
id: cache-short-amat-one-level
title: Average one blocking-cache access
level: intermediate
minutes: 4
sourceLesson: cache-arch-write-amat
summary: The initial lookup is paid on every access in the serial blocking model.
---

This unit builds on the earlier cache lessons and focuses on average one blocking-cache access. Keep each example’s stated hardware geometry and model assumptions when applying its result.

## Average memory access time

How fast is "the memory" when some accesses hit in a fast cache and some go much further? A single average answers that. For the serial, blocking lookup model used here (look in the cache, and only after a miss go to the next level, with the core waiting the whole time), AMAT is the expected service time of one memory access:

```formula
AMAT = t_hit + m t_penalty
where
AMAT: average memory access time: the expected time one memory access takes, in clock cycles (or nanoseconds)
t_hit: the hit time: how long a lookup in this cache takes, in clock cycles; paid on every access, hit or miss, because you always look in the cache first
m: the miss rate: the fraction of accesses that miss in this cache, a number from 0 to 1 (5% is 0.05)
t_penalty: the miss penalty: the extra time a miss costs on top of the lookup, in clock cycles; the time to get the data from the next level down
In words: every access pays the lookup, and the fraction that miss also pay the extra trip to the next level.
```

The formula comes from averaging: hits pay the lookup alone; misses pay the lookup plus the extra penalty. Weighting those costs by their hit and miss fractions simplifies to the card’s expression. It holds only while accesses are served one at a time and every miss is fully exposed to the core. The **hit time** is paid on every access, and the **miss penalty** is the *extra* time when you miss.

## Worked example 1: one level

L1 hit time 4 cycles, miss rate 5%, miss penalty 100 cycles.

```formula
AMAT = t_hit + m t_penalty
AMAT = 4 cycles + 0.05 × 100 cycles
AMAT = 4 cycles + 5 cycles
AMAT = 9 cycles
where
AMAT: average memory access time, in clock cycles
t_hit: the L1 hit time, here 4 cycles
m: the L1 miss rate as a fraction, here 5% = 0.05
t_penalty: the extra time per L1 miss, here 100 cycles
cycles: clock cycles, the processor's basic tick of time (at an assumed 4 GHz one cycle is 0.25 ns)
In words: a 4-cycle cache that misses 1 time in 20, with a 100-cycle penalty, averages 9 cycles per access.
```

The extra miss penalty contributes 5 cycles per access, versus 4 cycles for the lookup paid on every access. In the alternative weighted form below, only hit events contribute 3.8 cycles.

## Two conventions, same answer

Some books weight hits and misses separately, and count the whole time of a miss, including its initial lookup:

```formula
AMAT = h t_hit + m t_miss
t_miss = t_hit + t_penalty
t_miss = 4 cycles + 100 cycles = 104 cycles
AMAT = 0.95 × 4 cycles + 0.05 × 104 cycles
AMAT = 3.8 cycles + 5.2 cycles = 9 cycles
where
AMAT: average memory access time, in clock cycles
h: the hit rate, the fraction of accesses that hit: 1 − m, here 0.95
m: the miss rate, here 0.05
t_hit: the hit time, here 4 cycles
t_miss: the total time of a miss, lookup included, here 104 cycles
t_penalty: the extra time a miss costs beyond the lookup, here 100 cycles
cycles: clock cycles
In words: weighting hits by the hit time and misses by their full time gives the same 9 cycles as the first form.
```

Same result. Mixing the conventions by treating the 100-cycle extra penalty as the entire miss time gives 8.8 cycles, which undercounts the initial lookup on misses. Always check whether a quoted penalty includes the hit time.

## Key takeaways
- The initial lookup is paid on every access in the serial blocking model.
- Use either incremental miss penalty or total miss time consistently.

## Further reading
- [CMU: Cache memories](https://www.cs.cmu.edu/afs/cs/academic/class/15213-m19/www/lectures/12-cache-memories.pdf)
- [Intel: Memory cache control](https://cdrdv2-public.intel.com/874249/253668-090-sdm-vol-3a.pdf)
- [Average memory access time — Wikipedia](https://en.wikipedia.org/wiki/Average_memory_access_time)
- [Cache (computing): writing policies — Wikipedia](https://en.wikipedia.org/wiki/Cache_(computing))
- [Cache inclusion policy — Wikipedia](https://en.wikipedia.org/wiki/Cache_inclusion_policy)
- [Write buffer — Wikipedia](https://en.wikipedia.org/wiki/Write_buffer)
- [Memory part 2: CPU caches, Ulrich Drepper (LWN)](https://lwn.net/Articles/252125/)
