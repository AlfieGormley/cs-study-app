---
id: tree-heap-merging
title: Heap merging and alternative priority queues
level: intermediate
minutes: 4
sourceLesson: tree-heaps
summary: Keep only one current head from each sorted input.
---

Use the complete-tree array layout introduced earlier. The root is array slot zero; absent child positions lie beyond the occupied prefix. Here n counts binary heap entries and comparisons have constant cost. A valid min-heap makes each parent no greater than its children, without ordering siblings. Array allocation and returned output require their own cost accounting.

## Pattern: k-way merge

Merge k sorted lists (sorted runs from an external sort, per-shard query results, SSTables in LSM-tree compaction). Put the head of each list in a min-heap; repeatedly pop the smallest and push the next item from the same list.

This function uses heapq; import it as in the previous unit before running the example. The sample call returns a list; the comment shows that returned list, rather than printed script output.

```python
def merge_k(lists):
    h = []
    for i, lst in enumerate(lists):
        if lst:
            h.append((lst[0], i, 0))
    heapq.heapify(h)
    out = []
    while h:
        val, i, j = heapq.heappop(h)
        out.append(val)
        # Advance only the list just popped.
        j += 1
        if j < len(lists[i]):
            nxt = (lists[i][j], i, j)
            heapq.heappush(h, nxt)
    return out

merge_k([[1, 4, 9], [2, 3, 10], [5]])
# [1, 2, 3, 4, 5, 9, 10]
```

The binary heap never holds more than k items, one current head per list, so each of the N output items costs one pop and at most one push through a small heap of about log₂ k levels. That is O(k + N log(k + 1)) time, including scanning empty input lists, with O(k) heap space plus O(N) returned output. Two simpler alternatives are much worse when k is large: scanning all k heads to find each next item costs about k comparisons per item, and merging the lists pairwise one after another can re-copy early items about k times, up to O(N·k), N times k. `heapq.merge` is a lazy version of the heap merge.

> [!analogy] Real-world analogy: merging sorted piles of post
> Several sorters each hand you a pile of letters already in postcode order. To make one sorted stack you only ever look at the top letter of each pile: take the smallest, then reveal the next letter from that same pile.
>
> **How it maps:** each pile is a sorted input list, the visible top letters are the heap's contents (one head per list), taking the smallest is `heappop`, and revealing the next letter from that pile is the push from the same list.
>
> **Where it stops:** with three piles you can spot the smallest top letter at a glance. With a thousand piles, scanning every top would take a thousand looks per letter; the heap keeps the tops arranged so each step walks only about ten levels of the heap.

## Beyond binary heaps

- **d-ary heaps** (4-ary is common) are shallower, reducing possible upward levels but requiring more child comparisons per downward level. Cache and runtime effects depend on the implementation and workload.
- Fibonacci heaps support amortised O(1) decrease-key and O(log n) delete-min (for n queued items), giving O(E + V log V) for Dijkstra on a graph with V vertices and E edges, with suitable handles and nonnegative edge weights. Ordinary pairing heaps do not share this combined constant-amortized decrease-key guarantee; their analysis is different. Benchmark concrete implementations before choosing.
- Real uses: OS timer queues, Go's `container/heap`, Java's `PriorityQueue` (a binary heap), job schedulers, and the event queue in network simulators.

## Key takeaways
- Keep only one current head from each sorted input.
- After popping a head, advance only its input.
- Different priority queue structures trade off child comparisons and update costs.

## Further reading
- [heapq — Python docs](https://docs.python.org/3/library/heapq.html)
- [K-way merge algorithm — Wikipedia](https://en.wikipedia.org/wiki/K-way_merge_algorithm)
