---
id: cache-arch-friendly-code
title: Writing cache-friendly code
level: intermediate
minutes: 14
summary: Loop order and row-major layout, counting misses per iteration, loop blocking (tiling) for matrix multiply, power-of-two stride traps, and structure-of-arrays versus array-of-structs.
---

The previous lessons explained how caches work. This one is about using that knowledge. The rules boil down to two:

1. **Use every byte of every line you fetch** (spatial locality).
2. **Reuse data while it is still in the cache** (temporal locality).

Most cache-friendly techniques are one of these two ideas applied to a loop or a data structure. The examples are in C, because C makes memory layout explicit; the same ideas apply to NumPy, Java arrays, Rust and Go.

## Row-major layout and loop order

Built-in rectangular arrays in C/C++, Rust and Go have contiguous rows. Nested pointers, vectors or slices need not form one contiguous matrix. NumPy's default dense allocation is **row-major** (`order='C'`), but views can have other strides. Conventional dense arrays in Fortran, MATLAB, Julia and R use **column-major** order.

```
 double a[3][4];  row-major in memory:
 a00 a01 a02 a03 a10 a11 a12 a13 a20 ...
 |--- row 0 ---| |--- row 1 ---|
```

For an N-column C array of 8-byte doubles, the byte address of `a[i][j]` is `base + (i*N + j) * 8`. Moving along `j` steps 8 bytes; moving along `i` steps a whole row.

```c
// contiguous inner loop: along a row
for (int i = 0; i < N; i++)
    for (int j = 0; j < N; j++)
        sum += a[i][j];

// strided inner loop: jumps a row
for (int j = 0; j < N; j++)
    for (int i = 0; i < N; i++)
        sum += a[i][j];
```

Reordering a floating-point sum can change its rounding and final value. Layout optimisation must preserve the accuracy and dependency requirements of the application.

For a **model** with N = 1024, 8-byte doubles, aligned 64-byte lines, an initially empty 32 KiB fully associative LRU cache, no prefetching or other accesses, the row walk incurs **131,072** misses. The column walk revisits each line only after 1,024 distinct lines (64 KiB), beyond this cache's capacity: **1,048,576** misses. These are simulated cache misses, not a promised 8× run-time difference. Representative hardware slowdown figures are absent because no matching workload/processor measurements have been verified.

> [!tip] In NumPy
> `np.zeros((n, n))` defaults to C order. Its row slices are contiguous and its column slices are strided. Reduction performance also depends on NumPy's implementation and shape; `sum(axis=1)` is not universally fastest. `np.asfortranarray` supplies F-contiguous storage, copying when necessary. For a 2D array, `a.T` exchanges shape/strides in a view; it does not physically rearrange the elements.



## Counting misses per iteration

Use the following simplified steady-state model: 64-byte lines, aligned 8-byte doubles, demand allocation on reads/writes, no prefetching or conflict/interference misses, and no row/column retained between sweeps. A current line survives long enough to use its adjacent elements. Ignore first-touch overhead for a fixed element, which can be kept in a register. Under those assumptions:

| Access pattern | Misses / iteration |
|---|---|
| Fixed (same element) | 0 |
| Stride 1 (8-byte elements) | 1/8 = 0.125 |
| Stride of a row | 1 |

### Matrix multiply: loop order matters

The loops below compute `C += A × B`; initialise C to zero to obtain `C = A × B`. Assume disjoint arrays and valid dimensions. The six loop orders perform n³ scalar product-and-accumulate updates, but their locality differs. Floating-point transformations, fused operations and reassociation can affect rounding.

```c
// ijk: inner loop over k
for (i = 0; i < n; i++)
  for (j = 0; j < n; j++) {
    double s = C[i][j];
    for (k = 0; k < n; k++)
      s += A[i][k] * B[k][j];
    C[i][j] = s;
  }
```

Inner loop over `k`: `A[i][k]` is stride 1 (0.125), `B[k][j]` walks down a column (1), `C[i][j]` is fixed (0). Total **1.125** misses per iteration.

```c
// ikj: inner loop over j
for (i = 0; i < n; i++)
  for (k = 0; k < n; k++) {
    double r = A[i][k];
    for (j = 0; j < n; j++)
      C[i][j] += r * B[k][j];
  }
```

Inner loop over `j`: `A[i][k]` fixed (0), `B[k][j]` stride 1 (0.125), `C[i][j]` stride 1 (0.125). Total **0.25**.

| Order | Inner loop | Misses / iter |
|---|---|---|
| ijk, jik | k | 1.125 |
| ikj, kij | j | 0.25 |
| jki, kji | i | 2.0 |

The `jki` order walks both `A` and `C` down columns: two misses per iteration, 8 times worse than `ikj`. Changing loop order can improve performance when memory access is the bottleneck. (In practice the row of `C` in `ikj` often stays cached across `k`, so it can do even better than 0.25.)

## Blocking (tiling)

The unblocked `ikj` order revisits B for each row of A. For n = 1024 and 8-byte doubles, B occupies 8 MiB; whether it survives between sweeps depends on the cache hierarchy. There is still reuse within each fetched line, and lower caches may retain data. The preceding simplified no-between-sweep-reuse model estimates n³/4 line fills, not universal DRAM traffic.

**Blocking** splits the matrices into small tiles that fit in cache together, and does all the work on those tiles before moving on.

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

(This assumes n is a multiple of T; real code handles the edges.)

**Choosing T**: a first capacity check is the useful bytes in three T × T tiles. For a 32 KiB target and 8-byte doubles:

```
 3 x T^2 x 8 bytes <= 32,768
 T^2 <= 1,365   ->  T <= 36
```

T = 32 gives 24 KiB of useful tile data, but that does **not** guarantee residency. Row fragments occupy whole lines, other data competes for space, and an 8 KiB row stride can cause set conflicts even when useful bytes fit. Packing tiles contiguously or padding rows can help. In an ideal model where the three tiles remain resident, many input values are reused T times; actual traffic and speed depend on the implementation. Optimised matrix libraries combine blocking with techniques such as packing, register reuse and vectorisation.

## The power-of-two stride trap

Under simple modulo indexing, certain strides repeatedly select the same set. A model 32 KiB, 8-way cache with 64-byte lines has 64 sets and uses address bits 6–11 for its set index. If you step by exactly 4,096 bytes (or any multiple), bits 6–11 never change: every access lands in one set, and only 8 lines fit.

Take a 256 × 1024 array of doubles: each row is 8,192 bytes. Walk it column by column. Each column touches 256 lines, only 16 KiB, which should fit easily in 32 KiB.

```
 row stride 8,192 B (2^13)
 set bits 6..11 never change
 -> all 256 lines compete for 8 ways
 -> every access misses (100%)

 pad each row by 64 B (stride 8,256)
 -> rows spread over all 64 sets
 -> one miss per line: 12.5%
```

For an aligned array, initially empty cache, LRU replacement, demand allocation, no prefetching and no other accesses, simulating this cache gives 16,384 misses out of 16,384 accesses for the first 64 columns without padding, and 2,048 (12.5%, the same as walking by rows) with one line of padding per row. This is why FFT and image-processing libraries often pad their arrays to sizes that are *not* powers of two.

## Array of structs vs struct of arrays

How you group fields decides how many useful bytes each line brings in.

```c
// AoS: assume 4-byte floats, sizeof = 32
struct Particle {
    float x, y, z;
    float vx, vy, vz;
    float mass, charge;
};
struct Particle p[N];

// Struct of arrays (SoA)
struct Particles {
    float x[N], y[N], z[N];
    float vx[N], vy[N], vz[N];
    float mass[N], charge[N];
};
```

Assume 4-byte floats, a 32-byte Particle, aligned cold 64-byte lines, and each needed line fetched once. Consider a pass that only does `x += vx * dt`. The following counts cover data brought into the cache, excluding later dirty write-backs and extra hardware traffic:

- **AoS**: each particle's 32 bytes come in together, but only 8 (x and vx) are used. 75% of every line is wasted. For N = 1,000,000, the loop drags 32 MB through the cache.
- **SoA**: `x[]` and `vx[]` are dense arrays, so every byte fetched is used: 8 MB read. Contiguous values can also support vectorisation; for example, a 256-bit AVX vector holds eight 32-bit floats when that instruction set is available.

AoS can be useful when accessing most fields of one record together; SoA can still win for some vectorised whole-record workloads. Columnar storage, including the Parquet file format, applies the related idea of grouping values by column, but a file format is not itself an in-memory C SoA structure.

A middle path is **hot/cold splitting**: keep the frequently used fields in a compact struct, and move rarely used ones (names, debug info) behind a pointer or into a parallel array.

## Other habits that help

- **Consider contiguous numeric storage.** C++ `std::vector` (apart from specialised representations such as `vector<bool>`), Rust `Vec`, Java primitive arrays and contiguous NumPy arrays keep element storage together. NumPy views need not be contiguous. Reference containers such as CPython lists and Java `ArrayList<Integer>` add indirection; elements can share objects.
- **Inspect struct alignment and padding.** On an ABI with 8-byte doubles and 8-byte double alignment, a `char` followed by a `double` can require 7 padding bytes. Reordering can help, but may merely move padding to the end; compare `sizeof` and offsets rather than assuming sorting by size shrinks every record.
- **Fuse loops** that walk the same arrays so data is reused while hot, instead of streaming the arrays twice.
- **Shrink the data.** `float` instead of `double`, `int32` indices instead of pointers, bitsets instead of `bool` arrays.
- **Measure.** `perf stat -e cache-misses,L1-dcache-load-misses` on Linux, or Instruments on macOS, tells you whether a change actually reduced misses.

## Pitfalls

- **Optimising cold code.** Restructuring data only matters in loops that dominate run time; profile first.
- **Blocking for the wrong level or size.** A tile that fits L1 on one machine may not on another; libraries tune or detect sizes.
- **Trusting the compiler to fix loop order.** Compilers can interchange simple loops, but aliasing (two pointers that might overlap) often stops them.

## Key takeaways
- Contiguous traversal usually follows the last index for C-order storage and the first index for F-order storage; inspect actual strides and preserve program semantics.
- Under the stated simplified model, fixed/stride-1/row-stride accesses contribute approximately 0/0.125/1 misses per iteration. These are model results, not hardware promises.
- Blocking keeps a working set of tiles in cache; choose T so about 3 T² elements fit (T = 32 for doubles in 32 KiB).
- Strides that alias cache sets can cause conflict misses; suitable padding or packing may distribute accesses more evenly.
- Use SoA when passes touch a few fields of many elements, AoS when you use whole records.

## Further reading
- [CMU: Cache memories and matrix locality](https://www.cs.cmu.edu/afs/cs/academic/class/15213-m19/www/lectures/12-cache-memories.pdf)
- [Memory part 5: What programmers can do, Ulrich Drepper (LWN)](https://lwn.net/Articles/255364/)
- [Row- and column-major order — Wikipedia](https://en.wikipedia.org/wiki/Row-_and_column-major_order)
- [Loop nest optimization — Wikipedia](https://en.wikipedia.org/wiki/Loop_nest_optimization)
- [AoS and SoA — Wikipedia](https://en.wikipedia.org/wiki/AoS_and_SoA)
- [The N-dimensional array: memory layout — NumPy docs](https://numpy.org/doc/stable/reference/arrays.ndarray.html)
- [Computer Systems: A Programmer's Perspective (CS:APP)](https://csapp.cs.cmu.edu/)
