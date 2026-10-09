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

Before the algorithms, a note on notation. Throughout this lesson, **n** is the number of elements being sorted. Costs are written in **Big O** notation, which describes how a cost grows as n grows and ignores constant factors:

- O(1): a fixed amount, however large n is.
- O(n): grows in proportion to n. Twice the elements, about twice the cost.
- O(n²): grows with n × n. Twice the elements, about four times the cost.
- O(log n): grows with the logarithm of n, the number of times you can halve n before reaching 1. It is about 20 for a million elements.

O(...) is an upper bound ("at most this fast-growing"). **Θ** (Big Theta) means "exactly this growth rate, up to a constant factor", and **Ω** (Big Omega) means "at least this growth rate".

Now the four properties that every sort in this module will be judged on.

- **In-place**: uses O(1) extra memory beyond the input (some definitions allow O(log n) for a recursion stack). Bubble, selection and insertion are all in-place.
- **Stable**: equal keys keep their original relative order. If you sort orders by date and two orders share a date, a stable sort leaves them in the order they arrived.
- **Adaptive**: runs faster when the input is already partly sorted.
- **Online**: can sort a stream, accepting elements one at a time.

We also count two different costs: **comparisons** (is `a[i] < a[j]`?) and **moves** (swaps or writes). They matter in different settings. Comparing two long strings is expensive; writing to flash memory wears it out.

### Inversions: a measure of disorder

An **inversion** is a pair of positions `i < j` with `a[i] > a[j]`: an earlier element that is bigger than a later one. A sorted array has 0 inversions.

```
[3, 1, 2]
inversions: (3,1) and (3,2)  ->  2
```

How many inversions can there be? An array of n elements has a fixed number of pairs of positions, and in a reversed array of distinct items every one of those pairs is out of order. That gives the maximum:

```formula
I_max = n × (n − 1) / 2
I_max = 4 × 3 / 2 = 6
where
I_max: the largest possible number of inversions, reached when the array is in exactly reverse order
n: the number of elements in the array (all distinct); here 4, as in [4, 3, 2, 1]
In words: each of the n elements can pair with the n − 1 others, and dividing by 2 stops each pair being counted twice; in a reversed array every pair is an inversion.
```

So `[4, 3, 2, 1]` has 6 inversions, and a reversed array of 1,000 items has 499,500.

Inversions matter because swapping an out-of-order **adjacent** pair removes exactly one inversion; swapping an ordered pair can instead add one. So a sort that only swaps neighbours must do at least as many swaps as there are inversions. On a typical shuffled input, that is about half the maximum:

```formula
E[I] = n × (n − 1) / 4
E[I] = 1000 × 999 / 4 = 249750
where
E[I]: the expected (average) number of inversions I, averaged over every possible ordering of the input
n: the number of elements, all distinct and in a uniformly random order; here 1,000
In words: each pair is out of order with probability one half, so on average half of the n × (n − 1) / 2 pairs are inversions.
```

This only holds for a **uniformly random permutation** (every ordering equally likely) of distinct keys. Real data is often far less disordered, which is exactly what adaptive sorts exploit. Still, this single fact explains why bubble and insertion sort are quadratic on average: about n²/4 swaps.

## Bubble sort

Repeatedly walk the array, swapping neighbours that are out of order. After the first pass the largest element has "bubbled" to the end; after the second pass the last two positions are final, and so on.

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

Each pass compares neighbours across the unsorted part, which is one element shorter each time. Without an early exit, the comparisons add up to:

```formula
C = (n − 1) + (n − 2) + … + 1
C = n × (n − 1) / 2
C = 10 × 9 / 2 = 45
where
C: the number of comparisons bubble sort makes when every pass runs
n: the number of elements in the array; here 10
…: "and so on": each term is one less than the one before, down to 1
In words: the first pass makes n − 1 comparisons, the next one fewer, and the total of that shrinking series is n × (n − 1) / 2.
```

- Comparisons: up to that total, 45 for 10 elements. With the `swapped` flag, a sorted input finishes after one pass of n−1 comparisons (9 for 10 elements), so it is adaptive in the best case.
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

The scan for the minimum always covers the whole unsorted part, so the counts never depend on the input:

```formula
C = (n − 1) + (n − 2) + … + 1
C = n × (n − 1) / 2
S ≤ n − 1
C = 500 × 499 / 2 = 124750
where
C: the number of comparisons selection sort makes, on every input
S: the number of swaps it makes (one per position, at most)
n: the number of elements in the array; here 500
…: "and so on", down to 1
≤: less than or equal to
In words: selection sort always makes about n²/2 comparisons, but never more than n − 1 swaps.
```

- Comparisons: always exactly that total, whatever the input. It is **not adaptive**: a sorted array costs the same as a reversed one.
- Swaps: at most n−1 (499 for 500 elements). This is its one virtue. If writes are far more expensive than reads, selection sort has a linear worst-case swap bound, while bubble and insertion can require quadratic data movement. It need not use the fewest writes on every particular input.
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
> Each shift removes one inversion, and each element costs at most one extra comparison to stop. So the running time grows with the number of elements plus the number of inversions.

```formula
T = Θ(n + I)
I = 0  ⇒  T = Θ(n)
I = n × (n − 1) / 2  ⇒  T = Θ(n^2)
I ≤ n × k  ⇒  T = O(n × (k + 1))
where
T: the running time of insertion sort, counted in comparisons plus shifts
n: the number of elements in the array
I: the number of inversions (out-of-order pairs) in the input
k: the furthest any element starts from its final sorted position, in places
Θ: Big Theta: grows exactly this fast, up to a constant factor
O: Big O: grows at most this fast, up to a constant factor
n^2: n squared, n × n
⇒: "which means"
≤: less than or equal to
In words: insertion sort pays one step per element plus one per inversion, so it is linear on sorted input, quadratic on reversed input and close to linear when every element is near its final place.
```

On the trace above, n = 6 and I = 9, so the cost is about 6 + 9 = 15 steps. The sorted case is k = 0. The bound assumes shifting one place costs constant time, which is true for arrays.

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

Here n is the number of elements and I the number of inversions in the input. All three are in-place with O(1) extra space and O(n²) average and worst case.

## Where these appear in real systems

- **Hybrid sorts.** Timsort (Python, Java objects, V8) extends short runs with binary insertion sort. C++'s `std::sort` in libstdc++ finishes with insertion sort over the nearly sorted array that introsort leaves behind. pdqsort switches to insertion sort for partitions below about 24 elements.
- **Nearly sorted data.** Maintaining a sorted list with occasional appends, or re-sorting a leaderboard after a few scores change, is close to O(n) with insertion sort.
- **Shell sort** generalises insertion sort by first sorting elements far apart (gaps like 701, 301, 132, ... 1), removing many inversions with each long move. It is still used in some embedded code because it is tiny and needs no recursion.

## Pitfalls

1. **Breaking stability by accident.** Using `>=` instead of `>` in bubble or insertion sort silently makes them unstable. Stability is a property of the implementation, not just the algorithm's name.
2. **Assuming "simple" means "fine for small inputs" without measuring what small is.** With 10,000 elements, a quadratic sort makes about 50 million comparisons (10,000 × 10,000 / 2). **Content gap:** cross-language millisecond/second timings are omitted because no reproducible benchmark, hardware or implementation was supplied.
3. **Judging by comparisons alone.** On 10,000 reversed elements, selection sort and insertion sort both make about 50 million comparisons, but insertion sort also does about 50 million writes while selection sort does at most 9,999 swaps. Which is cheaper depends on what your "write" costs.

## Key takeaways
- Any sort that only swaps adjacent elements needs at least one swap per inversion, so it needs Ω(n²) swaps on a uniformly random permutation of distinct keys. This is a lower bound, not an upper bound on every such algorithm.
- Bubble sort: stable, adaptive with an early-exit flag, but slow and plagued by "turtles".
- Selection sort: the same quadratic number of comparisons on every input, at most n−1 swaps for n elements, not stable.
- Insertion sort: stable, online, Θ(n + inversions), and often a good choice for small arrays or arrays with few inversions, which is why production hybrid sorts use it.
- Stability, in-place and adaptivity are the properties you will use to judge every other sort.

## Further reading
- [Insertion sort — Wikipedia](https://en.wikipedia.org/wiki/Insertion_sort)
- [Elementary Sorts — Algorithms, 4th ed. (Sedgewick and Wayne)](https://algs4.cs.princeton.edu/21elementary/)
- [Bubble sort — Wikipedia](https://en.wikipedia.org/wiki/Bubble_sort)
- [Selection sort — Wikipedia](https://en.wikipedia.org/wiki/Selection_sort)
- [Adaptive sort — Wikipedia](https://en.wikipedia.org/wiki/Adaptive_sort)
