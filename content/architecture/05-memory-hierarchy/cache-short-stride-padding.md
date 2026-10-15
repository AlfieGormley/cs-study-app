---
id: cache-short-stride-padding
title: Break cache-set stride conflicts
level: intermediate
minutes: 3
sourceLesson: cache-arch-friendly-code
summary: A stride equal to the set count times the line size retains the same modulo index.
---

This unit builds on the earlier cache lessons and focuses on break cache-set stride conflicts. Keep each example’s stated hardware geometry and model assumptions when applying its result.

## The power-of-two stride trap

Under simple modulo indexing, certain strides repeatedly select the same set. Take a model 32 KiB, 8-way cache with 64-byte lines. Its number of sets, and the set an address falls in, are:

```formula
N_sets = S_cache / (B_line W)
N_sets = 32,768 B / (64 B × 8) = 64
I_set = ⌊A / B_line⌋ mod N_sets
where
N_sets: the number of cache sets
S_cache: the cache capacity, 32 KiB = 32,768 bytes
B_line: the line size, 64 bytes
W: the associativity: 8 ways (lines per set)
I_set: the set index, the set an address must go in
A: the byte address being accessed
⌊ ⌋: floor: round down to a whole number, so ⌊A / B_line⌋ is the line number
mod: the remainder after dividing; x mod 64 is between 0 and 63
B: byte, 8 bits
In words: the line number, wrapped round the 64 sets, picks the set; in binary that is address bits 6 to 11.
```

Six bits can count from 0 to 63, so bits 0–5 pick the byte within a 64-byte line and the next six bits, 6–11, pick one of the 64 sets. If you step by exactly 4,096 bytes (64 sets × 64 bytes), or any multiple of it, bits 6–11 never change: every access lands in one set, and only 8 lines fit.

Take a 256 × 1024 array of doubles: each row is 8,192 bytes. Walk it column by column. Each column touches 256 lines, only 16 KiB, which should fit easily in 32 KiB.

```
 row stride 8,192 B (2 x 4,096)
 set bits 6..11 never change
 -> all 256 lines compete for 8 ways
 -> every access misses (100%)

 pad each row by 64 B (stride 8,256)
 -> rows spread over all 64 sets
 -> one miss per line: 12.5%
```

For an aligned array, initially empty cache, LRU replacement, demand allocation, no prefetching and no other accesses, simulating this cache gives 16,384 misses out of 16,384 accesses for the first 64 columns without padding, and 2,048 (12.5%, the same as walking by rows) with one line of padding per row. This motivates padding or packing in FFT and image-processing implementations when their access patterns suffer such measured conflicts.

## Key takeaways
- A stride equal to the set count times the line size retains the same modulo index.
- One line of row padding distributes this example across sets and changes its simulated misses.

## Further reading
- [CMU: Cache memories and matrix locality](https://www.cs.cmu.edu/afs/cs/academic/class/15213-m19/www/lectures/12-cache-memories.pdf)
- [Memory part 5: What programmers can do, Ulrich Drepper (LWN)](https://lwn.net/Articles/255364/)
- [Row- and column-major order — Wikipedia](https://en.wikipedia.org/wiki/Row-_and_column-major_order)
- [Loop nest optimization — Wikipedia](https://en.wikipedia.org/wiki/Loop_nest_optimization)
- [AoS and SoA — Wikipedia](https://en.wikipedia.org/wiki/AoS_and_SoA)
- [The N-dimensional array: memory layout — NumPy docs](https://numpy.org/doc/stable/reference/arrays.ndarray.html)
- [Computer Systems: A Programmer's Perspective (CS:APP)](https://csapp.cs.cmu.edu/)
