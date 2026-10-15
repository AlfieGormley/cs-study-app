---
id: cache-short-spatial-lines
title: Spatial locality and cache-line traffic
level: basic
minutes: 3
sourceLesson: cache-arch-locality
summary: A line fill supplies adjacent bytes, with the useful count depending on alignment and element size.
---

This unit builds on the earlier cache lessons and focuses on spatial locality and cache-line traffic. Keep each example’s stated hardware geometry and model assumptions when applying its result.

## Spatial locality

If you used something, you will probably use its neighbours soon. Instructions run one after another. Arrays are walked element by element. Fields of a struct are read together.

A cache exploits spatial locality by moving data in fixed-size blocks called **cache lines**, not single bytes. This module normally assumes **64-byte lines** and 4-byte ints; real line sizes vary, including 128-byte examples. A fill supplies other ints in the same line, not necessarily the next 15: that depends on the accessed int's position. Later accesses still have lookup costs.

How many values one line holds is the line size divided by the size of each value:

```formula
n_line = L / s
n_line = 64 B / (8 B) = 8
n_line = 64 B / (4 B) = 16
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
N_lines = 4,000,000 B / (64 B) = 62,500
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

## Key takeaways
- A line fill supplies adjacent bytes, with the useful count depending on alignment and element size.
- Cold sequential miss counts require explicit allocation and interference assumptions.

## Further reading
- [CMU: Memory hierarchy](https://www.cs.cmu.edu/afs/cs/academic/class/15213-m19/www/lectures/11-memory-hierarchy.pdf)
- [Intel Memory Latency Checker](https://www.intel.com/content/www/us/en/developer/articles/tool/intelr-memory-latency-checker.html)
- [Memory hierarchy — Wikipedia](https://en.wikipedia.org/wiki/Memory_hierarchy)
- [Locality of reference — Wikipedia](https://en.wikipedia.org/wiki/Locality_of_reference)
- [What every programmer should know about memory, Ulrich Drepper (LWN)](https://lwn.net/Articles/250967/)
- [Gallery of processor cache effects, Igor Ostrovsky](https://igoro.com/archive/gallery-of-processor-cache-effects/)
- [Latency numbers every programmer should know (gist)](https://gist.github.com/jboner/2841832)
