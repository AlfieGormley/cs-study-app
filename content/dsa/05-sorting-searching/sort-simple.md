---
id: sort-simple
title: Simple sorts and what they teach
level: basic
minutes: 12
summary: Bubble, selection and insertion sort, and the vocabulary they introduce: stability, in-place, adaptive behaviour and inversions.
---

Bubble sort is rarely the right general-purpose library sort. So why learn the three "simple" sorts?

Because they are small enough to hold in your head, and each one makes a different trade-off visible. Selection sort minimises writes. Insertion sort exploits order that is already there. Bubble sort shows why "obviously correct" can still be slow. And the vocabulary they introduce (stable, in-place, adaptive) is exactly the vocabulary you need to choose between production sorts later.

Insertion sort is not just a teaching tool either: it runs inside Timsort, introsort and pdqsort for small sub-arrays.

## The vocabulary

Before the algorithms, four properties that every sort in this module will be judged on.

- **In-place**: uses O(1) extra memory beyond the input (some definitions allow O(log n) for a recursion stack). Bubble, selection and insertion are all in-place.
- **Stable**: equal keys keep their original relative order. If you sort orders by date and two orders share a date, a stable sort leaves them in the order they arrived.
- **Adaptive**: runs faster when the input is already partly sorted.
- **Online**: can sort a stream, accepting elements one at a time.

We also count two different costs: **comparisons** (is `a[i] < a[j]`?) and **moves** (swaps or writes). They matter in different settings. Comparing two long strings is expensive; writing to flash memory wears it out.

### Inversions: a measure of disorder

An **inversion** is a pair of positions `i < j` with `a[i] > a[j]`. A sorted array has 0 inversions. A reversed array of n distinct items has the maximum, n(n−1)/2.

```
[3, 1, 2]
inversions: (3,1) and (3,2)  ->  2
```

Inversions matter because swapping an out-of-order **adjacent** pair removes exactly one inversion; swapping an ordered pair can instead add one. So it must do at least as many swaps as there are inversions, which is n(n−1)/4 on a uniformly random permutation of distinct keys. That single fact explains why bubble and insertion sort are quadratic on average.

## Bubble sort

Repeatedly walk the array, swapping neighbours that are out of order. After the first pass the largest element has "bubbled" to the end; after pass k, the last k positions are final.

```python
def bubble_sort(a):
    n = len(a)
    for end in range(n - 1, 0, -1):
        swapped = False
        for i in range(end):
            if a[i] > a[i + 1]:
                a[i], a[i+1] = a[i+1], a[i]
                swapped = True
        if not swapped:
            break   # no swaps: sorted
```

- Comparisons: up to n(n−1)/2. With the `swapped` flag, a sorted input finishes after one pass of n−1 comparisons, so it is adaptive in the best case.
- Swaps: exactly the number of inversions.
- Stable, because it only swaps when strictly greater (`>`). Change that to `>=` and equal elements leapfrog each other: no longer stable.

Bubble sort has an asymmetry. A large element near the start (a "rabbit") races to the end in one pass. A small element near the end (a "turtle") moves only one position left per pass.

```
[2, 3, 4, 5, 1]   1 is a turtle
pass 1: [2, 3, 4, 1, 5]
pass 2: [2, 3, 1, 4, 5]
pass 3: [2, 1, 3, 4, 5]
pass 4: [1, 2, 3, 4, 5]
```

Four passes to move one element. Cocktail shaker sort (alternating direction) helps with turtles, but it is still O(n²).

## Selection sort

Find the minimum of the unsorted part and swap it into the next position.

```python
def selection_sort(a):
    n = len(a)
    for i in range(n - 1):
        m = i
        for j in range(i + 1, n):
            if a[j] < a[m]:
                m = j
        a[i], a[m] = a[m], a[i]
```

- Comparisons: always exactly n(n−1)/2, whatever the input. It is **not adaptive**: a sorted array costs the same as a reversed one.
- Swaps: at most n−1. This is its one virtue. If writes are far more expensive than reads, selection sort has a linear worst-case swap bound, while bubble and insertion can require quadratic data movement. It need not use the fewest writes on every particular input.
- **Not stable** in its usual array form. The long-distance swap can jump an element past its equal twin:

```
[2a, 2b, 1]
i=0: min is 1, swap with 2a
     [1, 2b, 2a]   2a and 2b reversed
```

You can make it stable by shifting instead of swapping (insert the minimum and slide the rest right), but that costs O(n) writes per step and throws away its only advantage.

## Insertion sort

Keep a sorted prefix. Take the next element and slide it left until it sits in the right place, like sorting a hand of cards.

```python
def insertion_sort(a):
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]   # shift right
            j -= 1
        a[j + 1] = key
```

Trace on `[5, 2, 4, 6, 1, 3]` (the bar marks the end of the sorted prefix):

```
start     [5 | 2, 4, 6, 1, 3]
key=2     [2, 5 | 4, 6, 1, 3]   1 shift
key=4     [2, 4, 5 | 6, 1, 3]   1 shift
key=6     [2, 4, 5, 6 | 1, 3]   0 shifts
key=1     [1, 2, 4, 5, 6 | 3]   4 shifts
key=3     [1, 2, 3, 4, 5, 6]    3 shifts
```

Total shifts: 9, which is exactly the number of inversions in the input. That is the key insight:

> [!note] Insertion sort is O(n + inversions)
> Each shift removes one inversion, and each element costs at most one extra comparison to stop. So the running time is Θ(n + I), where I is the number of inversions. Sorted input: I = 0, so O(n). Reversed: I = n(n−1)/2, so O(n²). An array where every element is within k places of its final position has I ≤ nk, so O(n(k + 1)), including the sorted case k = 0.

Insertion sort is:

- **Stable**, because it stops at the first element that is not strictly greater (`a[j] > key`).
- **Adaptive**, in the strong sense above.
- **Online**: you can feed it elements one at a time and the prefix is always sorted.
- **Fast for small n**. Its inner loop is a tight compare-and-shift with sequential memory access and no recursion. Below roughly 16 to 64 elements it usually beats merge sort and quicksort, whose overheads (function calls, extra buffers, pivot selection) dominate at that size.

A variant, **binary insertion sort**, finds the insertion point with binary search. That cuts comparisons to O(n log n), but shifting is still O(n²). It pays off when comparisons are expensive, which is why CPython uses it to build short runs in its list sort.

## Comparison

| Sort | Comparisons | Swaps/writes | Stable? |
|---|---|---|---|
| Bubble | O(n²), O(n) if sorted | = inversions | Yes |
| Selection | n(n−1)/2 always | ≤ n−1 swaps | No |
| Insertion | O(n + I) | = I shifts | Yes |

All three are in-place with O(1) extra space and O(n²) average and worst case.

## Where these appear in real systems

- **Hybrid sorts.** Timsort (Python, Java objects, V8) extends short runs with binary insertion sort. C++'s `std::sort` in libstdc++ finishes with insertion sort over the nearly sorted array that introsort leaves behind. pdqsort switches to insertion sort for partitions below about 24 elements.
- **Nearly sorted data.** Maintaining a sorted list with occasional appends, or re-sorting a leaderboard after a few scores change, is close to O(n) with insertion sort.
- **Shell sort** generalises insertion sort by first sorting elements far apart (gaps like 701, 301, 132, ... 1), removing many inversions with each long move. It is still used in some embedded code because it is tiny and needs no recursion.

## Pitfalls

1. **Breaking stability by accident.** Using `>=` instead of `>` in bubble or insertion sort silently makes them unstable. Stability is a property of the implementation, not just the algorithm's name.
2. **Assuming "simple" means "fine for small inputs" without measuring what small is.** At n = 10,000, n²/2 is 50 million comparisons. **Content gap:** cross-language millisecond/second timings are omitted because no reproducible benchmark, hardware or implementation was supplied.
3. **Judging by comparisons alone.** Selection sort and insertion sort both do about n²/2 comparisons on reversed input, but insertion sort does about n²/2 writes while selection sort does at most n−1 swaps. Which is cheaper depends on what your "write" costs.

## Key takeaways
- Any sort that only swaps adjacent elements needs at least one swap per inversion, so it needs Ω(n²) swaps on a uniformly random permutation of distinct keys. This is a lower bound, not an upper bound on every such algorithm.
- Bubble sort: stable, adaptive with an early-exit flag, but slow and plagued by "turtles".
- Selection sort: always n(n−1)/2 comparisons, at most n−1 swaps, not stable.
- Insertion sort: stable, online, Θ(n + inversions), and often a good choice for small arrays or arrays with few inversions, which is why production hybrid sorts use it.
- Stability, in-place and adaptivity are the properties you will use to judge every other sort.

## Further reading
- [Insertion sort — Wikipedia](https://en.wikipedia.org/wiki/Insertion_sort)
- [Elementary Sorts — Algorithms, 4th ed. (Sedgewick and Wayne)](https://algs4.cs.princeton.edu/21elementary/)
- [Bubble sort — Wikipedia](https://en.wikipedia.org/wiki/Bubble_sort)
- [Selection sort — Wikipedia](https://en.wikipedia.org/wiki/Selection_sort)
- [Adaptive sort — Wikipedia](https://en.wikipedia.org/wiki/Adaptive_sort)
