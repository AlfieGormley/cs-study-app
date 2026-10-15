---
id: cache-short-amat-three-levels
title: Compute a three-level hierarchy
level: intermediate
minutes: 3
sourceLesson: cache-arch-write-amat
summary: Work from DRAM upwards, nesting local miss probabilities.
---

This unit builds on the earlier cache lessons and focuses on compute a three-level hierarchy. Keep each example’s stated hardware geometry and model assumptions when applying its result.

## Worked example 3: three levels

L1: 4 cycles, 10% miss. L2: 14 cycles, 40% local miss. L3: 50 cycles, 25% local miss. DRAM: 300 cycles. Work from the bottom up, each level's AMAT becoming the miss penalty of the level above:

```formula
AMAT_L3 = t_L3 + m_L3 t_DRAM
AMAT_L3 = 50 cycles + 0.25 × 300 cycles
AMAT_L3 = 125 cycles
AMAT_L2 = t_L2 + m_L2 AMAT_L3
AMAT_L2 = 14 cycles + 0.40 × 125 cycles
AMAT_L2 = 64 cycles
AMAT = t_L1 + m_L1 AMAT_L2
AMAT = 4 cycles + 0.10 × 64 cycles
AMAT = 10.4 cycles
where
AMAT_L3: average time of an access that reaches L3, in clock cycles
t_L3: L3 hit time, 50 cycles
m_L3: L3 local miss rate, 0.25
t_DRAM: extra time to fetch from DRAM, 300 cycles
AMAT_L2: average time of an access that reaches L2, in clock cycles
t_L2: L2 hit time, 14 cycles
m_L2: L2 local miss rate, 0.40
AMAT: average memory access time seen by the core
t_L1: L1 hit time, 4 cycles
m_L1: L1 miss rate, 0.10
cycles: clock cycles
In words: the cost of L3 sets L2's penalty, and the cost of L2 sets L1's penalty, giving 10.4 cycles per access.
```

The fraction of all accesses that go to DRAM is the product of the local miss rates:

```formula
m_{L3,global} = m_L1 m_L2 m_L3
m_{L3,global} = 0.10 × 0.40 × 0.25 = 0.01
where
m_{L3,global}: L3's global miss rate: the fraction of all accesses that reach DRAM, here 1%
m_L1: L1 miss rate, 0.10
m_L2: L2 local miss rate, 0.40
m_L3: L3 local miss rate, 0.25
In words: 10% reach L2, 40% of those reach L3, and 25% of those reach DRAM, so 1 access in 100 goes to DRAM.
```

The same recursion in Python:

```python
def amat(levels, memory_time):
    """levels: [(hit_time, local_miss)]
    from L1 downwards."""
    # Begin at DRAM, then wrap each cache.
    t = memory_time
    for hit, miss in reversed(levels):
        # Lookup plus expected lower cost.
        t = hit + miss * t
    return t

print(amat([(4, .05), (12, .20)], 200))
# 6.6 cycles per demand access
print(amat([(4, .10), (14, .40),
            (50, .25)], 300))
# 10.4 cycles per demand access
```

## Key takeaways
- Work from DRAM upwards, nesting local miss probabilities.
- The Python recurrence implements the same serial service-time model.

## Further reading
- [CMU: Cache memories](https://www.cs.cmu.edu/afs/cs/academic/class/15213-m19/www/lectures/12-cache-memories.pdf)
- [Intel: Memory cache control](https://cdrdv2-public.intel.com/874249/253668-090-sdm-vol-3a.pdf)
- [Average memory access time — Wikipedia](https://en.wikipedia.org/wiki/Average_memory_access_time)
- [Cache (computing): writing policies — Wikipedia](https://en.wikipedia.org/wiki/Cache_(computing))
- [Cache inclusion policy — Wikipedia](https://en.wikipedia.org/wiki/Cache_inclusion_policy)
- [Write buffer — Wikipedia](https://en.wikipedia.org/wiki/Write_buffer)
- [Memory part 2: CPU caches, Ulrich Drepper (LWN)](https://lwn.net/Articles/252125/)
