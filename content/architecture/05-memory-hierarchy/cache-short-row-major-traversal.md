---
id: cache-short-row-major-traversal
title: Traverse the contiguous dimension
level: intermediate
minutes: 5
sourceLesson: cache-arch-friendly-code
summary: Rectangular C-order rows are contiguous; F-order columns are contiguous.
---

The previous lessons explained how caches work. This one is about using that knowledge. The rules boil down to two:

1. Use every byte of every line you fetch (spatial locality).
2. Reuse data while it is still in the cache (temporal locality).

Most cache-friendly techniques are one of these two ideas applied to a loop or a data structure. The examples are in C, because C makes memory layout explicit; the same ideas apply to NumPy, Java arrays, Rust and Go.

## Row-major layout and loop order

Built-in rectangular arrays in C/C++, Rust and the Go programming language have contiguous rows. Nested pointers, vectors or slices need not form one contiguous matrix. NumPy's default dense allocation is **row-major** (`order='C'`), but views can have other strides. Conventional dense arrays in Fortran, MATLAB, Julia and R use **column-major** order.

```
 double a[3][4];  row-major in memory:
 a00 a01 a02 a03 a10 a11 a12 a13 a20 ...
 |--- row 0 ---| |--- row 1 ---|
```

Where exactly does an element live? In a row-major array, all of row 0 comes first, then all of row 1, and so on, so to reach `a[i][j]` you skip `i` whole rows and then `j` elements:

```formula
A_ij = A_base + (iN + j)s
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

So `a[2][1]` in the 3 × 4 array above sits 72 bytes after `a[0][0]`. Incrementing `j` steps one 8-byte double; incrementing `i` steps one complete row. The formula assumes a genuine rectangular block of memory; an array of pointers to separately allocated rows does not follow it.

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

Take a model: a 1024 × 1024 array of 8-byte doubles, aligned 64-byte lines, an initially empty 32 KiB fully associative LRU cache, no prefetching or other accesses. The row walk misses once per line, because the other 7 doubles in each line are used straight after:

```formula
M_row = (N^2 s) / B_line
M_row = 1024^2 × 8 B / (64 B)
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

The column walk misses every time because it comes back to a line only after touching 1,023 intervening lines (a cycle of 1,024 lines, or 64 KiB), more than this 32 KiB cache holds, so the line has already been evicted. These are simulated cache misses, not a promised 8× run-time difference. Representative hardware slowdown figures are absent because no matching workload/processor measurements have been verified.

> [!tip] In NumPy
> `np.zeros((n, n))` defaults to C order. Its row slices are contiguous and its column slices are strided. Reduction performance also depends on NumPy's implementation and shape; `sum(axis=1)` is not universally fastest. `np.asfortranarray` supplies F-contiguous storage, copying when necessary. For a 2D array, `a.T` exchanges shape/strides in a view; it does not physically rearrange the elements.

## Key takeaways
- Rectangular C-order rows are contiguous; F-order columns are contiguous.
- Inspect actual strides and preserve floating-point accuracy when changing traversal order.

## Further reading
- [CMU: Cache memories and matrix locality](https://www.cs.cmu.edu/afs/cs/academic/class/15213-m19/www/lectures/12-cache-memories.pdf)
- [Memory part 5: What programmers can do, Ulrich Drepper (LWN)](https://lwn.net/Articles/255364/)
- [Row- and column-major order — Wikipedia](https://en.wikipedia.org/wiki/Row-_and_column-major_order)
- [Loop nest optimization — Wikipedia](https://en.wikipedia.org/wiki/Loop_nest_optimization)
- [AoS and SoA — Wikipedia](https://en.wikipedia.org/wiki/AoS_and_SoA)
- [The N-dimensional array: memory layout — NumPy docs](https://numpy.org/doc/stable/reference/arrays.ndarray.html)
- [Computer Systems: A Programmer's Perspective (CS:APP)](https://csapp.cs.cmu.edu/)
