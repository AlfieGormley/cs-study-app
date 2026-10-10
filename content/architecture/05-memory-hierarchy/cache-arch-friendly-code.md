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

Where exactly does an element live? In a row-major array, all of row 0 comes first, then all of row 1, and so on, so to reach `a[i][j]` you skip `i` whole rows and then `j` elements:

```formula
A_ij = A_base + (i × N + j) × s
A_ij = A_base + (2 × 4 + 1) × 8 B
A_ij = A_base + 72 B
where
A_ij: the byte address of element a[i][j]
A_base: the address of the array's first element, a[0][0]
i: the row number, counted from 0; here 2
j: the column number, counted from 0; here 1
N: the number of columns in each row; here 4, as in double a[3][4]
s: the size of one element in bytes; 8 for a double
B: byte, 8 bits
In words: skip i full rows of N elements, then j more elements, and multiply the element count by the element size to get a byte offset.
```

So `a[2][1]` in the 3 × 4 array above sits 72 bytes after `a[0][0]`. Moving along `j` (j + 1) steps 8 bytes; moving along `i` (i + 1) steps N × 8 bytes, a whole row. The formula assumes a genuine rectangular block of memory; an array of pointers to separately allocated rows does not follow it.

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

Take a **model**: a 1024 × 1024 array of 8-byte doubles, aligned 64-byte lines, an initially empty 32 KiB fully associative LRU cache, no prefetching or other accesses. The row walk misses once per line, because the other 7 doubles in each line are used straight after:

```formula
M_row = N^2 × s / B_line
M_row = 1024^2 × 8 B / 64 B
M_row = 131,072
M_col = N^2 = 1,048,576
where
M_row: cache misses for the row-by-row walk
M_col: cache misses for the column-by-column walk
N: the number of rows, which equals the number of columns here: 1024
N^2: N × N, the number of elements: 1,048,576
s: the size of one double, 8 bytes
B_line: the cache line size, 64 bytes
B: byte, 8 bits
In words: walking along rows costs one miss per 64-byte line, which holds 8 doubles; walking down columns misses on every single element.
```

The column walk misses every time because it comes back to a line only after touching 1,024 other lines (64 KiB), more than this 32 KiB cache holds, so the line has already been evicted. These are simulated cache misses, not a promised 8× run-time difference. Representative hardware slowdown figures are absent because no matching workload/processor measurements have been verified.

> [!tip] In NumPy
> `np.zeros((n, n))` defaults to C order. Its row slices are contiguous and its column slices are strided. Reduction performance also depends on NumPy's implementation and shape; `sum(axis=1)` is not universally fastest. `np.asfortranarray` supplies F-contiguous storage, copying when necessary. For a 2D array, `a.T` exchanges shape/strides in a view; it does not physically rearrange the elements.



## Counting misses per iteration

Use the following simplified steady-state model: 64-byte lines, aligned 8-byte doubles, demand allocation on reads/writes, no prefetching or conflict/interference misses, and no row/column retained between sweeps. A current line survives long enough to use its adjacent elements. Ignore first-touch overhead for a fixed element, which can be kept in a register.

A stride-1 walk (consecutive elements) misses only on the first element of each line, so its cost per iteration is one miss shared among all the elements a line holds:

```formula
m_iter = s / B_line
m_iter = 8 B / 64 B = 1/8 = 0.125
where
m_iter: average cache misses per loop iteration for one stride-1 array
s: the element size, 8 bytes for a double
B_line: the cache line size, 64 bytes
B: byte, 8 bits
In words: a 64-byte line holds 8 doubles, so a stride-1 walk misses on 1 iteration in 8.
```

A stride of a whole row (larger than a line) lands in a new line every time, so it costs 1 miss per iteration. Under those assumptions:

| Access pattern | Misses / iteration |
|---|---|
| Fixed (same element) | 0 |
| Stride 1 (8-byte elements) | 1/8 = 0.125 |
| Stride of a row | 1 |

### Matrix multiply: loop order matters

The loops below compute the matrix product of A and B and add it into C; initialise C to zero to obtain just the product. Assume disjoint n × n arrays of doubles, where n is the number of rows (and columns). Whichever order the three loops nest in, the work is the same:

```formula
U = n^3
U = 1024^3 ≈ 1.07 × 10^9
where
U: the number of scalar multiply-and-add updates, one per (i, j, k) combination
n: the size of each matrix: n rows and n columns; here 1024
n^3: n × n × n, because each of the three loops runs n times
≈: approximately equal to
In words: an n × n matrix multiply does n cubed multiply-adds whatever order the loops are in; only the memory access pattern changes.
```

The six loop orders all perform these updates, but their locality differs. Floating-point transformations, fused operations and reassociation can affect rounding.

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

Inner loop over `k`: `A[i][k]` is stride 1, `B[k][j]` walks down a column, `C[i][j]` is fixed. Add up each array's misses per iteration from the table:

```formula
m_iter = m_A + m_B + m_C
m_iter = 0.125 + 1 + 0 = 1.125
where
m_iter: total cache misses per inner-loop iteration
m_A: misses per iteration on A; stride 1, so 0.125
m_B: misses per iteration on B; down a column, so 1
m_C: misses per iteration on C; fixed element, so 0
In words: each iteration of the ijk inner loop costs about one and an eighth misses, almost all of them from walking down B's column.
```

```c
// ikj: inner loop over j
for (i = 0; i < n; i++)
  for (k = 0; k < n; k++) {
    double r = A[i][k];
    for (j = 0; j < n; j++)
      C[i][j] += r * B[k][j];
  }
```

Inner loop over `j`: `A[i][k]` is fixed (0 misses per iteration), `B[k][j]` is stride 1 (0.125) and `C[i][j]` is stride 1 (0.125). Total: 0 + 0.125 + 0.125 = **0.25** misses per iteration.

| Order | Inner loop | Misses / iter |
|---|---|---|
| ijk, jik | k | 1.125 |
| ikj, kij | j | 0.25 |
| jki, kji | i | 2.0 |

The `jki` order walks both `A` and `C` down columns: two misses per iteration, 8 times worse than `ikj`. Changing loop order can improve performance when memory access is the bottleneck. (In practice the row of `C` in `ikj` often stays cached across `k`, so it can do even better than 0.25.)

## Loop blocking (tiling)

The unblocked `ikj` order revisits B for each row of A. For 1024 × 1024 matrices of 8-byte doubles, B occupies 8 MiB; whether it survives between sweeps depends on the cache hierarchy. There is still reuse within each fetched line, and lower caches may retain data. The preceding simplified no-between-sweep-reuse model multiplies the work by the misses per iteration:

```formula
F = n^3 × m_iter
F = 1024^3 × 0.25 = 268,435,456
where
F: the number of cache line fills (misses) for the whole multiply
n: the matrix size (n × n); here 1024
n^3: n × n × n, the number of inner-loop iterations
m_iter: misses per inner-loop iteration; 0.25 for ikj
In words: about a quarter of a line fill for every multiply-add, which is roughly 268 million fills (about 16 GiB of line traffic at 64 bytes each) for a 1024 × 1024 multiply.
```

That is a model of line fills, not universal DRAM traffic.

**Loop blocking** splits the matrices into small tiles that fit in cache together, and does all the work on those tiles before moving on.

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

**Choosing T**: a first capacity check is the useful bytes in three T × T tiles (one each from A, B and C), which should not exceed the cache you are targeting. For a 32 KiB target and 8-byte doubles:

```formula
3 × T^2 × s ≤ S_cache
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

T = 32 gives 24 KiB of useful tile data, but that does **not** guarantee residency. Row fragments occupy whole lines, other data competes for space, and an 8 KiB row stride can cause set conflicts even when useful bytes fit. Packing tiles contiguously or padding rows can help. In an ideal model where the three tiles remain resident, many input values are reused T times; actual traffic and speed depend on the implementation. Optimised matrix libraries combine blocking with techniques such as packing, register reuse and vectorisation.

## The power-of-two stride trap

Under simple modulo indexing, certain strides repeatedly select the same set. Take a model 32 KiB, 8-way cache with 64-byte lines. Its number of sets, and the set an address falls in, are:

```formula
N_sets = S_cache / (B_line × W)
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

- **AoS**: each particle's 32 bytes come in together, but only 8 (x and vx) are used. 75% of every line is wasted. For 1,000,000 particles, the loop drags 1,000,000 × 32 bytes = 32 MB through the cache.
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
- **Loop blocking for the wrong level or size.** A tile that fits L1 on one machine may not on another; libraries tune or detect sizes.
- **Trusting the compiler to fix loop order.** Compilers can interchange simple loops, but aliasing (a pair of pointers that might overlap) often stops them.

## Key takeaways
- Contiguous traversal usually follows the last index for C-order storage and the first index for F-order storage; inspect actual strides and preserve program semantics.
- Under the stated simplified model, fixed/stride-1/row-stride accesses contribute approximately 0/0.125/1 misses per iteration. These are model results, not hardware promises.
- Loop blocking keeps a working set of tiles in cache; choose the tile edge so that three square tiles fit together (32 × 32 doubles per tile for a 32 KiB cache).
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
