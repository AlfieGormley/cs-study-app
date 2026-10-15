---
id: cache-short-matrix-loop-order
title: Count misses for matrix loop orders
level: intermediate
minutes: 5
sourceLesson: cache-arch-friendly-code
summary: Fixed, contiguous and row-stride accesses have different costs under the stated simplified model.
---

This unit builds on the earlier cache lessons and focuses on count misses for matrix loop orders. Keep each example’s stated hardware geometry and model assumptions when applying its result.

## Counting misses per iteration

Use the following simplified steady-state model: 64-byte lines, aligned 8-byte doubles, demand allocation on reads/writes, no prefetching or conflict/interference misses, and no row/column retained between sweeps. A current line survives long enough to use its adjacent elements. Ignore first-touch overhead for a fixed element, which can be kept in a register.

A stride-1 walk (consecutive elements) misses only on the first element of each line, so its cost per iteration is one miss shared among all the elements a line holds:

```formula
m_iter = s / B_line
m_iter = 8 B / (64 B) = 1/8 = 0.125
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

## Matrix multiply: loop order matters

The loops below compute the matrix product of A and B and add it into C; initialise C to zero to obtain just the product. Assume disjoint square arrays of doubles; n is the number of rows and columns, and i, j and k are zero-based loop indices. Whichever order the three loops nest in, the work is the same:

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
// ijk: keep one output in a scalar.
// A walks a row; B walks a column.
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
// ikj: reuse one A value across a row.
// B and C advance through adjacent doubles.
for (i = 0; i < n; i++)
  for (k = 0; k < n; k++) {
    double r = A[i][k];
    for (j = 0; j < n; j++)
      C[i][j] += r * B[k][j];
  }
```

Inner loop over `j`: `A[i][k]` is fixed (0 misses per iteration), `B[k][j]` is stride 1 (0.125) and `C[i][j]` is stride 1 (0.125). Total: 0 + 0.125 + 0.125 = 0.25 misses per iteration.

| Order | Inner loop | Misses / iter |
|---|---|---|
| ijk, jik | k | 1.125 |
| ikj, kij | j | 0.25 |
| jki, kji | i | 2.0 |

The `jki` order walks both `A` and `C` down columns: two misses per iteration, 8 times worse than `ikj`. Changing loop order can improve performance when memory access is the bottleneck. (In practice the row of `C` in `ikj` often stays cached across `k`, so it can do even better than 0.25.)

## Key takeaways
- Fixed, contiguous and row-stride accesses have different costs under the stated simplified model.
- The six multiplication loop orders do the same scalar updates with different access patterns.

## Further reading
- [CMU: Cache memories and matrix locality](https://www.cs.cmu.edu/afs/cs/academic/class/15213-m19/www/lectures/12-cache-memories.pdf)
- [Memory part 5: What programmers can do, Ulrich Drepper (LWN)](https://lwn.net/Articles/255364/)
- [Row- and column-major order — Wikipedia](https://en.wikipedia.org/wiki/Row-_and_column-major_order)
- [Loop nest optimization — Wikipedia](https://en.wikipedia.org/wiki/Loop_nest_optimization)
- [AoS and SoA — Wikipedia](https://en.wikipedia.org/wiki/AoS_and_SoA)
- [The N-dimensional array: memory layout — NumPy docs](https://numpy.org/doc/stable/reference/arrays.ndarray.html)
- [Computer Systems: A Programmer's Perspective (CS:APP)](https://csapp.cs.cmu.edu/)
