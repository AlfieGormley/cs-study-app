---
id: lin-array-cache-row-layout
title: Cache locality and row-major grids
level: basic
minutes: 4
sourceLesson: lin-arrays
summary: Scan the contiguous dimension for sequential memory access.
---

The preceding unit derived an address from the array base, index and fixed slot size. Constant-time indexing is a data-structure model; memory locality explains why two scans that do the same number of operations can still differ in real elapsed time.

## Why contiguous memory is fast

Both indexed access and a single pointer load are constant-time operations in the usual RAM model. Their measured latencies can differ because that model abstracts away the memory hierarchy.

CPUs do not fetch single bytes from RAM. They transfer a whole **cache line** (its size depends on the processor; this lesson assumes 64 bytes) and keep it in a small, fast cache. A cache hit can be much faster than a main-memory access. The actual latencies depend on the hardware, contention and access pattern, so no universal nanosecond figures are quoted here.

When you scan an array, one aligned 64-byte cache line contains sixteen 4-byte integers. A hardware **prefetcher** can recognise a sequential pattern and fetch later lines ahead of demand; effectiveness depends on the processor, stride and workload. This is **spatial locality**, and it is why a simple loop over an array is one of the fastest things a computer can do.

A linked list (covered later in this module) scatters its nodes around the heap. Each step can be a cache miss. Scanning n elements is O(n) for both on paper; dependent pointer loads can make the list slower, but no speed ratio follows without measuring the workload.

### 2D arrays: row-major order

A rectangular C or C++ array such as `int grid[3][4]` is contiguous and row-major: row 0 first, then row 1. A newly created C-order NumPy array has this layout too; NumPy also supports other strides and orders. Java int[][] is an array of references to separate int[] rows, which may have different lengths. Fortran, MATLAB and R normally use column-major layout.

```
grid (3 x 4), row-major:

[r0c0 r0c1 r0c2 r0c3 r1c0 r1c1 ...]
```

To locate a row-and-column element, count complete earlier rows and then the earlier slots in its row:

```formula reference
address(r, c) = base + (r × cols + c) × size
where
address(r, c): the memory address of the element in row r, column c
r: the row number, counting from 0
c: the column number, counting from 0
cols: how many columns each row has (4 in the grid above)
base: the memory address of element (0, 0), where the grid starts
size: how many bytes one element takes
In words: to reach a cell in a row-major grid, skip every complete earlier row, then the earlier cells in its own row, and convert that count of elements into bytes. Moving one column along moves one element; moving one row down jumps a whole row.
```

In the 3-by-4 grid of 4-byte integers above, row 1, column 2 comes after six earlier cells, so it starts twenty-four bytes after the grid's start. In a column-major language the roles swap: you skip whole columns first.

Loop order matters. Iterating row by row walks memory sequentially. Iterating column by column jumps a whole row's worth of bytes (the column count multiplied by the element size) every step, potentially touching a different cache line each time when that **stride** is large. Performance depends on dimensions, cache hierarchy and compiler transformations.

> [!analogy] Real-world analogy: Reading a page across or down
> A printed page is laid out line by line. Reading across each line uses every word your eyes land on before you move down. Reading only the first word of every line, then the second word of every line, makes your eyes jump a whole line each time and revisit the page many times.
>
> **How it maps:** The page is row-major memory, a line of text is a row, and each glance is a cache line: it brings in a run of neighbouring elements. A row-by-row loop uses the whole glance; a column-by-column loop jumps a full row's stride and may use only one element from each line it brings in.
>
> **Where it stops:** A reader can see a whole page at once, while a cache holds a limited number of lines and may evict one before the loop comes back to it. Hardware prefetching and compiler loop interchange can also change the outcome, so the real cost must be measured.

## Key takeaways
- Scan the contiguous dimension for sequential memory access.
- A cache-performance claim needs stated hardware and workload assumptions.

## Further reading
- [Array (data structure) — Wikipedia](https://en.wikipedia.org/wiki/Array_(data_structure))
- [Row- and column-major order — Wikipedia](https://en.wikipedia.org/wiki/Row-_and_column-major_order)
