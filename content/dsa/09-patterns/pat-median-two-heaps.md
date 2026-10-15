---
id: pat-median-two-heaps
title: Balance two halves around the running median
level: advanced
minutes: 5
sourceLesson: pat-heaps
summary: The lower-half maximum and upper-half minimum straddle the median.
---

Here n is the number of finite numeric observations seen so far. Values must be consistently ordered, so NaN is excluded; heap operations use amortised constant-cost comparisons.

## Pattern 3: two heaps for a running median

**Problem.** Numbers arrive one at a time. After each, report the median.

Re-sorting each time is O(n log n) per query. Instead, split the numbers into two halves:

- `lo`: a **max-heap** of the smaller half (its top is the largest small number);
- `hi`: a **min-heap** of the larger half (its top is the smallest large number).

Keep every element of `lo` no larger than every element of `hi`, and keep the sizes balanced: `len(lo)` equals `len(hi)` or exceeds it by one. Then the median sits at the tops:

```formula
m = a   if |lo| > |hi|
m = (a + b) / 2   if |lo| = |hi|
m = (3 + 5) / 2 = 4
where
m: the median of all numbers seen so far
a: the top of lo, the largest number in the smaller half
b: the top of hi, the smallest number in the larger half
|lo|: the number of items in the max-heap lo
|hi|: the number of items in the min-heap hi
In words: with an odd count, lo holds the extra item and its top is the middle value; with an even count, the median is the average of the two middle values, here 3 and 5 after adding 5, 15, 1 and 3.
```

```
  lo (max-heap)      hi (min-heap)
  [1, 3, 5]  top 5 | top 8  [8, 15]
  median = 5 (lo is bigger)
```

```python
import heapq

class MedianFinder:
    def __init__(self):
        self.lo = []   # max-heap (negated)
        self.hi = []   # min-heap

    def add(self, x):
        heapq.heappush(self.lo, -x)
        # move lo's largest across to hi
        top = -heapq.heappop(self.lo)
        heapq.heappush(self.hi, top)
        # rebalance: lo may be one bigger
        if len(self.hi) > len(self.lo):
            top = heapq.heappop(self.hi)
            heapq.heappush(self.lo, -top)

    def median(self):
        if not self.lo and not self.hi:
            raise ValueError("empty stream")
        if len(self.lo) > len(self.hi):
            return -self.lo[0]
        a, b = -self.lo[0], self.hi[0]
        # Even counts average the middle
        # values.
        return (a + b) / 2
```

Pushing through `lo` and then moving its top to `hi` guarantees the ordering invariant without any comparisons of our own; the rebalance step fixes the sizes.

```
add  lo        hi        median
5    [5]       []        5
15   [5]       [15]      10.0
1    [1,5]     [15]      5
3    [1,3]     [5,15]    4.0
8    [1,3,5]   [8,15]    5
```

Each `add` takes O(log(n + 1)) amortised heap work; `median` reads O(1) heap entries, and the two heaps together store O(n) values. The numeric example returns a floating-point mean for even sizes: very large integers can lose precision or overflow conversion, and finite floats can overflow their sum. For exact integer medians, replace `(a + b) / 2` with `Fraction(a + b, 2)` from `fractions`, accounting for integer bit costs.

The two-heaps shape also solves **IPO / maximise capital** (a min-heap of projects by cost, a max-heap of affordable profits) and, with deletion support, **sliding window median**. Naive lazy heaps may accumulate stale entries; O(k) storage and O(n log(k + 1)) total time require bounded heaps, rebuilding or indexed deletion.

## Recognising the pattern

| Cue | Pattern |
|---|---|
| "k largest/smallest/closest" | Size-k heap |
| "k-th largest in a stream" | Size-k min-heap |
| "top k frequent" | Counter + heap/buckets |
| "merge k sorted" | Heap of heads |
| "k-th smallest in sorted matrix" | K-way merge |
| "median of a stream" | Two heaps |
| Repeatedly take the best option | Heap (greedy) |

## Pitfalls

- **Wrong heap direction.** k largest → min-heap of size k; k smallest → max-heap of size k.
- **Comparing uncomparable items.** `(5, node_a)` vs `(5, node_b)` raises `TypeError` when the priorities tie; add an index.
- **Forgetting to negate back** when using `-x` for a max-heap.
- **Assuming the heap list is sorted.** Only `h[0]` is guaranteed; the rest is in heap order.
- **Integer vs float medians.** The even case returns an average, which may need to be a float.

## Recap of the pattern family
- A size-k min-heap keeps the k largest of n items in O(n log(k + 1)) time and O(k) space (for k from 1 to n), and works on streams.
- K-way merge holds one head per list in a heap: O(k + N log(N_nonempty + 1)) for N_nonempty nonempty inputs, a technique behind external sorting and LSM compaction.
- Two heaps (max-heap of the low half, min-heap of the high half) give a running median with O(log(n + 1)) amortised inserts.
- Python's `heapq` is a min-heap; negate for max, and use tie-breakers in tuples.
- Quickselect finds a one-off k-th element in O(n) average when all data is in memory.

## Key takeaways
- The lower-half maximum and upper-half minimum straddle the median.
- Preserve both ordering and the size difference of at most one.
- Even medians use a mean; numeric accuracy and empty-stream behavior need explicit handling.

## Further reading
- [heapq — Python docs](https://docs.python.org/3/library/heapq.html)
- [Heap cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/heap/)
- [Heap (data structure) — Wikipedia](https://en.wikipedia.org/wiki/Heap_(data_structure))
- [K-way merge algorithm — Wikipedia](https://en.wikipedia.org/wiki/K-way_merge_algorithm)
- [Quickselect — Wikipedia](https://en.wikipedia.org/wiki/Quickselect)
