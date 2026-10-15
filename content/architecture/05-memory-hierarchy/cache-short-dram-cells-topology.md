---
id: cache-short-dram-cells-topology
title: From DRAM cells to banks and ranks
level: advanced
minutes: 4
sourceLesson: cache-arch-dram
summary: Sense amplifiers restore disturbed charge and refresh maintains retention.
---

Earlier examples used assumed DRAM latencies to explain cache arithmetic. Below the last-level cache is a memory system with controllers, channels, ranks, banks and rows. Access latency depends on its state, traffic and placement. Streaming throughput benefits from overlapping requests, including useful prefetches; it is not guaranteed to reach peak bandwidth.

The numerical examples below are explicit models. Representative end-to-end latency and speedup figures are absent where the necessary processor, memory configuration and benchmark have not been reliably verified.

## The DRAM cell and why it is slow

A conventional DRAM cell uses **one transistor and one capacitor**. Information is represented by charge state; the mapping of charged/discharged to logical 1/0 can depend on cell organisation. That makes DRAM dense and cheap, but it has three consequences:

- Reads are destructive. Activation shares the cell's small charge with a bit line. A **sense amplifier** resolves the voltage difference and restores the cell while the row is active. This disturbs the stored charge; it is not simply a complete drain followed by restoration during precharge.
- Cells leak. Charge drains away in milliseconds, so every row must be refreshed (read and rewritten) periodically, whether or not anyone uses it.
- Access is row-at-a-time. The chip cannot read one bit cheaply. It opens a whole row (thousands of bits) into the sense amplifiers, called the **DRAM row buffer**, and then reads columns from it.

## Inside a DIMM: channels, ranks, banks, rows

The following is an illustrative DDR4-style topology, excluding ECC bits; actual widths, ranks, bank counts and address mapping vary.

```
 memory controller (on the CPU)
   |-- channel 0 (64-bit bus)
   |     |-- rank 0: 8 chips side by side
   |     |     |-- bank 0 .. bank 15
   |     |     |     rows x columns
   |     |     |     + 1 row buffer
   |     |-- rank 1 ...
   |-- channel 1 ...
```

- A **memory channel** is an independent bus with its own controller logic. More channels means more bandwidth in parallel.
- A **DRAM rank** groups DRAM devices operated together. In the illustrated 64-data-bit DDR4 channel, eight ×8 (8-bit-wide) devices supply the data width; ECC may add bits. DDR5 DIMMs divide their data interface into sub-channels.
- Each chip has several **DRAM banks**, with counts depending on device width and generation; DDR5 configurations can have up to 32. Each bank has its own DRAM row buffer, so different banks can work on different rows at the same time.
- A **DRAM row** (sometimes called a page) is distinct from an operating-system page. Its aggregate byte size depends on device geometry and rank width; no universal row size is assumed here.

The memory controller maps, and may hash, physical address bits to choose channel, rank, bank, row and column. Controllers can interleave consecutive cache lines across channels and banks; the exact mapping determines whether a stream uses those resources in parallel.

## Key takeaways
- Sense amplifiers restore disturbed charge and refresh maintains retention.
- Channels, ranks, banks and rows are different levels of organisation.

## Further reading
- [Micron: DDR5 features and refresh](https://www.micron.com/products/memory/dram-components/ddr5-sdram)
- [Intel: Data-dependent prefetcher](https://www.intel.com/content/www/us/en/developer/articles/technical/software-security-guidance/technical-documentation/data-dependent-prefetcher.html?source=study)
- [GCC: Prefetch builtin semantics](https://gcc.gnu.org/onlinedocs/gcc/Other-Builtins.html)
- [Dynamic random-access memory — Wikipedia](https://en.wikipedia.org/wiki/Dynamic_random-access_memory)
- [Memory timings — Wikipedia](https://en.wikipedia.org/wiki/Memory_timings)
- [DDR5 SDRAM — Wikipedia](https://en.wikipedia.org/wiki/DDR5_SDRAM)
- [Memory part 1: RAM, Ulrich Drepper (LWN)](https://lwn.net/Articles/250967/)
- [Memory part 4: NUMA support, Ulrich Drepper (LWN)](https://lwn.net/Articles/254445/)
- [NUMA memory policy — Linux kernel docs](https://docs.kernel.org/admin-guide/mm/numa_memory_policy.html)
- [numactl(8) — Linux manual page](https://man7.org/linux/man-pages/man8/numactl.8.html)
- [Cache prefetching — Wikipedia](https://en.wikipedia.org/wiki/Cache_prefetching)
- [Row hammer — Wikipedia](https://en.wikipedia.org/wiki/Row_hammer)
