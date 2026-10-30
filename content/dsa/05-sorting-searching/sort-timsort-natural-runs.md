---
id: sort-timsort-natural-runs
title: Timsort runs and short-range insertion
level: advanced
minutes: 3
sourceLesson: sort-real-world
summary: Run detection exploits existing order before merging.
---

Textbook sorts assume random input. Real data is rarely random. Log files arrive nearly sorted by timestamp. A table is re-sorted after a few rows change. Two sorted lists are concatenated. A column has five distinct values across ten million rows.

Production sorts are **hybrid sorting algorithms** engineered to exploit that structure while keeping a worst-case guarantee. Throughout, n is the number of elements, and costs use Big O notation (O(n log n) grows like n times the base-2 logarithm of n, about 20 million for a million elements). This lesson covers the two most important designs, **Timsort** and **pdqsort**, what each mainstream language uses, and the bugs that come from comparators and stability rather than the algorithms.

## Timsort

Tim Peters wrote Timsort for Python in 2002. It became the object sort in Java 7 and Android's Java libraries, and the array sort in V8 (Chrome and Node.js) since V8 7.0 in 2018; Swift's standard-library sort uses a Timsort-style run-merging design. It is a **stable, adaptive merge sort** built around **runs**.

### 1. Find natural runs

Scan for ascending or descending runs. In the original Timsort design, descending runs must be strictly decreasing before a plain reversal, because reversing equal elements breaks stability. CPython 3.14 also handles non-increasing runs by reversing equal-key subruns first, then reversing the whole run to restore tie order. The diagram below illustrates distinct keys.

```
[1, 4, 7, 9, 8, 5, 2, 3, 6]
 run A: 1 4 7 9 (ascending)
 run B: 8 5 2   (descending -> 2 5 8)
 run C: 3 6     (ascending)
```

> [!analogy] Real-world analogy: re-shelving a returns trolley
> A librarian re-shelving a trolley of returned books first notices stretches that are already in order (someone returned a whole series together) and keeps each stretch as a block. A stretch in exactly reverse order is simply flipped. Only then are the blocks merged into place.
>
> **How it maps:** each ordered stretch is a natural run, flipping a reversed stretch is run reversal, and merging blocks is Timsort's merge phase. The more order the trolley already has, the less work is left.
>
> **Where it stops:** a librarian can eyeball a whole stretch at once, while Timsort discovers a run one comparison at a time. And flipping a stretch that contains two copies of the same book would swap those copies, which is why reversal needs care with equal keys.

### 2. Enforce a minimum run length

Merging lots of tiny runs is wasteful. CPython 3.14 computes a **minrun** between 32 and 64 for large arrays and extends short natural runs using **binary insertion sort**. For arrays shorter than 64 it detects the first run, then extends it to the whole array if needed. Other Timsort implementations use different thresholds.

On random data, most runs are extended to minrun; a final short remainder or a longer natural run can differ, and Timsort behaves like a well-tuned bottom-up merge sort.

## Key takeaways
- Run detection exploits existing order before merging.
- Reversing a descending run must preserve ties; short runs are extended with binary insertion sort.

## Further reading
- [Sorting techniques — Python documentation](https://docs.python.org/3/howto/sorting.html)
- [CPython 3.14.0 list-sort design notes](https://raw.githubusercontent.com/python/cpython/v3.14.0/Objects/listsort.txt)
