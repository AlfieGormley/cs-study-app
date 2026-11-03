---
id: pat-merge-heads
title: Merge sorted streams through their current heads
level: advanced
minutes: 4
sourceLesson: pat-heaps
summary: Keep one current head per nonempty input list.
---

Here k is the number of sorted input lists, N_nonempty the number of nonempty lists and N their total element count. Numeric comparisons and list indexing have constant cost. The Trees & Heaps module's "Heap merging and alternative priority queues" unit introduces this merge; this unit focuses on its cost and where it shows up.

## Pattern 2: k-way merge

**Problem.** Merge k sorted lists (total N elements) into one sorted list.

At every step, the next output element is the smallest among the k list **heads**. A heap of those heads finds it in O(log(k + 1)), not O(k).

```python
import heapq

def merge_k(lists):
    heap = []
    for i, lst in enumerate(lists):
        if lst:
            heap.append((lst[0], i, 0))
    # Build once from all nonempty list
    # heads.
    heapq.heapify(heap)
    out = []
    while heap:
        # Take the smallest current input
        # head.
        val, i, j = heapq.heappop(heap)
        out.append(val)
        if j + 1 < len(lists[i]):
            item = (lists[i][j+1], i, j + 1)
            # Advance only the input just
            # consumed.
            heapq.heappush(heap, item)
    return out
```

```
lists: [1,4,5] [1,3,4] [2,6]
heap heads: (1,L0) (1,L1) (2,L2)
pop 1 (L0) push 4   out [1]
pop 1 (L1) push 3   out [1,1]
pop 2 (L2) push 6   out [1,1,2]
pop 3 (L1) push 4   ...
final: [1,1,2,3,4,4,5,6]
```

Inspecting all k inputs and heapifying their heads costs O(k). Each of the N outputs then costs one pop and at most one push on a heap that never holds more than one head per nonempty list. Scanning all k heads for every output would instead cost O(k) per element: for a million elements from 100 lists, that is a growth figure of about 100 million against roughly 7 million for the heap.

So total time is O(k + N log(N_nonempty + 1)), with O(N_nonempty) heap space plus O(N) returned output. Concatenating and a generic comparison sort has an O(N log N) bound, but adaptive sorting can exploit the k existing runs. Sequentially merging into a growing result has O(Nk) worst-case movement.

The list index `i` in the tuple breaks ties and tells us which list to advance. Python ships this as `heapq.merge(*lists)`, which is lazy.

> [!example] Where this runs in production
> External sorting (sorting files bigger than RAM) sorts chunks that fit in memory, writes them as sorted "runs", then k-way merges the runs. LSM-tree databases such as RocksDB and Cassandra do the same during **compaction**, merging sorted SSTable streams, often writing multiple output SSTables and applying version/tombstone rules.

Related problems: "k-th smallest element in a sorted matrix" (rows are sorted lists; pop k times), "smallest range covering one element from each of k lists" (track the max of the heads alongside the heap's min).

## Key takeaways
- Keep one current head per nonempty input list.
- A list identifier breaks equal-priority ties and selects which input to advance.
- Account for inspecting empty inputs and storing the returned result.

## Further reading
- [heapq — Python docs](https://docs.python.org/3/library/heapq.html)
- [Heap cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/algorithms/heap/)
- [Heap (data structure) — Wikipedia](https://en.wikipedia.org/wiki/Heap_(data_structure))
- [K-way merge algorithm — Wikipedia](https://en.wikipedia.org/wiki/K-way_merge_algorithm)
- [Quickselect — Wikipedia](https://en.wikipedia.org/wiki/Quickselect)
