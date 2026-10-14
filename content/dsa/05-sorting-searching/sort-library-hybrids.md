---
id: sort-library-hybrids
title: pdqsort and language sorting contracts
level: advanced
minutes: 3
sourceLesson: sort-real-world
summary: Pattern checks and bounded insertion attempts exploit favourable inputs.
---

This unit builds on the preceding sorting units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

## pdqsort

Orson Peters' **pattern-defeating quicksort** (2016, paper 2021) is the modern unstable sort. Go adopted it for `sort.Sort` in Go 1.19, and Rust used it for `sort_unstable` for years (Rust 1.81 replaced it with **ipnsort**, a successor by Peters and Bergdoll). It extends introsort with ideas that make common patterns fast:

- **Pivot selection**: median-of-three, or Tukey's ninther for larger arrays.
- **Partial insertion sort**: if partitioning detects an already partitioned range (excluding pivot setup), try insertion sort with a small cap on moves. On sorted or nearly sorted input this finishes in O(n).
- **Equal-element handling**: if the pivot equals the element just before the current sub-array, all elements equal to it are partitioned off in one pass. With k distinct keys the cost is O(nk), linear for few distinct values.
- **Bad-partition detection**: an unbalanced split triggers a shuffle of a few elements to break adversarial patterns. After a logarithmic budget of bad partitions, it falls back to heapsort, guaranteeing O(n log n).
- **Branchless block partitioning** (from BlockQuicksort) for cheap comparisons such as integers, avoiding branch mispredictions on random data.

The result: O(n log n) worst case, in place, and linear on sorted, reversed and all-equal inputs.

## What your language actually uses

| Language | Default | Stable? |
|---|---|---|
| Python `sorted`, `list.sort` | Timsort (powersort merges) | Yes |
| Java objects, `List.sort` | TimSort | Yes |
| Java primitives | Dual-pivot quicksort | n/a |
| JavaScript `Array.sort` | Timsort in V8 | Yes |
| C++ `std::sort` | Typically introsort-family; implementation-specific | No |
| C++ `std::stable_sort` | Typically merge-based; implementation-specific | Yes |
| Rust `sort` / `sort_unstable` | driftsort / ipnsort | Yes / No |
| Go `sort.Sort`, `slices.Sort` | pdqsort | No |

Notes on the table:

- Java sorts primitives with an unstable quicksort because equal `int`s are indistinguishable, so stability is invisible. Objects need stability, so they get TimSort.
- JavaScript only **required** a stable sort from ES2019; older engines differed.
- Go provides `sort.Stable` and `slices.SortStableFunc` when you need stability.
- C's `qsort` specifies neither the algorithm nor stability.

## Key takeaways
- Pattern checks and bounded insertion attempts exploit favourable inputs.
- Know whether stability and complexity are API guarantees or implementation choices.

## Further reading
- [pdqsort design and guarantees — project documentation](https://raw.githubusercontent.com/orlp/pdqsort/master/readme.md)
- [Go 1.19 sorting implementation change](https://go.dev/doc/go1.19)
- [Slice sorting contracts — Rust documentation](https://doc.rust-lang.org/std/primitive.slice.html)
