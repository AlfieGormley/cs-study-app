---
id: lin-queue-priority-ties
title: Priority queues, heap costs and tie-breaking
level: advanced
minutes: 4
sourceLesson: lin-queues
summary: A heap serves the best key rather than the earliest arrival.
---

A FIFO queue serves by arrival time. A priority queue instead serves by an ordering key. Here n is the number of queued items, and the complexity model assumes constant-time key comparisons; expensive comparisons add their own cost.

## Priority queues

Sometimes "first come, first served" is wrong. An emergency department treats the most urgent patient first; an OS scheduler runs the highest-priority thread. A **priority queue** always removes the item with the **best priority** (smallest or largest key), whenever it arrived.

For a queue holding n items, simple implementations make one operation slow. For the sorted-array row, keep descending order and remove the minimum at the end without shifting; insertion bounds are amortised over backing growth. In the table, log n means log₂ n, the number of times n can be halved before reaching 1: about 20 for a million items, so O(log n) operations stay cheap even for huge queues.

| Implementation | insert | remove-min |
|---|---|---|
| Unsorted array | O(1) | O(n) |
| Sorted array | O(n) | O(1) |
| Binary heap | O(log n) | O(log n) |

The **binary heap** balances both, and also gives O(1) peek and O(n) construction from an existing list. How it works (a tree packed into an array) is covered in the heaps module; for now, use the library.

```python
import heapq
h = []
heapq.heappush(h, (2, "write report"))
heapq.heappush(h, (1, "fix outage"))
heapq.heappush(h, (3, "lunch"))
heapq.heappop(h)  # (1, 'fix outage')
```

Practical details:

- The traditional heapq functions use a min-heap on a list. Python 3.14 adds public max-heap functions such as heappush_max and heappop_max; on older versions, negate numeric keys.
- With `(priority, item)` tuples, equal priorities fall back to comparing the items, which fails with a `TypeError` for dicts and other non-comparable objects (and, for comparable items, silently orders ties by the item rather than by arrival). Add a counter: `(priority, next(counter), item)`.
- Java's `PriorityQueue` is also a min-heap by default; pass a `Comparator` for other orders. Its iterator does **not** visit items in priority order.
- Uses include Dijkstra's shortest paths, event-driven simulations, schedulers, merging k sorted lists and keeping the top k items.

### Model a complete insert-and-drain workload

Picture a million inserts followed by a million remove-min operations, with keys arriving in random order. A descending sorted array must shift, on average, about half of the items already stored for every insert, so the shifting adds up quadratically: hundreds of billions of moves at this size. An unsorted array is just as bad the other way round, scanning every remaining item on each remove-min. A binary heap does a logarithmic number of tree-level steps per operation, about twenty for a million items, so the whole workload is O(n log n), where n is the number of items: tens of millions of steps.

Those are different abstract operations, so their ratio is not a measured speedup. A heap pop may compare children and the replacement item at each level, and the model does not count every comparison exactly. If all items are available before processing starts, bulk heapify builds the heap in linear time, which changes the workload.

## Key takeaways
- A heap serves the best key rather than the earliest arrival.
- Add a unique sequence counter when payloads cannot be compared.

## Further reading
- [heapq — Python docs](https://docs.python.org/3/library/heapq.html)
- [PriorityQueue — Java SE 21 API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/PriorityQueue.html)
