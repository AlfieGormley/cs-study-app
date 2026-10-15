---
id: pat-merge-heads
title: Merge sorted streams through their current heads
level: advanced
minutes: 4
sourceLesson: pat-heaps
summary: Keep one current head per nonempty input list.
---

Here k is the number of sorted input lists, N_nonempty the number of nonempty lists and N their total element count. Numeric comparisons and list indexing have constant cost.

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

Let N_nonempty be the number of nonempty lists. Inspecting all k inputs and heapifying their heads costs O(k); each of the N outputs then costs one pop and at most one push on a heap of at most N_nonempty heads:

```formula
T = O(k + N log(N_nonempty + 1))
N log_2(N_nonempty) ≈ 10^6 × 6.6
N log_2(N_nonempty) ≈ 6.6 × 10^6
Nk = 10^6 × 100 = 10^8
where
T: the total running time of the heap merge
O(…): Big-O, the growth rate of the cost, ignoring constant factors
k: the number of input lists; here 100
N_nonempty: the number of nonempty input lists, at most k; here 100
N: the total number of elements across all lists; here 10^6
log: logarithm; its base doesn't matter inside Big-O
log_2: the base-2 logarithm; log_2(100) ≈ 6.6
≈: approximately equal to
In words: the logarithmic expression for a million outputs and 100 heads is about 6.6 million, against a 100-million expression for scanning all heads. These are growth-expression values: each output can involve both a pop and a push, with implementation-dependent comparison counts.
```

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
