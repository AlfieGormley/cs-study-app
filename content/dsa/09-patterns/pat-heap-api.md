---
id: pat-heap-api
title: Use heap roots and safe priority tuples
level: advanced
minutes: 3
sourceLesson: pat-heaps
summary: A min-heap exposes its minimum at the root without sorting every element.
---

A binary heap gives you the minimum (or maximum) of a changing collection in O(1), and inserts or removes the root in O(log(n + 1)) heap comparisons, where n is the number of items in the heap. The log is there because a heap is a balanced tree a number of levels logarithmic in its size, and an insert or removal walks one path from top to bottom; the + 1 just keeps the bound meaningful when n is 0 or 1. Removing an arbitrary item needs a way to locate it. Python list resizing makes individual operations occasionally linear; the standard bound is amortised and assumes constant-cost comparisons. Many problems that look like "sort everything" only need the *best few* items, or the *current* best, and a heap can avoid sorting the entire collection.

The following units develop three patterns built on that one idea.

```
Top-K        keep a heap of size k
K-way merge  heap holds one head per list
Two heaps    max-heap | min-heap around
             the median
```

## Python's heapq in 60 seconds

`heapq` turns a plain list into a **min-heap**: `h[0]` is always the smallest. In the table, n is the number of items in the heap (or in the input iterable `it`), and k is how many items you ask for.

| Call | Cost |
|---|---|
| `heappush(h, x)` | O(log(n + 1)) |
| `heappop(h)` | O(log(n + 1)) |
| `h[0]` (peek) | O(1) |
| `heapreplace(h, x)` | O(log(n + 1)): pop, then push |
| `heapify(h)` | O(n) |
| `nlargest(k, it)` | O(n log(k + 1)), k from 1 to n |

Python 3.14 provides public max-heap functions such as `heapify_max` and `heappush_max`. The examples use the older-compatible **negation** technique for ordered numeric values: push `-x`, and `-h[0]` is the maximum. NaN values are excluded because they do not provide the required ordering.

Tuples compare element by element, so `(priority, item)` works. If priorities can tie and the items aren't comparable (say, linked-list nodes), add a tie-breaking counter: `(priority, i, item)`.

## Key takeaways
- A min-heap exposes its minimum at the root without sorting every element.
- Heapify builds bottom-up in linear time.
- A unique tie-breaker avoids comparing non-comparable records.

## Further reading
- [heapq — Python docs](https://docs.python.org/3/library/heapq.html)
- [Heap cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/heap/)
- [Heap (data structure) — Wikipedia](https://en.wikipedia.org/wiki/Heap_(data_structure))
- [K-way merge algorithm — Wikipedia](https://en.wikipedia.org/wiki/K-way_merge_algorithm)
- [Quickselect — Wikipedia](https://en.wikipedia.org/wiki/Quickselect)
