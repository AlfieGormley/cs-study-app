---
id: cache-short-matrix-tiling
title: Keep matrix tiles together
level: intermediate
minutes: 5
sourceLesson: cache-arch-friendly-code
summary: Blocking exposes reuse by revisiting small tiles before moving on.
---

This unit builds on the earlier cache lessons and focuses on keep matrix tiles together. Keep each example’s stated hardware geometry and model assumptions when applying its result.

## Loop blocking (tiling)

The unblocked `ikj` order revisits input matrix B for each row of input matrix A; C is the output accumulator. In this unit, n denotes the common square matrix edge. For 1024 × 1024 matrices of 8-byte doubles, B occupies 8 MiB; whether it survives between sweeps depends on the cache hierarchy. There is still reuse within each fetched line, and lower caches may retain data. The preceding simplified no-between-sweep-reuse model multiplies the work by the misses per iteration:

```formula
F = n^3 m_iter
F = 1024^3 × 0.25 = 268,435,456
where
F: the number of cache line fills (misses) for the whole multiply
n: the matrix size (n × n); here 1024
n^3: n × n × n, the number of inner-loop iterations
m_iter: misses per inner-loop iteration; 0.25 for ikj
In words: about a quarter of a line fill for every multiply-add, which is roughly 268 million fills (about 16 GiB of line traffic at 64 bytes each) for a 1024 × 1024 multiply.
```

That is a model of line fills, not universal DRAM traffic.

**Loop blocking** splits the matrices into small tiles that fit in cache together, and does all the work on those tiles before moving on. In the drawing, a and b are input tiles, c is the accumulating output tile, and T is the tile edge in elements.

```
 A            B            C
 +--+--+--+   +--+--+--+   +--+--+--+
 |a |  |  |   |b |  |  |   |c |  |  |
 +--+--+--+ x +--+--+--+ = +--+--+--+
 |  |  |  |   |  |  |  |   |  |  |  |
 +--+--+--+   +--+--+--+   +--+--+--+
 c += a x b for one T x T tile at a time
```

```c
#define T 32  /* tile edge */
// Tile origins choose a subproblem.
// Inner loops update C from A and B tiles.
for (ii = 0; ii < n; ii += T)
 for (kk = 0; kk < n; kk += T)
  for (jj = 0; jj < n; jj += T)
   for (i = ii; i < ii + T; i++)
    for (k = kk; k < kk + T; k++) {
     double r = A[i][k];
     for (j = jj; j < jj + T; j++)
      C[i][j] += r * B[k][j];
    }
```

Here n is the matrix edge in elements; i, j and k are element indices, ii, jj and kk are tile origins, and T is the tile edge. This fragment assumes disjoint allocated arrays, valid dimensions and n divisible by T; a complete implementation also handles allocation failures and edge tiles.

Choosing the tile edge: a first capacity check is the useful bytes in three equal square tiles (one each from A, B and C), which should not exceed the cache you are targeting (with additional headroom needed in practice). For a 32 KiB target and 8-byte doubles:

```formula
3T^2 s ≤ S_cache
3 × T^2 × 8 B ≤ 32,768 B
T^2 ≤ 1,365
T ≤ 36
where
T: the tile edge, in elements; each tile is T × T
T^2: T × T, the number of elements in one tile
3: the number of tiles in use at once, one from each matrix
s: the size of one double, 8 bytes
S_cache: the target cache's capacity; 32 KiB = 32,768 bytes
≤: less than or equal to
B: byte, 8 bits
In words: three tiles of T × T doubles must fit in 32 KiB, which allows a tile edge of up to 36 elements; 32 is the nearest power of two below that.
```

(1,365 is 32,768 / 24 rounded down; the square root of 1,365 is about 36.9, and T must be a whole number.)

A tile edge of 32 gives 24 KiB of useful tile data, but that does not guarantee residency. Row fragments occupy whole lines, other data competes for space, and an 8 KiB row stride can cause set conflicts even when useful bytes fit. Packing tiles contiguously or padding rows can help. In an ideal model where the three tiles remain resident, many input values are reused T times; actual traffic and speed depend on the implementation. Optimised matrix libraries combine blocking with techniques such as packing, register reuse and vectorisation.

For a separate ideal traffic model, assume packed aligned tiles, sufficient associativity, no interference and no retained data between tile steps. With 32-element tile edges in a 1,024-element matrix, there are 32 tile positions along each of three dimensions. Each step loads three cold tiles once and performs every update in their cubic subproblem. This deliberately pessimistic reset-between-steps model is separate from actual code that can retain data across tile steps. The focused question works through its line counts.

## Key takeaways
- Blocking exposes reuse by revisiting small tiles before moving on.
- Useful-byte capacity is a first check; line coverage, set conflicts and competing data still matter.

## Further reading
- [CMU: Cache memories and matrix locality](https://www.cs.cmu.edu/afs/cs/academic/class/15213-m19/www/lectures/12-cache-memories.pdf)
- [Memory part 5: What programmers can do, Ulrich Drepper (LWN)](https://lwn.net/Articles/255364/)
- [Row- and column-major order — Wikipedia](https://en.wikipedia.org/wiki/Row-_and_column-major_order)
- [Loop nest optimization — Wikipedia](https://en.wikipedia.org/wiki/Loop_nest_optimization)
- [AoS and SoA — Wikipedia](https://en.wikipedia.org/wiki/AoS_and_SoA)
- [The N-dimensional array: memory layout — NumPy docs](https://numpy.org/doc/stable/reference/arrays.ndarray.html)
- [Computer Systems: A Programmer's Perspective (CS:APP)](https://csapp.cs.cmu.edu/)
