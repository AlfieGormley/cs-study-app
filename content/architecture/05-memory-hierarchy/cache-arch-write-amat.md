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

A store updates the cache line and marks it **dirty**. Modified data is propagated when required, for example on dirty eviction, explicit write-back, or a coherence request; eviction is not the only trigger.

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

- **Inclusive**: presence in an included upper level implies presence in the lower level. The lower copy need not contain the newest bytes when an upper copy is dirty. Evicting the lower entry requires invalidating the included upper entries. Inclusion can help filter snoops, at the cost of duplicated capacity.
- **Exclusive**: a line is resident in only one of the specified levels. Their nominal capacities can therefore add without duplication between those levels; other caches and metadata remain separate concerns.
- **Neither inclusive nor exclusive (NINE)**: neither presence nor absence in one level guarantees the corresponding state in another. “Non-inclusive” alone does not necessarily rule out an exclusive design.

Specific processor-generation inclusion policies are not catalogued here because the necessary configuration-specific verification is unavailable in this lesson.



## Average memory access time

For the serial, blocking lookup model used here, AMAT is the expected service time of one memory access:

```
 AMAT = hit time + miss rate x miss penalty
```

Here the **hit time** is paid on every access (you always look in the cache first), and the **miss penalty** is the *extra* time when you miss.

### Worked example 1: one level

L1 hit time 4 cycles, miss rate 5%, miss penalty 100 cycles.

```
 AMAT = 4 + 0.05 x 100
      = 4 + 5
      = 9 cycles
```

The extra miss penalty contributes 5 cycles per access, versus 4 cycles for the lookup paid on **every** access. The hit-only contribution in the alternative weighted form is 0.95 × 4 = 3.8 cycles.

### Two conventions, same answer

Some books write AMAT = (hit rate × hit time) + (miss rate × total miss time), where the total miss time *includes* the initial lookup. With total miss time = 4 + 100 = 104:

```
 0.95 x 4 + 0.05 x 104 = 3.8 + 5.2 = 9
```

Same result. Mixing the conventions (using 100 as the total) gives 8.8, which is wrong. Always check whether a penalty includes the hit time.

### Worked example 2: two levels

In this serial model, the miss penalty of L1 is the incremental time spent accessing L2 and any lower level. The table uses incremental lookup times, not end-to-end latencies that already include earlier lookups.

| Level | Hit time | Local miss rate |
|---|---|---|
| L1 | 4 cycles | 5% |
| L2 | 12 cycles | 20% |
| DRAM | 200 cycles | - |

```
 L2 AMAT = 12 + 0.20 x 200 = 52
 AMAT    = 4 + 0.05 x 52
         = 4 + 2.6 = 6.6 cycles
```

### Local vs global miss rate

- **Local miss rate** of a level = its misses / accesses *that reach it*. L2's 20% is local: of the 5% of accesses that reach L2, 20% miss.
- **Global miss rate** = its misses / *all* CPU accesses. L2 global = 0.05 × 0.20 = **1%**.

These products describe the same stream of demand accesses filtered through successive levels, ignoring additional prefetch, write-back, and coherence traffic. Use local rates in the nested formula. A quoted L2 miss rate of "20%" sounds terrible but, here, only 1 access in 100 goes to DRAM.

### Worked example 3: three levels

L1: 4 cycles, 10% miss. L2: 14 cycles, 40% local miss. L3: 50 cycles, 25% local miss. DRAM: 300 cycles.

```
 L3 = 50 + 0.25 x 300 = 125
 L2 = 14 + 0.40 x 125 = 64
 L1 =  4 + 0.10 x 64  = 10.4 cycles
```

Global L3 miss rate = 0.10 × 0.40 × 0.25 = 1%.

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

With write-back and no buffering, a miss that evicts a dirty line must write it back first. If 40% of victims are dirty and a write-back costs as much as a fetch (100 cycles):

```
 penalty = 100 + 0.4 x 100 = 140
 AMAT    = 4 + 0.05 x 140 = 11 cycles
```

A **write-back buffer** can hold the dirty victim while its write-back overlaps the fetch or later execution. The benefit depends on scheduling, available bandwidth, and buffer space; it is not guaranteed to recover a particular AMAT.

## From AMAT to CPI

Using the iron law (CPU time = instructions × CPI × cycle time), memory stalls add directly to CPI for a simple in-order core that blocks on misses:

```
 CPI = base CPI
     + (mem refs / instr) x miss rate
       x miss penalty
```

Assume base CPI already includes cache-hit execution cost and that miss penalties cannot overlap. With base CPI 1.0, 0.4 data references per instruction, L1d miss rate 5%, and an L1 miss penalty of 52 cycles (the L2 AMAT above):

```
 stalls = 0.4 x 0.05 x 52 = 1.04
 CPI    = 1.0 + 1.04 = 2.04
```

Half of all cycles are spent waiting for memory. Instruction fetches add their own term if the L1i misses.

## Trade-offs and pitfalls

- **AMAT is a model for blocking caches.** Out-of-order cores keep running independent instructions during a miss and can have many misses outstanding at once (**memory-level parallelism**). Ten overlapped 100-cycle misses do not cost 1,000 cycles. AMAT alone cannot reliably rank such designs or predict total stall time: dependency chains, overlap, bandwidth, and queueing can change the result.
- **Average hides the tail.** A loop with 99% hits can still be dominated by the 1% if those are DRAM misses.
- **Evaluate hit time and miss rate together.** In this model L1 lookup time is paid on every access; lower-level costs are weighted by how often accesses reach them. Which change matters most depends on the workload and trade-off.
- **Write-allocate can double traffic** for streaming writes; use streaming stores or library routines that do.

## Key takeaways
- Write-through propagates stores, possibly through a merging buffer; write-back tracks dirty data and propagates it when required, including eviction or coherence events.
- Write-allocate allocates a line on a store miss. A partial-line update often needs old bytes and exclusive permission; a full-line streaming path may avoid the old-data read.
- AMAT = hit time + miss rate × miss penalty, applied recursively from the bottom up with local miss rates.
- Global miss rate = product of local miss rates down to that level.
- For non-overlapping blocking misses, stall CPI = references per instruction × miss rate × extra penalty; add it to a base CPI that already includes hits.

## Further reading
- [CMU: Cache memories](https://www.cs.cmu.edu/afs/cs/academic/class/15213-m19/www/lectures/12-cache-memories.pdf)
- [Intel: Memory cache control](https://cdrdv2-public.intel.com/874249/253668-090-sdm-vol-3a.pdf)
- [Average memory access time — Wikipedia](https://en.wikipedia.org/wiki/Average_memory_access_time)
- [Cache (computing): writing policies — Wikipedia](https://en.wikipedia.org/wiki/Cache_(computing))
- [Cache inclusion policy — Wikipedia](https://en.wikipedia.org/wiki/Cache_inclusion_policy)
- [Write buffer — Wikipedia](https://en.wikipedia.org/wiki/Write_buffer)
- [Memory part 2: CPU caches, Ulrich Drepper (LWN)](https://lwn.net/Articles/252125/)
