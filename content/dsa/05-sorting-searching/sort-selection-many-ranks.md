---
id: sort-selection-many-ranks
title: Many ranks and running medians
level: advanced
minutes: 2
sourceLesson: sort-selection
summary: Select a prefix and sort only that prefix when ordered top-k output is required.
---

This unit builds on the preceding sorting units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

## Choosing a method

| Method | Time | Space | Use when |
|---|---|---|---|
| Sort | O(n log n) | O(n) / O(1) | Need many ranks |
| Quickselect | O(n) exp. | O(1) | Array in memory |
| Med. of medians | O(n) worst | O(n) in shown list version | Guarantee needed |
| Size-k heap | O(n log(k + 1)) | O(k) | Streams, small k |

Practical notes:

- **Many percentiles at once** (p50, p90, p99, p99.9): one sort may be convenient; repeated or multi-rank selection can avoid sorting everything. Benchmark the implementation. Streaming monitoring can instead use bounded-memory summaries such as t-digest or configured HDR Histogram, with their own accuracy/range trade-offs.
- **The k smallest, unordered** in linear time: quickselect for the last retained rank leaves the k smallest in the first k array positions (in arbitrary order). Sort just those if you need them ordered: O(n + k log k).
- **Running median of a stream**: keep two heaps, a max-heap for the lower half and a min-heap for the upper half, rebalanced so their sizes differ by at most one. Each insert is O(log n) and the median is read from the roots in O(1).

For a running median, keep every value in the lower heap no larger than every value in the upper heap. Maintain the lower heap at equal size or one larger. Insert into the appropriate side, then move a root if necessary. With an odd total, the lower root is the median; with an even total, the median convention may average the two roots. After the stream 5, 15, 1, 3, 8, the lower half is 1, 3, 5 and the upper half is 8, 15, giving median 5. Heap contents describe membership here, not their internal array order.

## Key takeaways
- Select a prefix and sort only that prefix when ordered top-k output is required.
- Two balanced heaps support a running median; several static ranks may justify sorting once.

## Further reading
- [Heap operations and top-k — Python heapq](https://docs.python.org/3/library/heapq.html)
