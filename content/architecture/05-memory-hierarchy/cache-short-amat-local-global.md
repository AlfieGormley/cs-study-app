---
id: cache-short-amat-local-global
title: Nested AMAT and local miss rates
level: intermediate
minutes: 4
sourceLesson: cache-arch-write-amat
summary: Use the average cost of the lower levels as the upper miss penalty.
---

This unit builds on the earlier cache lessons and focuses on nested amat and local miss rates. Keep each example’s stated hardware geometry and model assumptions when applying its result.

## Worked example 2: two levels

With two caches, the L1 miss penalty is no longer a fixed number: an L1 miss goes to L2, which itself may hit or miss. So the L1 miss penalty is the AMAT of everything below L1, and the formula nests. In this serial model, the miss penalty of L1 is the incremental time spent accessing L2 and any lower level. The table uses incremental lookup times, not end-to-end latencies that already include earlier lookups.

| Level | Hit time | Local miss rate |
|---|---|---|
| L1 | 4 cycles | 5% |
| L2 | 12 cycles | 20% |
| DRAM | 200 cycles | - |

```formula
AMAT_L2 = t_L2 + m_L2 t_DRAM
AMAT_L2 = 12 cycles + 0.20 × 200 cycles
AMAT_L2 = 52 cycles
AMAT = t_L1 + m_L1 AMAT_L2
AMAT = 4 cycles + 0.05 × 52 cycles
AMAT = 4 cycles + 2.6 cycles = 6.6 cycles
where
AMAT_L2: the average time of an access that reaches L2, in clock cycles; this is L1's miss penalty
t_L2: the L2 hit time, here 12 cycles
m_L2: L2's local miss rate (of the accesses that reach L2, the fraction that miss), here 0.20
t_DRAM: the extra time to fetch from DRAM (main memory) after an L2 miss, here 200 cycles
AMAT: the average memory access time seen by the core, in clock cycles
t_L1: the L1 hit time, here 4 cycles
m_L1: L1's miss rate, here 0.05
cycles: clock cycles
In words: work out the average cost of going to L2 first, then use it as L1's miss penalty.
```

Adding a level does not change the formula; it only replaces a fixed miss penalty with the AMAT of the level below.

## Local vs global miss rate

The miss rate of a lower cache can be measured against two different counts, and the two give very different numbers.

```formula
m_local = N_miss / N_reach
m_global = N_miss / N_all
m_{L2,global} = m_L1 m_{L2,local}
m_{L2,global} = 0.05 × 0.20 = 0.01
where
m_local: the local miss rate of a cache level, a fraction from 0 to 1
N_miss: the number of misses in that level
N_reach: the number of accesses that actually reach that level (for L2, the L1 misses)
m_global: the global miss rate of that level, a fraction from 0 to 1
N_all: the number of memory accesses the CPU made in total
m_{L2,global}: L2's global miss rate, here 0.01 = 1%
m_L1: L1's miss rate, here 0.05
m_{L2,local}: L2's local miss rate, here 0.20
In words: local counts misses against the accesses that got as far as this level; global counts them against every access, so it is the product of the local rates on the way down.
```

This unit’s L2 figure of 20% is a **local miss rate**: of the 5% of accesses that reach L2, 20% miss, so its **global miss rate** is 1%. These products describe the same stream of demand accesses filtered through successive levels, ignoring additional prefetch, write-back, and coherence traffic. Use local rates in the nested formula. A quoted L2 miss rate of "20%" sounds terrible but, here, only 1 access in 100 goes to DRAM.

## Key takeaways
- Use the average cost of the lower levels as the upper miss penalty.
- A lower level’s local and global miss rates use different denominators.

## Further reading
- [CMU: Cache memories](https://www.cs.cmu.edu/afs/cs/academic/class/15213-m19/www/lectures/12-cache-memories.pdf)
- [Intel: Memory cache control](https://cdrdv2-public.intel.com/874249/253668-090-sdm-vol-3a.pdf)
- [Average memory access time — Wikipedia](https://en.wikipedia.org/wiki/Average_memory_access_time)
- [Cache (computing): writing policies — Wikipedia](https://en.wikipedia.org/wiki/Cache_(computing))
- [Cache inclusion policy — Wikipedia](https://en.wikipedia.org/wiki/Cache_inclusion_policy)
- [Write buffer — Wikipedia](https://en.wikipedia.org/wiki/Write_buffer)
- [Memory part 2: CPU caches, Ulrich Drepper (LWN)](https://lwn.net/Articles/252125/)
