---
id: cache-short-hierarchy-locality
title: Why a memory hierarchy works
level: basic
minutes: 5
sourceLesson: cache-arch-locality
summary: Small nearby memories trade capacity for access cost.
---

Many high-performance CPU cores overlap several instructions. A dependent load missing all caches can stall work while DRAM responds; independent requests may overlap. Actual latency depends on the chip, workload and memory configuration.

Computers use a hierarchy to balance capacity, cost and latency: small memories close to execution units backed by larger levels. **Locality**, reuse of the same or nearby data, makes this arrangement effective.

## Why small memories can be fast

Three design costs motivate the hierarchy:

- Distance. Signals take time to cross a chip. A small memory sitting right next to the execution units can be read in a few cycles; a large one is physically further away and has longer wires.
- Technology. Many CPU caches are built from **SRAM**: each bit is a little latch of about six transistors. It is fast and needs no refresh, but it is big and expensive per bit. Main memory is **DRAM**: one transistor and one capacitor per bit. It is dense and cheap but slow, and it leaks (it must be refreshed, see the DRAM lesson).
- Search cost. Finding an item in a bigger structure takes more decoding and comparing, so even the same technology gets slower as it grows.

## The hierarchy in numbers

A common general-purpose hierarchy is shown below. Exact capacities and latencies require a named processor and measurement conditions; not every machine has every level. Register operands are not zero-time physical accesses, even when they add no separate cache-load instruction.

| Level | Role |
|---|---|
| Registers | Small operand storage near execution units |
| L1 | Small, low-latency instruction/data caches |
| L2 | More capacity with a different latency trade-off |
| L3 / last-level cache | Often shared across cores |
| DRAM | Main volatile storage |
| SSD | Persistent storage reached through I/O |

> Generic latency, cache-hit-rate and size ranges are omitted because no representative processor/workload measurements were verified for the earlier figures. Use specifications and measurements for the target machine.

```
       faster, smaller, dearer per byte
              ^
   [registers]
   [   L1   ]
   [    L2    ]
   [     L3     ]
   [     DRAM       ]
   [      SSD         ]
              v
       slower, bigger, cheaper per byte
```

> [!note] Where the OS fits in
> The operating system can cache file contents in DRAM (the page cache). Virtual memory and TLBs support address translation for memory accesses. Those are covered in the Operating Systems subject; here we focus on the CPU caches and DRAM.

## Locality: why a small cache works

Imagine a program that used every byte of its memory equally and at random. Assume independent uniformly distributed byte accesses, a full cache, equal-sized cache lines and no overhead counted as data. The chance of a hit then follows the fraction of addressable data held:

```formula
h_rand ≈ C_cache / C_mem
h_rand ≈ 32 KiB / (16 GiB)
h_rand ≈ 2^15 B / 2^34 B
h_rand ≈ 1 / 524,288 ≈ 0.0002 %
where
h_rand: the hit rate under purely random, uniform access: the fraction of accesses that find their data in the cache
C_cache: the cache's capacity, here 32 KiB
C_mem: the capacity of the memory behind it, here 16 GiB of DRAM
KiB: kibibyte, 1,024 bytes (2^10 B)
GiB: gibibyte, 1,073,741,824 bytes (2^30 B)
B: byte, 8 bits
2^15: 15 copies of 2 multiplied together, 32,768; 32 KiB is 32 × 1,024 = 32,768 bytes
2^34: 34 copies of 2 multiplied together; 16 GiB is 16 × 2^30 bytes
≈: approximately equal to
%: per cent, parts per hundred
In words: if every byte were equally likely, a cache holding one 524,288th of memory would hit only about two times in a million accesses.
```

This independent uniform-access model is a poor-locality case that many real programs do not resemble. Adversarial conflict patterns can have even fewer hits; it is not a universal worst-case bound. Programs with useful locality can do much better. Two common forms of locality explain why.

## Temporal locality

If you used something recently, you will probably use it again soon. Loop counters, the top of the stack, a hot function's instructions, the root of a B-tree, an accumulating total: all are touched over and over.

A cache exploits temporal locality by keeping recently used data and evicting data that has not been used for a while.

## Key takeaways
- Small nearby memories trade capacity for access cost.
- Temporal locality is reuse soon; uniform random accesses lose that advantage.

## Further reading
- [CMU: Memory hierarchy](https://www.cs.cmu.edu/afs/cs/academic/class/15213-m19/www/lectures/11-memory-hierarchy.pdf)
- [Intel Memory Latency Checker](https://www.intel.com/content/www/us/en/developer/articles/tool/intelr-memory-latency-checker.html)
- [Memory hierarchy — Wikipedia](https://en.wikipedia.org/wiki/Memory_hierarchy)
- [Locality of reference — Wikipedia](https://en.wikipedia.org/wiki/Locality_of_reference)
- [What every programmer should know about memory, Ulrich Drepper (LWN)](https://lwn.net/Articles/250967/)
- [Gallery of processor cache effects, Igor Ostrovsky](https://igoro.com/archive/gallery-of-processor-cache-effects/)
- [Latency numbers every programmer should know (gist)](https://gist.github.com/jboner/2841832)
