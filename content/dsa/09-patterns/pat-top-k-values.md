---
id: pat-top-k-values
title: Retain the strongest values in a size-budget heap
level: advanced
minutes: 4
sourceLesson: pat-heaps
summary: For the largest values, the minimum root is the weakest retained member.
---

Here n is the number of scored numeric inputs and k is the requested number to keep. Comparisons have constant cost; values must provide consistent ordering.

## Pattern 1: top-K

**Problem.** Find the k largest elements of n (or the k-th largest).

Options:

| Approach | Time | Extra space |
|---|---|---|
| Sort, take last k | O(n log n) | Python sort: O(n) auxiliary, plus output |
| Min-heap of size k | O(n log(k + 1)) | O(k) |
| Max-heapify all, pop k | O(n + k log(n + 1)) | O(n) storage; O(1) heapify auxiliary |
| Randomised quickselect | O(n) expected | O(1) auxiliary with iterative in-place partition |

To see why the size-k heap pays off when k is much smaller than n, compare the dominant terms:

```formula
W_sort ≈ n log_2(n)
W_heap ≈ n log_2(k)
W_sort ≈ 10^6 × 20 = 2 × 10^7
W_heap ≈ 10^6 × 3.3 ≈ 3.3 × 10^6
where
W_sort: an illustrative comparison-growth expression for sorting all n items, not an exact comparison count
W_heap: an illustrative logarithmic-work expression for scanning n values with a size-k min-heap; replacements and actual comparisons depend on input and implementation
n: the number of items; here 10^6
k: how many of the largest items you want; here 10
log_2: the base-2 logarithm, the number of halvings from the argument down to 1; log_2(10^6) ≈ 20 and log_2(10) ≈ 3.3
≈: approximately equal to
In words: each heap operation only climbs a tree log_2(k) levels deep instead of log_2(n), so for the top 10 of a million items these two expressions have a ratio of about six; the size-k heap holds only 10 candidate items. This ratio is not an actual comparison count or measured speedup.
```

These are rough counts that ignore constant factors; the memory saving (k items instead of n) is often the bigger win.

The size-k heap is a standard option. The counter-intuitive part: to keep the k **largest**, use a **min**-heap. Its root is the smallest of your current top k, the "weakest member", which is exactly what a newcomer must beat.

```python
import heapq

def top_k(nums, k):
    if type(k) is not int or k < 0:
        raise ValueError("nonnegative k")
    if k == 0:
        return []
    heap = []
    for x in nums:
        if len(heap) < k:
            heapq.heappush(heap, x)
        elif x > heap[0]:
            # Replace the weakest retained
            # value.
            heapq.heapreplace(heap, x)
    return heap    # up to k largest values
```

```
nums = [3, 2, 1, 5, 6, 4], k = 2
3  heap [3]
2  heap [2,3]
1  1 < 2: ignore
5  5 > 2: replace -> [3,5]
6  6 > 3: replace -> [5,6]
4  4 < 5: ignore
2nd largest = heap[0] = 5
```

> [!note] Quickselect
> Quickselect partitions like quicksort but recurses into only the side containing the k-th position: expected O(n) with independent random pivots, O(n²) worst case for ordinary quickselect. It is a useful option for a one-off order statistic, but universal speed claims require benchmarks. The usual in-place implementation needs the array resident and reorders it.

## Key takeaways
- For the largest values, the minimum root is the weakest retained member.
- The result is heap-ordered rather than sorted and may have fewer values than the requested budget.
- Quickselect suits a one-off resident order statistic; a small heap supports streams.

## Further reading
- [heapq — Python docs](https://docs.python.org/3/library/heapq.html)
- [Heap cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/heap/)
- [Heap (data structure) — Wikipedia](https://en.wikipedia.org/wiki/Heap_(data_structure))
- [K-way merge algorithm — Wikipedia](https://en.wikipedia.org/wiki/K-way_merge_algorithm)
- [Quickselect — Wikipedia](https://en.wikipedia.org/wiki/Quickselect)
