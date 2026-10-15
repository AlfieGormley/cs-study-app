---
id: cache-short-stores-inclusion
title: Write traffic and inclusion policies
level: intermediate
minutes: 5
sourceLesson: cache-arch-write-amat
summary: Write-through and write-back decide when modified bytes travel downstream.
---

Reads are the easy half of caching: if the line is present, return it; if not, fetch it. Writes raise harder questions. When a store hits in L1, does memory get updated now or later? When a store misses, do we bother fetching the line at all? The answers change how much traffic flows between levels, and that changes performance.

Later short lessons combine these policies with the **average memory access time** (AMAT) model and then the cost in cycles per instruction.

## On a write hit: write-through or write-back

## Write-through

Every store updates the cached copy and must be propagated to the next level. A **write buffer** can defer or merge those updates, so the next level need not reflect a pending store immediately.

- A clean write-through line does not need a dirty eviction write-back; pending buffered writes still must complete correctly.
- Without write merging, one million issued stores send one million writes downstream. Merging can reduce that traffic.
- A full write buffer can stall further stores.

## Write-back

A store updates the cache line and marks it dirty (it sets the line's dirty bit). Modified data is propagated when required, for example on dirty eviction, explicit write-back, or a coherence request; eviction is not the only trigger.

- Repeated local writes can avoid repeated downstream data writes while the core retains ownership. They still consume execution/cache resources.
- In the simple allocate-on-miss model, replacing a dirty victim requires preserving its data and fetching the incoming line.
- A lower cache or DRAM may hold stale data, so coherent agents must obtain the current copy through the coherence mechanism. Non-coherent DMA requires the platform's cache-maintenance rules.

The following traffic example assumes no write merging, no intervening coherence requests, and one final eviction. The assignment trace writes one cached variable, `x`; arrows show downstream propagation:

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

The natural pairings are write-back + write-allocate (the usual choice) and write-through + no-write-allocate.

In a coherent fetch-on-write model, a store miss requests exclusive permission, often through a **read for ownership** (RFO) coherence transaction that also obtains the line. Data may come from another cache rather than DRAM. A full-line overwrite may permit an implementation to omit the old-data fetch.

> [!example] Modelled traffic for overwriting 64 MiB
> Assume aligned 64-byte lines initially absent from all caches, no useful old data, no write-fetch elimination, and eventual write-back of every dirty line. Ordinary fetch-on-write stores read 64 MiB and write 64 MiB: 128 MiB of DRAM data traffic.
> In an ideal full-line streaming-store path that avoids allocation/old-data reads, the corresponding data traffic is 64 MiB. Real non-temporal instructions and library thresholds are implementation-specific; this is a traffic model, not a guarantee for every `memset` call.

## Inclusion between levels

These properties apply to the particular pair or collection of cache levels being discussed:

- **Inclusive hierarchy**: presence in an included upper level implies presence in the lower level. The lower copy need not contain the newest bytes when an upper copy is dirty. Evicting the lower entry requires invalidating the included upper entries. Inclusion can help filter snoops, at the cost of duplicated capacity.
- **Exclusive hierarchy**: a line is resident in only one of the specified levels. Their nominal capacities can therefore add without duplication between those levels; other caches and metadata remain separate concerns.
- Neither inclusive nor exclusive (NINE): neither presence nor absence in one level guarantees the corresponding state in another. “Non-inclusive” alone does not necessarily rule out an exclusive design.

Specific processor-generation inclusion policies are not catalogued here because the necessary configuration-specific verification is unavailable in this lesson.

## Key takeaways
- Write-through and write-back decide when modified bytes travel downstream.
- Allocation and hierarchy inclusion are separate policy choices with different traffic and residency consequences.

## Further reading
- [CMU: Cache memories](https://www.cs.cmu.edu/afs/cs/academic/class/15213-m19/www/lectures/12-cache-memories.pdf)
- [Intel: Memory cache control](https://cdrdv2-public.intel.com/874249/253668-090-sdm-vol-3a.pdf)
- [Average memory access time — Wikipedia](https://en.wikipedia.org/wiki/Average_memory_access_time)
- [Cache (computing): writing policies — Wikipedia](https://en.wikipedia.org/wiki/Cache_(computing))
- [Cache inclusion policy — Wikipedia](https://en.wikipedia.org/wiki/Cache_inclusion_policy)
- [Write buffer — Wikipedia](https://en.wikipedia.org/wiki/Write_buffer)
- [Memory part 2: CPU caches, Ulrich Drepper (LWN)](https://lwn.net/Articles/252125/)
