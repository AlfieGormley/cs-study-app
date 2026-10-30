---
id: tree-python-top-k
title: Python priority queues and streaming top-k
level: intermediate
minutes: 5
sourceLesson: tree-heaps
summary: Use an insertion counter to break equal-priority payload ties.
---

Use the complete-tree array layout introduced earlier. The root is array slot zero; absent child positions lie beyond the occupied prefix. Here n counts binary heap entries and comparisons have constant cost. A valid min-heap makes each parent no greater than its children, without ordering siblings. Array allocation and returned output require their own cost accounting.

## heapq in Python

Python's `heapq` module implements a **min-heap on a plain list**. There is no binary heap class.

Here n is the number of items in the binary heap (or in the input, for `heapify` and `nlargest`), and k is how many items you ask for.

| Function | Cost |
|---|---|
| `heappush(h, x)` | O(log n) |
| `heappop(h)` | O(log n) |
| `h[0]` (peek) | O(1) |
| `heapify(h)` | O(n), in place |
| `heapreplace(h, x)` | pop then push, O(log n) |
| `heappushpop(h, x)` | push then pop, O(log n) |
| `nlargest(k, it)` | O(n log(k + 1)) when k is between 1 and n; implementation may choose max or sorting |

Practical details:

- **Max-heaps**: before Python 3.14, negate the keys (`heappush(h, -x)`). Python 3.14 added `heapify_max`, `heappush_max`, `heappop_max` and friends.
- **Priorities with payloads**: push tuples `(priority, item)`. If two priorities tie, Python compares the items, which fails for objects that don't support `<`. Add a counter: `(priority, next(counter), item)`. This also makes ties first-in-first-out.
- **Changing a priority** ("decrease-key") is not supported. The usual trick is **lazy deletion**: push a new entry and mark the old one as removed, skipping stale entries when they are popped. Dijkstra's algorithm in Python is normally written this way.

## Pattern: top-k

"Find the k largest of n items" (top 10 search results, the 100 busiest IPs in a log). Sorting is O(n log n). Better: keep a **min-heap of size k** holding the best k seen so far. Its root is the *weakest* of the current top k, so each new item only needs comparing with the root.

```python
import heapq

def top_k(nums, k):
    if not isinstance(k, int) or k < 0:
        raise ValueError("k must be >= 0")
    if k == 0:
        return []
    h = []
    for x in nums:
        if len(h) < k:
            heapq.heappush(h, x)
        # Replace only the weakest
        # kept value.
        elif x > h[0]:
            heapq.heapreplace(h, x)
    return sorted(h, reverse=True)

top_k([5, 1, 9, 3, 7, 9, 2, 8], 3)
# [9, 9, 8]
```

Each item costs one comparison with the root, and at most one replace that sifts through a binary heap of only k items. Many items fail that first comparison and cost nothing more. So the worst case is O(n log(k + 1)) time, including the final sort of the k keepers, and O(k) memory (the + 1 just keeps the logarithm above zero when k is 1). Larger k returns all n items; zero keepers returns immediately.

With a billion log lines and 100 keepers, that is at most about 7 heap levels per item instead of the 30 a heap of all n items would need, and it works on a stream that never fits in memory. `heapq.nlargest` does this for you.

> [!analogy] Real-world analogy: a door policy at a full venue
> A small venue holds exactly 100 people. Once it is full, the door staff let a newcomer in only if they beat the least impressive person currently inside, who is then asked to leave. The staff never need to compare a newcomer with anyone except that one weakest guest.
>
> **How it maps:** the venue is the min-heap of size k, the weakest guest is the root `h[0]`, the comparison at the door is `x > h[0]`, and the swap is `heapreplace`. Everyone turned away costs one comparison.
>
> **Where it stops:** door staff could simply know who is weakest. A heap must do a few swaps after each replacement, about log₂ k of them, to bring the next weakest keeper to the root.

> [!tip] Min-heap for the largest, max-heap for the smallest
> It feels backwards, but for the k **largest** you want quick access to the **smallest** of your keepers, because that is the one a newcomer must beat.

If all n items are in memory and you only need the k-th element, **quickselect** finds it in expected O(n), but it does not stream and reorders the array.

## Key takeaways
- Use an insertion counter to break equal-priority payload ties.
- A min-heap retains the largest stream items by exposing its weakest keeper.
- Changing priorities requires an extra policy such as lazy deletion.

## Further reading
- [heapq — Python docs](https://docs.python.org/3/library/heapq.html)
