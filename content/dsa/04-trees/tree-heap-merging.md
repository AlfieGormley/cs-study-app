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

The binary heap never holds more than k items, so each of the N output items costs one pop and at most one push through a small binary heap:

```formula
W ≈ k + N × log_2(k + 1)
W ≈ 3 + 7 log_2(3 + 1)
W ≈ 3 + 7 × 2 = 17
W_pair ≈ N × k
where
W: the work for the heap merge, counted in list visits plus heap levels sifted
k: the number of sorted input lists; 3 in the example above
N: the total number of items across all the lists; 7 in the example
log_2(k + 1): the base-2 logarithm of k + 1, about the number of levels in a heap of k items
W_pair: the work, up to a constant factor, for merging the lists one after another instead
≈: approximately equal to (these are growth estimates, not exact counts)
In words: the heap merge visits every list once and then pays about log_2(k) heap levels per output item; merging lists one by one can re-copy items about k times.
```

So the binary heap merge costs O(k + N log(k + 1)), including scanning empty input lists, with O(k) binary heap space plus O(N) returned output. Merging the lists pairwise one after another would cost up to O(N·k), N times k. `heapq.merge` is a lazy version of this.

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
