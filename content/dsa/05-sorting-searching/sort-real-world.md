---
id: sort-real-world
title: Real-world sorting
level: advanced
minutes: 15
summary: What your language's sort actually does (Timsort, pdqsort, introsort, dual-pivot quicksort), how runs and galloping exploit real data, and how comparators, keys and stability go wrong in production.
---

Textbook sorts assume random input. Real data is rarely random. Log files arrive nearly sorted by timestamp. A table is re-sorted after a few rows change. Two sorted lists are concatenated. A column has five distinct values across ten million rows.

Production sorts are **hybrids** engineered to exploit that structure while keeping a worst-case guarantee. This lesson covers the two most important designs, **Timsort** and **pdqsort**, what each mainstream language uses, and the bugs that come from comparators and stability rather than the algorithms.

## Timsort

Tim Peters wrote Timsort for Python in 2002. It became the object sort in Java 7, the sort in Android, V8 (Chrome and Node.js, since V8 7.0 in 2018) and Swift. It is a **stable, adaptive merge sort** built around **runs**.

### 1. Find natural runs

Scan for ascending or descending runs. In the original Timsort design, descending runs must be strictly decreasing before a plain reversal, because reversing equal elements breaks stability. CPython 3.14 also handles non-increasing runs by reversing equal-key subruns first, then reversing the whole run to restore tie order. The diagram below illustrates distinct keys.

```
[1, 4, 7, 9, 8, 5, 2, 3, 6]
 run A: 1 4 7 9 (ascending)
 run B: 8 5 2   (descending -> 2 5 8)
 run C: 3 6     (ascending)
```

### 2. Enforce a minimum run length

Merging lots of tiny runs is wasteful. CPython 3.14 computes a **minrun** between 32 and 64 for large arrays and extends short natural runs using **binary insertion sort**. For arrays shorter than 64 it detects the first run, then extends it to the whole array if needed. Other Timsort implementations use different thresholds.

On random data, most runs are extended to minrun; a final short remainder or a longer natural run can differ, and Timsort behaves like a well-tuned bottom-up merge sort.

### 3. Merge runs with a balanced policy

Runs are pushed onto a stack. Timsort merges only **adjacent** runs (merging non-adjacent ones would break stability) and chooses when to merge so that merges stay balanced and the stack stays small.

Classic Timsort uses run-length inequalities such as |A| > |B| + |C| and |B| > |C| to keep pending runs growing geometrically toward the bottom of the stack. Correct collapse logic must maintain the intended invariant beyond just the top three runs. Stack capacity and policies differ by implementation; CPython uses powersort.

> [!warning] A proof found a bug
> In 2015, researchers formally verifying Java's `TimSort` with the KeY tool found that the merge-collapse rules did not always restore the invariant. On specially crafted arrays of around 67 million elements, the run stack overflowed with an `ArrayIndexOutOfBoundsException`. Python fixed the rule; Java enlarged the stack. Since Python 3.11, CPython uses the **powersort** merge policy (Munro and Wild), which is provably near-optimal and simpler to reason about.

### 4. Gallop when one run is winning

During a normal merge, Timsort counts how many times in a row the output came from the same run. If that reaches `MIN_GALLOP` (initially 7), it switches to **galloping**: an exponential search checking positions 1, 3, 7, 15, ... then a binary search, to find how many elements it can copy in one block.

```
A: [1 2 3 4 5 ... 1000]
B: [500.5, 2000]
normal merge: ~500 comparisons for A's head
galloping: ~2·log2(500) ≈ 18 compares
```

If galloping stops paying off, the threshold rises; if it keeps paying off, it falls. This adaptivity is why concatenating two sorted lists and sorting costs close to O(n), not O(n log n).

### Timsort's profile

| Input | Cost |
|---|---|
| Already sorted / reversed | O(n): one run |
| k runs | O(n(1 + log k)) adaptive bound |
| Random | O(n log n), close to merge sort |
| Merge buffer | up to n/2 elements; key caching and other metadata add storage |

Timsort minimises **comparisons**, which is exactly right for Python and JavaScript, where each comparison is a dynamic call that may run user code and costs far more than moving a pointer.

## pdqsort

Orson Peters' **pattern-defeating quicksort** (2016, paper 2021) is the modern unstable sort. Go adopted it for `sort.Sort` in Go 1.19, and Rust used it for `sort_unstable` for years (Rust 1.81 replaced it with **ipnsort**, a successor by Peters and Bergdoll). It extends introsort with ideas that make common patterns fast:

- **Pivot selection**: median-of-three, or Tukey's ninther for larger arrays.
- **Partial insertion sort**: if partitioning detects an already partitioned range (excluding pivot setup), try insertion sort with a small cap on moves. On sorted or nearly sorted input this finishes in O(n).
- **Equal-element handling**: if the pivot equals the element just before the current sub-array, all elements equal to it are partitioned off in one pass. With k distinct keys the cost is O(nk), linear for few distinct values.
- **Bad-partition detection**: an unbalanced split triggers a shuffle of a few elements to break adversarial patterns. After about log n bad partitions, it falls back to heapsort, guaranteeing O(n log n).
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

## Comparators: the contract

A comparator must define a **strict weak ordering**. In practice:

1. Consistent: `cmp(a, b)` always gives the same answer for the same pair.
2. Irreflexive and asymmetric: never a < a; if a < b then not b < a.
3. Transitive: a < b and b < c imply a < c, and the same for "equal".

Break the contract and the consequences depend on the language:

- **Java** TimSort may throw `IllegalArgumentException: Comparison method violates its general contract!`, often only on large or unlucky inputs, so it passes tests and fails in production.
- **C++** `std::sort` has **undefined behaviour**. Real implementations can run past the end of the array (the unguarded insertion sort assumes a sentinel), causing crashes or memory corruption.
- **Rust** may panic since 1.81, but never causes memory unsafety.
- **Python** may produce an order that does not satisfy the intended relation; user comparison code can also raise exceptions.

Common ways to break it:

```java
// overflow: 2e9 - (-2e9) wraps negative
(a, b) -> a - b
// fix
(a, b) -> Integer.compare(a, b)
```

- Random comparators (`() => Math.random() - 0.5` to "shuffle") are inconsistent and produce biased shuffles. Use Fisher–Yates.
- **NaN.** Ordered comparisons (<, <=, >, >=) with NaN are false, while != is true. Treating NaN as equivalent to every value via neither-less-than breaks transitivity of incomparability. In Python, `sorted([3, nan, 1, 2])` returns `[3, nan, 1, 2]`: not sorted at all. Filter NaNs out first or use a key that places them explicitly.
- Comparators that read mutable state (a "current time" or a cache that changes mid-sort).

## Keys instead of comparators

Python 3 dropped `cmp` in favour of `key`. A key function is called **once per element**: n calls. A comparator is called on every comparison: O(n log n) calls in the worst case for this sort, often fewer on ordered inputs. For a million items that is 1 million versus 20 million calls to an expensive function, such as lower-casing a string or parsing a date.

```python
rows.sort(
    key=lambda r: (r.country, -r.score))
```

This "decorate, sort, undecorate" pattern is known as the **Schwartzian transform** from Perl. Tuple keys give lexicographic multi-field order. When a field cannot be negated (strings in descending order), use `functools.cmp_to_key` or rely on stability.

## Stability in practice

Stability lets you build multi-key sorts from single-key sorts. **Sort by the secondary key first, then by the primary key:**

```python
people = [("ann", 30), ("bob", 25),
          ("cat", 30), ("dan", 25)]
people.sort(key=lambda p: p[0])  # name
people.sort(key=lambda p: p[1])  # age
# [('bob',25), ('dan',25),
#  ('ann',30), ('cat',30)]
```

The second sort orders by age; within equal ages, the stable sort keeps the name order from the first sort. This is exactly how clicking "sort by name" and then "sort by age" behaves in a spreadsheet or UI table: users expect the earlier ordering to survive within ties, and an unstable sort makes rows jump around.

Python's `reverse=True` is also stable: equal elements keep their original order rather than being reversed.

> [!tip] Choosing in practice
> Use your language's default sort with a key function. Reach for a stable sort when the order of ties is visible to users or downstream code. Reach for an unstable one (`sort_unstable`, `std::sort`) only when you have measured that sorting matters and ties are indistinguishable.

## Key takeaways
- Timsort finds natural runs, extends short ones with binary insertion sort, merges adjacent runs with a balanced policy and gallops when one run dominates: O(n) on sorted data, stable, and reduced comparisons on partially ordered data.
- pdqsort extends introsort with pattern detection, equal-key partitioning and branchless partitioning: unstable, in place, O(n log n) worst case and linear on common patterns.
- Python, Java objects and JavaScript use stable Timsort; C++ `std::sort`, Go and Rust's `sort_unstable` use unstable introsort-family algorithms.
- Comparators must be a strict weak ordering. Subtraction overflow, NaNs and random comparators cause exceptions, undefined behaviour or silent misordering.
- Prefer key functions (n calls) over comparators (n log n calls), and use stability to compose multi-key sorts.

## Further reading
- [listsort.txt: Tim Peters' description of Timsort (CPython)](https://github.com/python/cpython/blob/main/Objects/listsort.txt)
- [Pattern-defeating Quicksort — Orson Peters (arXiv)](https://arxiv.org/abs/2106.05123)
- [Getting things sorted in V8 — V8 blog](https://v8.dev/blog/array-sort)
- [Sorting techniques — Python docs](https://docs.python.org/3/howto/sorting.html)
- [Timsort — Wikipedia](https://en.wikipedia.org/wiki/Timsort)
- [Go 1.19 release notes (sort uses pdqsort)](https://go.dev/doc/go1.19)
