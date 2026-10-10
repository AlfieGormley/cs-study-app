---
id: cache-arch-locality
title: Locality and the memory hierarchy
level: basic
minutes: 10
summary: The latency, capacity and cost trade-offs behind memory hierarchies, and how temporal and spatial locality help caches.
---

Many high-performance CPU cores overlap several instructions. A dependent load missing all caches can stall work while DRAM responds; independent requests may overlap. Actual latency depends on the chip, workload and memory configuration.

Computers use a **hierarchy** to balance capacity, cost and latency: small memories close to execution units backed by larger levels. **Locality**, reuse of the same or nearby data, makes this arrangement effective.

## Why small memories can be fast

Three design costs motivate the hierarchy:

- **Distance.** Signals take time to cross a chip. A small memory sitting right next to the execution units can be read in a few cycles; a large one is physically further away and has longer wires.
- **Technology.** Many CPU caches are built from **SRAM**: each bit is a little latch of about six transistors. It is fast and needs no refresh, but it is big and expensive per bit. Main memory is **DRAM**: one transistor and one capacitor per bit. It is dense and cheap but slow, and it leaks (it must be refreshed, see the DRAM lesson).
- **Search cost.** Finding an item in a bigger structure takes more decoding and comparing, so even the same technology gets slower as it grows.

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

Imagine a program that used every byte of its memory equally and at random. Then the chance that a given access finds its data in the cache is simply the fraction of memory the cache can hold:

```formula
h_rand ≈ C_cache / C_mem
h_rand ≈ 32 KiB / 16 GiB
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

This independent uniform-access model is a worst case that real programs rarely resemble. Programs with useful locality can do much better. Two common forms of locality explain why.

### Temporal locality

**If you used something recently, you will probably use it again soon.** Loop counters, the top of the stack, a hot function's instructions, the root of a B-tree, an accumulating total: all are touched over and over.

A cache exploits temporal locality by **keeping recently used data** and evicting data that has not been used for a while.

### Spatial locality

**If you used something, you will probably use its neighbours soon.** Instructions run one after another. Arrays are walked element by element. Fields of a struct are read together.

A cache exploits spatial locality by moving data in fixed-size blocks called **cache lines**, not single bytes. This module normally assumes **64-byte lines** and 4-byte ints; real line sizes vary, including 128-byte examples. A fill supplies other ints in the same line, not necessarily the next 15: that depends on the accessed int's position. Later accesses still have lookup costs.

How many values one line holds is the line size divided by the size of each value:

```formula
n_line = L / s
n_line = 64 B / 8 B = 8
n_line = 64 B / 4 B = 16
where
n_line: how many values of one type fit in one cache line
L: the cache line size, in bytes (B); 64 B here
s: the size of one value, in bytes; 8 B for a double (second line), 4 B for a 32-bit int (third line)
B: byte, 8 bits
In words: a 64-byte line holds 8 doubles or 16 ints, so one fetch brings in that many neighbours at once.
```

```
 one 64-byte line holds 8 doubles (8 B each)
 +----+----+----+----+----+----+----+----+
 | d0 | d1 | d2 | d3 | d4 | d5 | d6 | d7 |
 +----+----+----+----+----+----+----+----+
   ^ read d0: miss, whole line fetched
     d1..d7: hits
```

Summing an array shows how much this saves. Summing 1,000,000 4-byte ints walks 4 MB in order. Take a line-aligned array (it starts exactly on a line boundary) and a cold cache that starts empty, fetches only on demand, and suffers no interfering evictions. Every line then misses exactly once, on its first int:

```formula
N_lines = S_array / L
N_lines = 4,000,000 B / 64 B = 62,500
m = N_lines / N_loads
m = 62,500 / 1,000,000 = 0.0625
m = 6.25 %
where
N_lines: the number of cache lines the array covers, and so the number of misses
S_array: the array's size in bytes: 1,000,000 ints × 4 B
L: the cache line size, 64 bytes
N_loads: the number of scalar loads, one per int: 1,000,000
m: the miss rate, misses divided by accesses
B: byte, 8 bits
%: per cent, parts per hundred
In words: each 64-byte line holds 16 ints, so only one load in 16 misses: 6.25 %.
```

This is a model, not a measurement. An unaligned start can add a line. Prefetching and interference change demand miss counts.

## Hits, misses and the working set

Some vocabulary used throughout this module:

- **Cache hit** (hit): the data is in this level. **Cache miss** (miss): it is not, and the request goes to the next level down.
- **Hit rate** and **miss rate**: the fractions of accesses that hit and miss (formulas below).
- **Miss penalty**: the extra time a miss costs (the time to get the line from below).
- **Working set**: the data a program touches over a short window of time. Fitting in a level makes reuse possible, but set conflicts, other activity, coherence and replacement policy can still evict data. Exceeding capacity can increase misses.

Every access either hits or misses, so the two rates always add up to 1:

```formula
h = N_hits / N_acc
m = 1 − h
where
h: the hit rate, a fraction from 0 to 1 (often written as a percentage)
m: the miss rate, a fraction from 0 to 1
N_hits: the number of accesses that hit in this level
N_acc: the total number of accesses to this level
In words: the hit rate is the share of accesses that found their data here, and the miss rate is everything else.
```

For example, 950 hits out of 1,000 accesses is a hit rate of 0.95 (95 %) and a miss rate of 0.05 (5 %). These are rates for one level: an L2 miss rate here counts only the accesses that reached L2 (the AMAT lesson calls this the local miss rate, and also defines a global one).

The working set is why performance graphs often show **performance cliffs**. A carefully controlled repeated-access benchmark may show transitions near cache capacities. Streaming bandwidth, prefetching and access dependencies can make the curve quite different.

```
time per
access
  ^                          ______ DRAM
  |                  _______/
  |          _______/  L3
  |  _______/ L2
  |__/ L1
  +--------------------------> size
    32K    1M         32M
```

## Seeing locality in code

The same amount of work can have very different locality. Both functions below add up the same list of numbers; only the order differs.

```python
import random

N = 10_000_000
data = list(range(N))

def in_order():
    total = 0
    for i in range(N):
        total += data[i]
    return total

order = list(range(N))
random.shuffle(order)

def shuffled():
    total = 0
    for i in order:
        total += data[i]
    return total
```

In CPython, a list contains references to objects. Sequentially reading the reference array has spatial locality; shuffled indices scatter those accesses and can increase cache misses. Object allocation, shared objects, interpreter work, the extra array of indices and cache size affect the result. Run a controlled benchmark rather than assuming a fixed slowdown.

> A universal 5–10× slowdown and interpreter nanoseconds-per-iteration figure are omitted because no matching runtime, machine and benchmark were verified.

## Real-world consequences

- **Arrays can improve traversal locality compared with scattered linked lists**, even at the same big-O complexity. A dependent `next` pointer limits when the next demand address becomes known; whether it misses depends on placement, residency and prefetch capabilities.
- **B-trees can reduce serial node accesses compared with binary trees** for large indexes. A B-tree node is sized to hold many keys in a few cache lines (or one disk page), so each visited node can provide several nearby keys. A node may span several lines; cache misses depend on residency and search layout.
- **Hot loops should be small.** Instructions are cached too (in a separate L1 instruction cache). Huge unrolled or inlined code can overflow it.
- **Data size matters.** Using `int32` instead of `int64` fits twice as many integers per line; packing one-byte booleans into bits fits eight times as many flags, excluding layout overhead.

## Pitfalls

- **Assuming the big-O tells the whole story.** Two O(n) algorithms (time growing in proportion to n, the number of elements) can differ by 10× because one streams memory and the other jumps around.
- **Benchmarking with tiny inputs.** If the test data fits in L1, you are measuring the fast path. Production data that overflows into DRAM behaves differently.
- **Assuming 64-byte lines everywhere.** Line sizes vary by processor and cache level. Query the target (`sysctl hw.cachelinesize` on macOS, `getconf LEVEL1_DCACHE_LINESIZE` on Linux) rather than hard-coding it in portable code.

## Key takeaways
- Distance, storage technology and lookup cost motivate a hierarchy: registers, L1, L2, L3, DRAM, storage.
- Exact latency ratios depend on hardware, load and access pattern; measure them rather than assuming a universal table.
- Temporal locality (reuse soon) is exploited by keeping recent data; spatial locality (neighbours soon) by moving whole cache lines, 64 bytes in the main examples here.
- Working-set capacity matters, but conflicts, replacement, prefetching and interference also determine hit rates.
- Data layout and access order can matter as much as algorithmic complexity.

## Further reading
- [CMU: Memory hierarchy](https://www.cs.cmu.edu/afs/cs/academic/class/15213-m19/www/lectures/11-memory-hierarchy.pdf)
- [Intel Memory Latency Checker](https://www.intel.com/content/www/us/en/developer/articles/tool/intelr-memory-latency-checker.html)
- [Memory hierarchy — Wikipedia](https://en.wikipedia.org/wiki/Memory_hierarchy)
- [Locality of reference — Wikipedia](https://en.wikipedia.org/wiki/Locality_of_reference)
- [What every programmer should know about memory, Ulrich Drepper (LWN)](https://lwn.net/Articles/250967/)
- [Gallery of processor cache effects, Igor Ostrovsky](https://igoro.com/archive/gallery-of-processor-cache-effects/)
- [Latency numbers every programmer should know (gist)](https://gist.github.com/jboner/2841832)
