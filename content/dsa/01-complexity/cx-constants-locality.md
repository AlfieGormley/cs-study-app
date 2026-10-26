---
id: cx-constants-locality
sourceLesson: cx-in-practice
title: Constants, locality and theoretical winners
level: advanced
minutes: 3
summary: Explain practical performance differences hidden by asymptotic labels.
---

Two implementations can share a growth class yet perform very differently. Asymptotic notation deliberately hides fixed factors and simplifies the memory system.

## Small pieces can favour simple methods

Insertion sort has quadratic worst-case work in its run length, but small pieces can benefit from its simple operations and contiguous access. A hybrid sort can use it only below a fixed run-size cap. Across all pieces, that bounded work remains linear in the total item count; the merging or partitioning stages determine the larger-input bound.

CPython 3.14's natural merge sort extends short runs using binary insertion sort and uses a Powersort merge policy. Its tuning choices are implementation details. The useful general idea is to bound expensive small-run work and measure whether it helps.

## Locality changes the cost per access

Contiguous arrays place neighbouring values near one another. Scattered linked-list nodes require following references; the next address may not be known until the previous node is loaded. Both traversals are linear in item count, but their cache misses and memory dependencies differ.

For a C-style row-major matrix, neighbouring columns within one row are contiguous. Traversing down a column instead jumps by a row stride. Both orders visit every entry, yet row order usually has better spatial locality for large matrices. Exact timing depends on layout, cache size, associativity, compiler transformations and hardware. Total matrix size alone does not prove every column access misses the cache.

> [!analogy] Real-world analogy: Reading a shelf in order
> Reading adjacent book labels can be easier than following instructions to shelves across a building.
>
> **How it maps:** Nearby array elements resemble adjacent labels; dependent pointers resemble directions learned only after reaching each location.
>
> **Where it stops:** CPUs prefetch, cache and overlap work. The comparison suggests locality, not a numerical slowdown.

## A smaller exponent still needs a practical implementation

Some theoretically faster algorithms have large constants or extra storage needs. Compare a proposed matrix-multiplication implementation with a measured baseline using representative sizes, numeric types, memory limits and accuracy requirements. A ratio of powers with assumed unit constants cannot establish a real speedup.

## Key takeaways
- Constants and locality matter over finite input ranges.
- A bounded quadratic subroutine can fit inside a faster-growing overall algorithm.
- Benchmark time, peak memory and accuracy before replacing a tuned baseline.

## Further reading
- [CPython 3.14 sorting design](https://github.com/python/cpython/blob/3.14/Objects/listsort.txt)
- [What every programmer should know about memory](https://www.akkadia.org/drepper/cpumemory.pdf)
