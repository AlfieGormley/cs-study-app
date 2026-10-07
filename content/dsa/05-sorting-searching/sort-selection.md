---
id: sort-selection
title: Selection: quickselect, median of medians and heaps
level: advanced
minutes: 14
summary: Finding the k-th smallest element without sorting, in expected O(n) with quickselect, worst-case O(n) with median of medians, and O(n log(k + 1)) with a heap for top-k and streams.
---

Many questions that sound like sorting are really **selection**: find the median latency, the 99th percentile, the 10 highest-scoring posts, the k nearest points. You need one element (or k elements) in the right place, not the whole array ordered.

Sorting answers all of these in O(n log n). But selection can be done in **O(n)**, and top-k in **O(n log(k + 1))**. At a billion items, log₂ n is about thirty; this compares asymptotic growth, not literal pass counts or measured runtime.

Throughout, "k-th smallest" is 0-based: k = 0 is the minimum, k = n − 1 the maximum, k = n // 2 the (upper) median.

## The easy cases

- **Minimum or maximum**: one pass, n − 1 comparisons. That is optimal: every element except the winner must lose at least one comparison.
- **Min and max together**: compare elements in pairs, then the smaller with the current min and the larger with the current max. That is about 3n/2 comparisons instead of 2n.
- **Second smallest**: a knockout tournament finds it in n + ⌈log₂ n⌉ − 2 comparisons: the runner-up must have lost directly to the winner.

The general k is where it gets interesting.

## Quickselect

Hoare's **quickselect** (1961) is quicksort that only recurses into **one side**. Partition around a pivot. The pivot lands at its final index p. If k == p, done. If k < p, the answer is on the left; otherwise it is on the right. Throw the other side away.

```python
import random

def quickselect(a, k):
    if not 0 <= k < len(a):
        raise IndexError(
            "rank out of range"
        )
    lo, hi = 0, len(a) - 1
    while True:
        if lo == hi:
            return a[lo]
        r = random.randint(lo, hi)
        a[r], a[hi] = a[hi], a[r]
        p = lomuto(a, lo, hi)
        if k == p:
            return a[p]
        if k < p:
            hi = p - 1
        else:
            lo = p + 1
```

(`lomuto` is the partition from the quicksort lesson.) This compact version has the expected linear guarantee for distinct keys. With duplicates, random pivots alone do not prevent quadratic time on all-equal input; use a three-way partition and discard the entire equal block for a duplicate-robust version. Because only one side survives, recursion becomes a loop.

Trace with the last element as pivot (no randomisation, to keep it readable), finding k = 5 in `[7, 2, 1, 6, 8, 5, 3, 4]`:

```
pivot 4: [2,1,3,4,8,5,7,6]  p=3
k=5 > 3: keep a[4..7] = [8,5,7,6]
pivot 6: [5,6,7,8]          p=5
k == p: answer 6
```

Check: sorted, the array is `[1, 2, 3, 4, 5, 6, 7, 8]` and index 5 is 6.

### Why it is expected O(n)

With a good pivot, each round discards a constant fraction. If every pivot split the array in half, the work would be

```
n + n/2 + n/4 + ...  <=  2n
```

A geometric series, so linear. For distinct keys, with random pivots the splits are not exactly half, but the pivot lands in the middle 50% of the range with probability 1/2, and then at least a quarter is discarded. The expected cost is still a geometric series: **O(n)**. A more careful analysis gives about 3.4n expected comparisons for the median (2(1 + ln 2)n), and fewer for k near the ends.

### The worst case

Bad pivots every round shrink the range by only one element: n + (n − 1) + ... = **O(n²)**, exactly like quicksort. With a first- or last-element pivot, a sorted input does this. Random pivots make it vanishingly unlikely, but not impossible, and an adversary who can predict your random number generator can still force it.

## Median of medians: worst-case O(n)

In 1973 Blum, Floyd, Pratt, Rivest and Tarjan showed that selection can be done in O(n) **guaranteed**. The trick is to spend a little linear work finding a pivot that is provably not too far from the middle.

1. Split the array into groups of 5.
2. Find the median of each group (constant work per group).
3. **Recursively** select the median of those n/5 medians. Use it as the pivot.
4. Partition and recurse into the side containing k.

```python
def select(a, k):
    if not 0 <= k < len(a):
        raise IndexError(
            "rank out of range"
        )
    if len(a) <= 5:
        return sorted(a)[k]
    groups = [a[i:i + 5]
              for i in range(0, len(a), 5)]
    medians = [sorted(g)[len(g) // 2]
               for g in groups]
    mid = len(medians) // 2
    pivot = select(medians, mid)
    lows = [x for x in a if x < pivot]
    highs = [x for x in a if x > pivot]
    n_eq = len(a) - len(lows) - len(highs)
    if k < len(lows):
        return select(lows, k)
    if k < len(lows) + n_eq:
        return pivot
    return select(highs,
                  k - len(lows) - n_eq)
```

### Why the pivot is good

Picture the groups as columns, each sorted with its median in the middle row, and the columns ordered by their medians. M is the median of medians.

```
 smaller medians    larger medians
   .  .  .  |  .  .  .
   .  .  .  |  .  .  .
   m  m  m  M  m  m  m
   .  .  .  |  .  .  .
   .  .  .  |  .  .  .
```

Half of the medians are ≤ M. Each of those medians has two more elements in its group below it. So at least 3 elements in each of about half the n/5 groups are ≤ M: roughly **3n/10** elements are ≤ M, and by symmetry roughly 3n/10 are ≥ M. (Precisely, at least 3n/10 − 6 after accounting for the ragged last group and M's own group.)

So the recursive call in step 4 is on at most about **7n/10** elements. The recurrence is:

```
T(n) <= T(n/5) + T(7n/10) + O(n)
```

Since 1/5 + 7/10 = 9/10 < 1, the total work at each level of recursion shrinks geometrically, and **T(n) = O(n)**.

> [!note] Why groups of 5?
> With groups of 3, the guarantee is only about n/3 on each side, giving the upper-bound recurrence T(n) ≤ T(n/3) + T(2n/3) + O(n). This analysis establishes only O(n log n), not a matching lower bound. Five is the smallest odd group size giving linear time by this simple argument; other algorithms can use repeated grouping or different methods.

### Practical costs and hybrids

The constant factor is large: sorting every group of 5, the extra recursive call and the partition add up to extra work compared with classical randomized selection; exact constants depend on the implementation, and the list-building version above also allocates heavily. So in practice median of medians is a **fallback**, not a default:

- **Introselect** (Musser, 1997) runs quickselect, and if it is not shrinking the range fast enough, switches to a fallback. A carefully budgeted linear-time fallback gives a linear worst-case bound; a heap fallback may give O(n log n). C++ requires only average linear complexity for ordinary std::nth_element and does not mandate an algorithm. NumPy documents O(n) worst-case introselect.
- **Floyd–Rivest** (1975) picks the pivot from a small random sample and achieves about n + min(k, n − k) comparisons expected, close to the theoretical optimum. It is used for large in-memory selection.

## The k smallest with a heap

Quickselect needs the whole array in memory and rearranges it. For **top-k from a stream**, or when k is much smaller than n, a **heap** is the better tool (heap operations are covered in the trees module).

To keep the k smallest seen so far, keep a **max-heap of size k**. Its root is the largest of your current best k: the one to throw out when something smaller arrives.

```python
import heapq

def k_smallest(nums, k):
    if k < 0:
        raise ValueError("k >= 0")
    if k == 0:
        return []
    heap = []   # max-heap via negation
    for x in nums:
        if len(heap) < k:
            heapq.heappush(heap, -x)
        elif x < -heap[0]:
            heapq.heapreplace(heap, -x)
    return sorted(-x for x in heap)
```

Trace for k = 3 over `[9, 1, 8, 2, 7, 3, 6, 4, 5]`:

```
9 -> {9}
1 -> {1, 9}
8 -> {1, 8, 9}
2 -> 2 < 9: drop 9 -> {1, 2, 8}
7 -> 7 < 8: drop 8 -> {1, 2, 7}
3 -> 3 < 7: drop 7 -> {1, 2, 3}
6, 4, 5 -> not < 3: ignored
result [1, 2, 3]
```

The counter-intuitive part: to find the **smallest** k, use a **max**-heap; to find the **largest** k, use a **min**-heap. The root is the gatekeeper for "worst of the best".

- **Time:** O(n log(k + 1)). Each element costs at most one O(log k) heap operation, and once the heap holds good values, most elements are rejected by a single comparison with the root.
- **Space:** O(k), independent of n. It works on a stream you cannot store: the 100 smallest response-time records from a stream. Ranking query frequencies additionally needs counting or a frequency sketch.

Python's `heapq.nsmallest(k, it)` and `nlargest` implement this. C++'s `std::partial_sort` uses the same heap idea to put the k smallest at the front, in order.

An alternative is to heapify the whole array in O(n) and pop k times: O(n + k log n). That is fast for small k, but it needs all the data in memory and rearranges it.

## Choosing a method

| Method | Time | Space | Use when |
|---|---|---|---|
| Sort | O(n log n) | O(n) / O(1) | Need many ranks |
| Quickselect | O(n) exp. | O(1) | Array in memory |
| Med. of medians | O(n) worst | O(n) in shown list version | Guarantee needed |
| Size-k heap | O(n log(k + 1)) | O(k) | Streams, small k |

Practical notes:

- **Many percentiles at once** (p50, p90, p99, p99.9): one sort may be convenient; repeated or multi-rank selection can avoid sorting everything. Benchmark the implementation. Streaming monitoring can instead use bounded-memory summaries such as t-digest or configured HDR Histogram, with their own accuracy/range trade-offs.
- **The k smallest, unordered** in linear time: quickselect for index k − 1 leaves the k smallest in `a[0..k−1]` (in arbitrary order). Sort just those if you need them ordered: O(n + k log k).
- **Running median of a stream**: keep two heaps, a max-heap for the lower half and a min-heap for the upper half, rebalanced so their sizes differ by at most one. Each insert is O(log n) and the median is read from the roots in O(1).

## Key takeaways
- Selection finds the k-th smallest without sorting; minimum and maximum take n − 1 comparisons.
- Quickselect partitions and keeps only the side containing k: expected O(n) (about 3.4n comparisons for the median), worst case O(n²).
- Median of medians (groups of 5) guarantees a pivot with about 3n/10 elements on each side, giving T(n) ≤ T(n/5) + T(7n/10) + O(n) = O(n), with implementation-dependent overhead; it is one possible introselect fallback.
- For top-k, keep a size-k heap of the opposite kind (max-heap for the smallest k): O(n log(k + 1)) time and O(k) memory, which works on streams.
- C++ std::nth_element promises average linear selection; NumPy np.partition documents worst-case linear introselect; `heapq.nsmallest` and `std::partial_sort` use heaps.

## Further reading
- [Quickselect — Wikipedia](https://en.wikipedia.org/wiki/Quickselect)
- [Median of medians — Wikipedia](https://en.wikipedia.org/wiki/Median_of_medians)
- [Selection algorithm — Wikipedia](https://en.wikipedia.org/wiki/Selection_algorithm)
- [Floyd–Rivest algorithm — Wikipedia](https://en.wikipedia.org/wiki/Floyd%E2%80%93Rivest_algorithm)
- [heapq — Python docs](https://docs.python.org/3/library/heapq.html)
- [std::nth_element — cppreference](https://en.cppreference.com/w/cpp/algorithm/nth_element)
