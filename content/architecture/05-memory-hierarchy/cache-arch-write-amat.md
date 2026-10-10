---
id: cache-arch-write-amat
title: Write policies and AMAT
level: intermediate
minutes: 13
summary: What happens on a store (write-through vs write-back, write-allocate vs no-write-allocate), how inclusion works between levels, and how to calculate average memory access time and stall CPI in an explicit blocking-cache model.
---

Reads are the easy half of caching: if the line is present, return it; if not, fetch it. Writes raise harder questions. When a store hits in L1, does memory get updated now or later? When a store misses, do we bother fetching the line at all? The answers change how much traffic flows between levels, and that changes performance.

The second half of this lesson turns all of this into one number: the **average memory access time** (AMAT), and from it the cost in cycles per instruction.

## On a write hit: write-through or write-back

### Write-through

Every store updates the cached copy and must be propagated to the next level. A **write buffer** can defer or merge those updates, so the next level need not reflect a pending store immediately.

- A clean write-through line does not need a dirty eviction write-back; pending buffered writes still must complete correctly.
- Without write merging, one million issued stores send one million writes downstream. Merging can reduce that traffic.
- A full write buffer can stall further stores.

### Write-back

A store updates the cache line and marks it **dirty** (it sets the line's dirty bit). Modified data is propagated when required, for example on dirty eviction, explicit write-back, or a coherence request; eviction is not the only trigger.

- Repeated local writes can avoid repeated downstream data writes while the core retains ownership. They still consume execution/cache resources.
- In the simple allocate-on-miss model, replacing a dirty victim requires preserving its data and fetching the incoming line.
- A lower cache or DRAM may hold stale data, so coherent agents must obtain the current copy through the coherence mechanism. Non-coherent DMA requires the platform's cache-maintenance rules.

The following traffic example assumes no write merging, no intervening coherence requests, and one final eviction:

```
 write-through       write-back
 x=1 -> L1 and L2    x=1 -> L1 (dirty)
 x=2 -> L1 and L2    x=2 -> L1 (dirty)
 x=3 -> L1 and L2    x=3 -> L1 (dirty)
                     evict -> L2 gets 3
 3 writes to L2      1 write to L2
```

Write-back is common for ordinary cacheable memory, but policies depend on the processor, cache level, memory type, and instruction. A processor-by-processor policy catalogue is absent here because those specific configurations have not been reliably verified.

## On a write miss: allocate or not

- **Write-allocate**: allocate a cache line on a store miss, then update it. A partial-line store commonly fetches the old line; hardware may avoid that fetch for a complete overwrite. Good if you will read or write nearby data soon.
- **No-write-allocate** (write-around): send the write to the next level and leave the cache alone. Good for data you will not touch again.

The natural pairings are **write-back + write-allocate** (the usual choice) and **write-through + no-write-allocate**.

In a coherent fetch-on-write model, a store miss requests exclusive permission, often through a **read for ownership** (RFO) transaction that also obtains the line. Data may come from another cache rather than DRAM. A full-line overwrite may permit an implementation to omit the old-data fetch.

> [!example] Modelled traffic for overwriting 64 MiB
> Assume aligned 64-byte lines initially absent from all caches, no useful old data, no write-fetch elimination, and eventual write-back of every dirty line. Ordinary fetch-on-write stores read 64 MiB and write 64 MiB: **128 MiB** of DRAM data traffic.
> In an ideal full-line streaming-store path that avoids allocation/old-data reads, the corresponding data traffic is **64 MiB**. Real non-temporal instructions and library thresholds are implementation-specific; this is a traffic model, not a guarantee for every `memset` call.

## Inclusion between levels

These properties apply to the particular pair or collection of cache levels being discussed:

- **Inclusive hierarchy**: presence in an included upper level implies presence in the lower level. The lower copy need not contain the newest bytes when an upper copy is dirty. Evicting the lower entry requires invalidating the included upper entries. Inclusion can help filter snoops, at the cost of duplicated capacity.
- **Exclusive hierarchy**: a line is resident in only one of the specified levels. Their nominal capacities can therefore add without duplication between those levels; other caches and metadata remain separate concerns.
- **Neither inclusive nor exclusive (NINE)**: neither presence nor absence in one level guarantees the corresponding state in another. “Non-inclusive” alone does not necessarily rule out an exclusive design.

Specific processor-generation inclusion policies are not catalogued here because the necessary configuration-specific verification is unavailable in this lesson.



## Average memory access time

How fast is "the memory" when some accesses hit in a fast cache and some go much further? A single average answers that. For the serial, blocking lookup model used here (look in the cache, and only after a miss go to the next level, with the core waiting the whole time), AMAT is the expected service time of one memory access:

```formula
AMAT = t_hit + m × t_penalty
where
AMAT: average memory access time: the expected time one memory access takes, in clock cycles (or nanoseconds)
t_hit: the hit time: how long a lookup in this cache takes, in clock cycles; paid on every access, hit or miss, because you always look in the cache first
m: the miss rate: the fraction of accesses that miss in this cache, a number from 0 to 1 (5% is 0.05)
t_penalty: the miss penalty: the extra time a miss costs on top of the lookup, in clock cycles; the time to get the data from the next level down
In words: every access pays the lookup, and the fraction that miss also pay the extra trip to the next level.
```

The formula comes from averaging: a fraction (1 − m) of accesses take t_hit and a fraction m take t_hit + t_penalty, and those two terms add up to t_hit + m × t_penalty. It holds only while accesses are served one at a time and every miss is fully exposed to the core. The **hit time** is paid on every access, and the **miss penalty** is the *extra* time when you miss.

### Worked example 1: one level

L1 hit time 4 cycles, miss rate 5%, miss penalty 100 cycles.

```formula
AMAT = t_hit + m × t_penalty
AMAT = 4 cycles + 0.05 × 100 cycles
AMAT = 4 cycles + 5 cycles
AMAT = 9 cycles
where
AMAT: average memory access time, in clock cycles
t_hit: the L1 hit time, here 4 cycles
m: the L1 miss rate as a fraction, here 5% = 0.05
t_penalty: the extra time per L1 miss, here 100 cycles
cycles: clock cycles, the processor's basic tick of time (at 4 GHz one cycle is 0.25 ns)
In words: a 4-cycle cache that misses 1 time in 20, with a 100-cycle penalty, averages 9 cycles per access.
```

The extra miss penalty contributes 5 cycles per access, versus 4 cycles for the lookup paid on **every** access. The hit-only contribution in the alternative weighted form below is 0.95 × 4 = 3.8 cycles.

### Two conventions, same answer

Some books weight hits and misses separately, and count the whole time of a miss, including its initial lookup:

```formula
AMAT = h × t_hit + m × t_miss
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

Same result. Mixing the conventions (using 100 as the total miss time) gives 0.95 × 4 + 0.05 × 100 = 8.8 cycles, which is wrong. Always check whether a quoted penalty includes the hit time.

### Worked example 2: two levels

With two caches, the L1 miss penalty is no longer a fixed number: an L1 miss goes to L2, which itself may hit or miss. So the L1 miss penalty is the AMAT of everything below L1, and the formula nests. In this serial model, the miss penalty of L1 is the incremental time spent accessing L2 and any lower level. The table uses incremental lookup times, not end-to-end latencies that already include earlier lookups.

| Level | Hit time | Local miss rate |
|---|---|---|
| L1 | 4 cycles | 5% |
| L2 | 12 cycles | 20% |
| DRAM | 200 cycles | - |

```formula
AMAT_L2 = t_L2 + m_L2 × t_DRAM
AMAT_L2 = 12 cycles + 0.20 × 200 cycles
AMAT_L2 = 52 cycles
AMAT = t_L1 + m_L1 × AMAT_L2
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

### Local vs global miss rate

The miss rate of a lower cache can be measured against two different counts, and the two give very different numbers.

```formula
m_local = N_miss / N_reach
m_global = N_miss / N_all
m_{L2,global} = m_L1 × m_{L2,local}
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

The lesson's L2 figure of 20% is a **local miss rate**: of the 5% of accesses that reach L2, 20% miss, so its **global miss rate** is **1%**. These products describe the same stream of demand accesses filtered through successive levels, ignoring additional prefetch, write-back, and coherence traffic. Use local rates in the nested formula. A quoted L2 miss rate of "20%" sounds terrible but, here, only 1 access in 100 goes to DRAM.

### Worked example 3: three levels

L1: 4 cycles, 10% miss. L2: 14 cycles, 40% local miss. L3: 50 cycles, 25% local miss. DRAM: 300 cycles. Work from the bottom up, each level's AMAT becoming the miss penalty of the level above:

```formula
AMAT_L3 = t_L3 + m_L3 × t_DRAM
AMAT_L3 = 50 + 0.25 × 300 = 125 cycles
AMAT_L2 = t_L2 + m_L2 × AMAT_L3
AMAT_L2 = 14 + 0.40 × 125 = 64 cycles
AMAT = t_L1 + m_L1 × AMAT_L2
AMAT = 4 + 0.10 × 64 = 10.4 cycles
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
m_{L3,global} = m_L1 × m_L2 × m_L3
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
    t = memory_time
    for hit, miss in reversed(levels):
        t = hit + miss * t
    return t

print(amat([(4, .05), (12, .20)], 200))
# 6.6
print(amat([(4, .10), (14, .40),
            (50, .25)], 300))
# 10.4
```

### Dirty evictions in the penalty

With write-back and no buffering, a miss that evicts a dirty line must write it back first, so the average miss penalty grows by the dirty fraction times the write-back cost. If 40% of victims are dirty and a write-back costs as much as a fetch (100 cycles):

```formula
t_penalty = t_fetch + d × t_wb
t_penalty = 100 + 0.4 × 100 = 140 cycles
AMAT = t_hit + m × t_penalty
AMAT = 4 + 0.05 × 140 = 11 cycles
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

## From AMAT to CPI

AMAT tells you the cost of one access; what you usually care about is total run time. The "iron law" of processor performance splits run time into three factors:

```formula
T_CPU = N_instr × CPI × t_cycle
where
T_CPU: the CPU time the program takes, in seconds (s)
N_instr: the number of instructions executed
CPI: cycles per instruction: the average number of clock cycles each instruction takes
t_cycle: the clock period, the length of one cycle, in seconds; 0.25 ns at 4 GHz
In words: run time is how many instructions you execute, times how many cycles each takes on average, times how long a cycle is.
```

Memory stalls make each instruction take more cycles, so for a simple in-order core that blocks on misses they add directly to CPI:

```formula
CPI = CPI_base + r × m × t_penalty
where
CPI: cycles per instruction including memory stalls
CPI_base: cycles per instruction with a perfect cache, cache-hit cost already included
r: memory references per instruction: how many loads and stores an average instruction makes, e.g. 0.4
m: the miss rate of the cache those references use, a fraction from 0 to 1
t_penalty: the extra cycles each miss costs, in clock cycles
In words: each instruction makes r memory references, a fraction m of them miss, and each miss stalls the core for the penalty.
```

Assume base CPI already includes cache-hit execution cost and that miss penalties cannot overlap. With base CPI 1.0, 0.4 data references per instruction, L1d (level-1 data cache) miss rate 5%, and an L1 miss penalty of 52 cycles (the L2 AMAT above):

```formula
S = r × m × t_penalty
S = 0.4 × 0.05 × 52 = 1.04 cycles
CPI = CPI_base + S
CPI = 1.0 + 1.04 = 2.04 cycles
where
S: memory stall cycles per instruction
r: data references per instruction, 0.4
m: L1d miss rate, 0.05
t_penalty: L1 miss penalty, 52 cycles
CPI: cycles per instruction, with stalls
CPI_base: cycles per instruction with no misses, 1.0
cycles: clock cycles (per instruction here)
In words: each instruction loses 1.04 cycles to data misses, which roughly doubles CPI from 1.0 to 2.04.
```

About half of all cycles (1.04 of 2.04) are spent waiting for memory. Instruction fetches add a stall term of their own, using one reference per instruction and the L1i (level-1 instruction cache) miss rate, if the L1i misses. The model breaks down once misses overlap: see the first pitfall below.

## Trade-offs and pitfalls

- **AMAT is a model for blocking caches.** Out-of-order cores keep running independent instructions during a miss and can have many misses outstanding at once (**memory-level parallelism**). Ten overlapped 100-cycle misses do not cost 1,000 cycles. AMAT alone cannot reliably rank such designs or predict total stall time: dependency chains, overlap, bandwidth, and queueing can change the result.
- **Average hides the tail.** A loop with 99% hits can still be dominated by the 1% if those are DRAM misses.
- **Evaluate hit time and miss rate together.** In this model L1 lookup time is paid on every access; lower-level costs are weighted by how often accesses reach them. Which change matters most depends on the workload and trade-off.
- **Write-allocate can double traffic** for streaming writes; use streaming stores or library routines that do.

## Key takeaways
- Write-through propagates stores, possibly through a merging buffer; write-back tracks dirty data and propagates it when required, including eviction or coherence events.
- Write-allocate allocates a line on a store miss. A partial-line update often needs old bytes and exclusive permission; a full-line streaming path may avoid the old-data read.
- AMAT is the hit time plus the miss rate times the miss penalty. With several levels, apply it from the bottom up, using local miss rates; each level's AMAT is the miss penalty of the level above.
- A level's global miss rate is the product of the local miss rates from L1 down to that level.
- For non-overlapping blocking misses, the stall cycles per instruction are the references per instruction times the miss rate times the extra penalty; add them to a base CPI that already includes hits.

## Further reading
- [CMU: Cache memories](https://www.cs.cmu.edu/afs/cs/academic/class/15213-m19/www/lectures/12-cache-memories.pdf)
- [Intel: Memory cache control](https://cdrdv2-public.intel.com/874249/253668-090-sdm-vol-3a.pdf)
- [Average memory access time — Wikipedia](https://en.wikipedia.org/wiki/Average_memory_access_time)
- [Cache (computing): writing policies — Wikipedia](https://en.wikipedia.org/wiki/Cache_(computing))
- [Cache inclusion policy — Wikipedia](https://en.wikipedia.org/wiki/Cache_inclusion_policy)
- [Write buffer — Wikipedia](https://en.wikipedia.org/wiki/Write_buffer)
- [Memory part 2: CPU caches, Ulrich Drepper (LWN)](https://lwn.net/Articles/252125/)
