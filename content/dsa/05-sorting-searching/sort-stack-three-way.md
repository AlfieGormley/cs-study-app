---
id: sort-stack-three-way
title: Bounded stacks and duplicate-aware partitions
level: intermediate
minutes: 3
sourceLesson: sort-quicksort
summary: Recursing only on the smaller side bounds stack growth.
---

This unit builds on the preceding sorting units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

## Recursion depth

Even with good pivots, naive quicksort can recurse O(n) deep on bad luck. The fix is simple: **recurse into the smaller side and loop on the larger**. Each recursive call is on at most half the elements, so the size halves with every level of nesting:

```formula
D ≤ ⌊log_2(n)⌋ + 1
D ≤ ⌊log_2(10^6)⌋ + 1 = 20
where
D: number of simultaneous stack frames including the initial call, for a nonempty array
⌊ ⌋: floor, round down to an integer
n: the number of elements; here a million (10^6)
log_2(n): the base-2 logarithm of n: how many times n can be halved before reaching 1
≤: less than or equal to
≈: approximately equal to
In words: if every nested call gets at most half the elements, there can be at most about log_2(n) of them stacked up.
```

The larger side is handled by the loop, which uses no extra stack.

```python
def quicksort(a, lo, hi):
    while lo < hi:
        # Partition before choosing the next
        # range.
        p = lomuto(a, lo, hi)
        # Only nest recursion on the smaller
        # side.
        if p - lo < hi - p:
            quicksort(a, lo, p - 1)
            # Discard the pivot and its left
            # side.
            lo = p + 1
        else:
            quicksort(a, p + 1, hi)
            # Discard the pivot and its
            # right side.
            hi = p - 1
```

## 3-way partitioning

Real data often has many duplicates: sorting a million orders by country code, or by a status with five values. Two-way partitioning keeps re-partitioning equal keys. **3-way partitioning** (Dijkstra's Dutch national flag problem) splits into `< pivot`, `= pivot` and `> pivot`, and recurses only on the outer two.

```python
def three_way(a, lo, hi):
    pivot = a[lo]
    lt, i, gt = lo, lo, hi
    while i <= gt:
        if a[i] < pivot:
            a[lt], a[i] = a[i], a[lt]
            lt += 1
            i += 1
        # Swap from the right; recheck this
        # index.
        elif a[i] > pivot:
            a[i], a[gt] = a[gt], a[i]
            # The swapped-in item is still
            # untested.
            gt -= 1
        else:
            i += 1
    return lt, gt  # a[lt..gt] == pivot
```

```
[3, 5, 3, 1, 3, 6, 2, 3]  pivot 3
->[1, 2, 3, 3, 3, 3, 6, 5]
         lt 2     gt 5
recurse on [1, 2] and [6, 5] only
```

With k distinct key values among the n elements, randomized 3-way quicksort has an expected O(n(1 + log k)) bound; exact work also depends on key frequencies; with all keys equal, it is a single O(n) pass. Sedgewick and Bentley showed this is optimal up to a constant for inputs with many duplicates.

## Key takeaways
- Recursing only on the smaller side bounds stack growth.
- Three-way partitioning finishes equal keys immediately and recurses on the outer ranges.

## Further reading
- [Quicksort and partitioning — Princeton Algorithms](https://algs4.cs.princeton.edu/23quicksort/)
