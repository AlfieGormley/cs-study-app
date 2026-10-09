---
id: sort-quicksort
title: Quicksort
level: intermediate
minutes: 15
summary: Lomuto and Hoare partitioning, pivot choice, the O(n²) worst case and how randomisation, 3-way partitioning and introsort defend against it.
---

Merge sort does its work on the way **up**: split blindly, then merge carefully. Quicksort does the opposite. It works on the way **down**: partition carefully, then the two halves need no combining at all.

1. Pick a **pivot** element.
2. **Partition**: rearrange the array so everything smaller than the pivot comes before everything larger.
3. Recursively sort the two sides. Done; there is no merge step.

Throughout this lesson, n is the number of elements being sorted, and costs use Big O notation (O, Θ and Ω: at most, exactly and at least this growth rate, ignoring constant factors). Quadratic means growing with n², n × n.

Quicksort is in-place, has tiny inner loops and accesses memory sequentially, which can make it fast on arrays; the fastest choice depends on data, comparator and implementation. Its weakness is that a bad pivot makes the split lopsided, and a run of bad pivots makes it quadratic. Most of the engineering around quicksort is about avoiding that.

## Lomuto partition

The simpler scheme, popularised by Programming Pearls and CLRS. Use the last element as the pivot. Keep a boundary `i`: everything left of `i` is smaller than the pivot.

```python
def lomuto(a, lo, hi):
    pivot = a[hi]
    i = lo
    for j in range(lo, hi):
        if a[j] < pivot:
            a[i], a[j] = a[j], a[i]
            i += 1
    a[i], a[hi] = a[hi], a[i]
    return i   # pivot's final index

def quicksort(a, lo, hi):
    if lo < hi:
        p = lomuto(a, lo, hi)
        quicksort(a, lo, p - 1)
        quicksort(a, p + 1, hi)
```

Trace on `[7, 2, 1, 6, 8, 5, 3, 4]`, pivot 4:

```
j=1: 2<4 swap a[0],a[1] [2,7,1,6,8,5,3,4]
j=2: 1<4 swap a[1],a[2] [2,1,7,6,8,5,3,4]
j=6: 3<4 swap a[2],a[6] [2,1,3,6,8,5,7,4]
end: swap a[3],a[7]     [2,1,3,4,8,5,7,6]
                               ^ pivot at 3
```

After partitioning, the pivot is in its **final sorted position**. Recursion handles `[2,1,3]` and `[8,5,7,6]`.

## Hoare partition

Hoare's original 1961 scheme uses two pointers moving towards each other, swapping pairs that are on the wrong side.

```python
def hoare(a, lo, hi):
    pivot = a[(lo + hi) // 2]
    i, j = lo - 1, hi + 1
    while True:
        i += 1
        while a[i] < pivot:
            i += 1
        j -= 1
        while a[j] > pivot:
            j -= 1
        if i >= j:
            return j
        a[i], a[j] = a[j], a[i]

def quicksort(a, lo, hi):
    if lo < hi:
        p = hoare(a, lo, hi)
        quicksort(a, lo, p)      # note: p
        quicksort(a, p + 1, hi)
```

Same input, pivot `a[3] = 6`:

```
swap a[0],a[7] [4,2,1,6,8,5,3,7]
swap a[3],a[6] [4,2,1,3,8,5,6,7]
swap a[4],a[5] [4,2,1,3,5,8,6,7]
pointers cross: return j=4
left [4,2,1,3,5]   right [8,6,7]
```

Two differences matter:

- Under a uniformly random permutation of distinct keys, these classical schemes give Hoare roughly one-third of Lomuto's expected swaps; this is not a bound for every input.
- Hoare does **not** put the pivot in its final place. It only guarantees that everything in the left part is no bigger than the pivot and everything in the right part is no smaller. So the recursion is on `[lo, p]` and `[p+1, hi]`, not `p-1`. Using Lomuto bounds with Hoare can leave an unsorted boundary element out of recursion. Choosing `hi` as the pivot index in this Hoare variant can instead fail to shrink a partition and cause infinite recursion.

### Duplicates

On an array where every element is equal, Lomuto with `<` finds nothing smaller, so every partition is 0 versus n−1: **O(n²)**. Hoare's pointers stop on equal elements (`<` and `>` are strict), swap them, and meet in the middle: balanced splits, O(n log n). Stopping on equal keys looks wasteful but is exactly what saves it.

## Pivot choice and the worst case

Quicksort's cost depends entirely on how balanced the splits are. Two **recurrences** (costs written in terms of the same cost on smaller inputs) show the two extremes:

```formula
T_good(n) = 2 × T_good(n / 2) + n
T_good(n) = Θ(n × log n)
T_bad(n) = T_bad(n − 1) + n
T_bad(n) = Θ(n^2)
where
T_good(n): the running time on n elements when every pivot is the median, so each split is exactly in half
T_bad(n): the running time when every pivot is the smallest or largest element, so each split peels off just one element
n: the number of elements in the current sub-array; the "+ n" term is the partition, which looks at every element once
Θ: Big Theta: exactly this growth rate, up to a constant factor
log: the logarithm (base 2 here; the base only changes a constant)
n^2: n squared, n × n
In words: halving every time gives merge sort's n log n; removing only one element each time gives a sum of n + (n − 1) + … + 1, which is quadratic.
```

With the first or last element as the pivot, **already sorted input** is the worst case: each partition peels off one element. Lomuto then compares the pivot with every other element of a sub-array that shrinks by one each time:

```formula
C = (n − 1) + (n − 2) + … + 1
C = n × (n − 1) / 2
C = 100 × 99 / 2 = 4950
C = 10^6 × (10^6 − 1) / 2 ≈ 5 × 10^11
where
C: the number of comparisons Lomuto quicksort makes on sorted input with a last-element pivot
n: the number of elements; 100 in the first example, 1,000,000 (10^6) in the second
…: "and so on", down to 1
10^6: ten to the power 6, a million; 10^11 is a hundred billion
≈: approximately equal to
In words: sorted input turns quicksort into a triangle of comparisons, about n²/2 of them.
```

For 100 elements the recursion also goes 99 levels deep. For a million elements that is about 500 billion comparisons and a stack overflow. Sorted and reverse-sorted inputs are common in practice, so this is not theoretical.

Defences:

- **Median-of-three**: use the median of the first, middle and last elements. Fixes sorted and reverse-sorted inputs and gives slightly better splits on random data. Large arrays can use the "ninther" (median of three medians of three).
- **Random pivot**: pick a uniformly random element. Now no particular input is bad; only bad luck is. The expected number of comparisons is given below, for every fixed input of **distinct keys**, with fresh independent uniform pivots. Randomizing the pivot alone does not rescue Lomuto on all-equal keys. The probability of quadratic behaviour is vanishingly small for large n.

```formula
C_avg ≈ 2 × n × ln(n)
C_avg ≈ 1.39 × n × log_2(n)
C_avg ≈ 1.39 × 10^6 × 19.93 ≈ 2.8 × 10^7
where
C_avg: the expected (average) number of comparisons randomised quicksort makes on n distinct keys
n: the number of elements; 1,000,000 (10^6) in the last line
ln(n): the natural logarithm of n (base e, about 2.718); ln(n) ≈ 0.693 × log_2(n)
log_2(n): the base-2 logarithm of n, how many times n can be halved before reaching 1; log_2(10^6) ≈ 19.93
10^6: ten to the power 6, a million; 10^7 is ten million
≈: approximately equal to (the leading term only; lower-order terms are dropped)
In words: with random pivots, quicksort makes only about 39% more comparisons than perfect halving would, around 28 million for a million keys.
```

> [!warning] Deterministic pivots can be attacked
> If an attacker knows your pivot rule, they can construct an input that triggers the worst case. McIlroy's 1999 paper "A Killer Adversary for Quicksort" did this against C library `qsort` implementations. For untrusted input, use randomisation or a sort with a worst-case guarantee.

## Recursion depth

Even with good pivots, naive quicksort can recurse O(n) deep on bad luck. The fix is simple: **recurse into the smaller side and loop on the larger**. Each recursive call is on at most half the elements, so the size halves with every level of nesting:

```formula
D ≤ log_2(n)
D ≤ log_2(10^6) ≈ 20
where
D: the maximum number of recursive calls on the stack at once (the recursion depth)
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
        p = lomuto(a, lo, hi)
        if p - lo < hi - p:
            quicksort(a, lo, p - 1)
            lo = p + 1
        else:
            quicksort(a, p + 1, hi)
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
        elif a[i] > pivot:
            a[i], a[gt] = a[gt], a[i]
            gt -= 1
        else:
            i += 1
    return lt, gt  # a[lt..gt] == pivot
```

```
[3, 5, 3, 1, 3, 6, 2, 3]  pivot 3
->[1, 2, 3, 3, 3, 3, 6, 5]
         lt=2     gt=5
recurse on [1, 2] and [6, 5] only
```

With k distinct key values among the n elements, randomized 3-way quicksort has an expected O(n(1 + log k)) bound; exact work also depends on key frequencies; with all keys equal, it is a single O(n) pass. Sedgewick and Bentley showed this is optimal up to a constant for inputs with many duplicates.

## Introsort: a worst-case guarantee

David Musser's **introsort** (1997) combines three algorithms:

1. Run quicksort (median-of-three pivots).
2. Track recursion depth. If it exceeds a limit (formula below), the pivots are going badly, so switch that sub-array to **heapsort**, which is O(n log n) worst case (lesson 4).
3. Leave sub-arrays below a threshold (16 elements in libstdc++) unsorted, then finish with insertion sort.

The depth limit in libstdc++ is:

```formula
d_max = 2 × ⌊log_2(n)⌋
d_max = 2 × ⌊log_2(10^6)⌋ = 2 × 19 = 38
where
d_max: the recursion depth at which introsort gives up on quicksort for that sub-array
n: the number of elements being sorted; here a million (10^6)
log_2(n): the base-2 logarithm of n; log_2(10^6) ≈ 19.93
⌊ ⌋: the floor: round down to a whole number, so ⌊19.93⌋ = 19
In words: introsort allows about twice the depth that perfect halving would need before deciding the pivots are bad.
```

Since heapsort costs O(n log n) on any sub-array it takes over, the total stays O(n log n). You get quicksort's speed in the common case and an O(n log n) guarantee. C++ requires `std::sort` to be O(n log n) in the worst case since C++11, and the major standard libraries (libstdc++, MSVC and, since 2022, libc++) use introsort-style hybrids. .NET's `Array.Sort` is introsort too. pdqsort (lesson 6) is a modern descendant.

## Variants in production

- **Dual-pivot quicksort** (Yaroslavskiy, 2009) partitions into three parts using two pivots. Java has used it for `Arrays.sort` on primitive arrays since Java 7. For the analyzed unsampled algorithm on uniformly random distinct keys, the leading comparison count is slightly lower, while swaps increase (formula below). This model alone does not establish a runtime or cache-miss improvement for a modern Java implementation.

```formula
C_dual ≈ 1.9 × n × ln(n)
C_classic ≈ 2 × n × ln(n)
where
C_dual: the expected comparisons of Yaroslavskiy's dual-pivot quicksort (leading term)
C_classic: the expected comparisons of classic single-pivot quicksort (leading term)
n: the number of elements, distinct and in uniformly random order
ln(n): the natural logarithm of n (base e, about 2.718)
≈: approximately equal to, keeping only the leading term
In words: dual-pivot quicksort makes about 5% fewer comparisons in this model.
```

- **Not stable.** Partitioning swaps elements over long distances, so equal keys can be reordered. That is why Java uses quicksort only for primitives (where stability is invisible) and a merge sort for objects.

## Summary

| | Quicksort |
|---|---|
| Average time | Θ(n log n), ~1.39 n log₂ n compares |
| Worst time | Θ(n²) (introsort: n log n) |
| Extra space | O(log n) stack with smaller-side recursion |
| Stable | No |

## Key takeaways
- Quicksort partitions around a pivot and recurses; there is no merge step, and it works in place.
- Lomuto is simpler and puts the pivot in its final place; Hoare does far fewer swaps but needs `[lo, p]` and `[p+1, hi]` recursion.
- First- or last-element pivots make sorted input Θ(n²); random or median-of-three pivots fix that, and randomisation gives ~1.39 n log₂ n expected comparisons for distinct keys; duplicate-heavy inputs need suitable partitioning.
- Recurse on the smaller side to bound stack depth at log₂ n.
- 3-way partitioning handles duplicates; introsort falls back to heapsort for a worst-case O(n log n) guarantee.

## Further reading
- [Quicksort — Algorithms, 4th ed. (Sedgewick and Wayne)](https://algs4.cs.princeton.edu/23quicksort/)
- [Quicksort — Wikipedia](https://en.wikipedia.org/wiki/Quicksort)
- [Quicksort is Optimal — Sedgewick and Bentley (slides)](https://www.cs.princeton.edu/~rs/talks/QuicksortIsOptimal.pdf)
- [Introsort — Wikipedia](https://en.wikipedia.org/wiki/Introsort)
- [Dutch national flag problem — Wikipedia](https://en.wikipedia.org/wiki/Dutch_national_flag_problem)
- [std::sort — cppreference](https://en.cppreference.com/w/cpp/algorithm/sort)
