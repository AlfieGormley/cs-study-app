---
id: sort-stream-top-k-heaps
title: Keeping top-k from a stream
level: advanced
minutes: 4
sourceLesson: sort-selection
summary: For the smallest values, keep a max-heap whose root is the worst retained item.
---

This unit builds on the preceding sorting units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

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
        # The root is the worst retained
        # item.
        elif x < -heap[0]:
            # Replace it only with a better
            # newcomer.
            heapq.heapreplace(heap, -x)
    # Undo negation and order the retained
    # keys.
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

- **Time:** O(n log(k + 1)). Each element costs at most one O(log k) heap operation, and once the heap holds good values, most elements are rejected by a single comparison with the root. The "+ 1" only keeps the bound sensible for one retained item, where its logarithm would otherwise be zero.

```formula
T = O(n log(k + 1))
n log_2(k + 1) ≈ 10^6 × 6.66 ≈ 6.7 × 10^6
where
T: the worst-case running time of the size-k heap method
n: the number of elements read from the stream; a million (10^6) here
k: how many smallest elements to keep; 100 here
log_2(k + 1): the base-2 logarithm of k + 1, roughly the height of the heap; log_2(101) ≈ 6.66
log: the logarithm (the base only changes a constant)
O: Big O: grows at most this fast, up to a constant factor
≈: approximately equal to
In words: each item can travel down a logarithmic-height heap. The 6.7-million figure is a growth proxy, not a bound on literal executed instructions or measured time.
```

- **Space:** O(k), independent of n. It works on a stream you cannot store: the 100 smallest response-time records from a stream. Ranking query frequencies additionally needs counting or a frequency sketch.

Python's `heapq.nsmallest(k, it)` and `nlargest` implement this. C++'s `std::partial_sort` puts the k smallest at the front in order. A heap is a common implementation; the standard specifies the result and comparison bound, not that algorithm.

An alternative is to heapify the whole array in O(n) and pop k times: O(n + k log n). That is fast for small k, but it needs all the data in memory and rearranges it.

## Key takeaways
- For the smallest values, keep a max-heap whose root is the worst retained item.
- A fixed-size heap processes the stream in bounded memory and rejects worse newcomers cheaply.

## Further reading
- [Heap operations and top-k — Python heapq](https://docs.python.org/3/library/heapq.html)
