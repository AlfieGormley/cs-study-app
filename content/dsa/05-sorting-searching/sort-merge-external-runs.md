---
id: sort-merge-external-runs
title: External sorting with bounded memory
level: basic
minutes: 3
sourceLesson: sort-merge
summary: Generate sorted runs, then merge their buffered fronts with a heap.
---

This unit builds on the preceding sorting units. Here n is the number of input elements; Big O bounds growth up to a constant factor, and logarithms are base two unless stated otherwise.

## External sorting: data bigger than memory

Suppose you must sort 100 GB of records on a machine with 1 GB of RAM. You cannot load it all, and random access to disk is slow. Merge sort's sequential access pattern makes it the natural fit.

**Phase 1: run generation.** For a simplified example, reserve 1 GB for sortable records with additional memory available for overhead, sort each chunk, and write it as a sorted **run**. That gives 100 runs. On a machine with only 1 GB total, choose smaller chunks and expect more runs.

**Phase 2: k-way merge.** Open all 100 runs at once. Give each a small input buffer (say 8 MB each, reserving the remaining memory for output, heap and process overhead) and repeatedly output the smallest front element. With k runs (here k = 100), finding the smallest of the k fronts efficiently uses a **min-heap** of size k (covered in the trees module), costing O(log k) per element.

```
run 1 [buffer] \
run 2 [buffer]  \
  ...            > min-heap -> output
run 100 [buffer]/
```

The arithmetic of the plan:

```formula
r = D / M = 100 GB / 1 GB = 100
B = r × 8 MB = 800 MB
where
r: the number of sorted runs phase 1 produces
D: the total size of the data, here 100 gigabytes
M: the memory used to sort each chunk, here 1 gigabyte
B: the total memory phase 2 spends on input buffers, one per run
GB: gigabyte, 1,000,000,000 bytes
MB: megabyte, 1,000,000 bytes
In words: 100 GB sorted 1 GB at a time gives 100 runs, and 100 input buffers of 8 MB need 800 MB in the merge phase.
```

Total: every record is read and written twice (once per phase), all sequentially. If there are too many runs to merge in one go, you merge in several passes, each multiplying run length by k.

> [!example] PostgreSQL does exactly this
> When a sort needs more memory than `work_mem` (default 4 MB), PostgreSQL switches to an external merge sort using temporary files. `EXPLAIN ANALYZE` shows `Sort Method: external merge  Disk: ...` instead of `quicksort  Memory: ...`. Raising `work_mem` for a big reporting query can keep the sort in memory.

The same pattern appears in big-data systems: MapReduce and Spark sort map output into spill files and merge them, and LSM-tree databases (RocksDB, Cassandra) merge sorted files during compaction.

## Key takeaways
- Generate sorted runs, then merge their buffered fronts with a heap.
- Run budgets must leave room for buffers and process overhead; extra merge passes add disk traffic.

## Further reading
- [Merge sort and its complexity — Princeton Algorithms](https://algs4.cs.princeton.edu/22mergesort/)
- [PostgreSQL memory budgets and temporary files](https://www.postgresql.org/docs/current/runtime-config-resource.html)
