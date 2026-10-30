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

In this plan, 100 input buffers of 8 MB take 800 MB during the merge. More runs means smaller buffers each, and very small buffers turn sequential reads into many short ones, so the run count and buffer size are planned together.

Total: every record is read and written twice (once per phase), all sequentially. If there are too many runs to merge in one go, you merge in several passes, each multiplying run length by k.

> [!example] PostgreSQL does exactly this
> When a sort needs more memory than `work_mem` (default 4 MB), PostgreSQL switches to an external merge sort using temporary files. `EXPLAIN ANALYZE` shows `Sort Method: external merge  Disk: ...` instead of `quicksort  Memory: ...`. Raising `work_mem` for a big reporting query can keep the sort in memory.

> [!analogy] Real-world analogy: sorting a huge card index on a small desk
> You must alphabetise a hundred drawers of index cards, but your desk only holds one drawer's worth. So you sort one drawer at a time on the desk and put each sorted batch back in its own box. Then you line up the boxes, look only at the front card of each, and repeatedly move the earliest of those front cards onto the final pile.
>
> **How it maps:** the desk is RAM, each sorted box is a run written to disk, and choosing the earliest front card is the k-way merge (the min-heap keeps track of which front card is earliest). Every card is handled twice: once while making a box, once while merging.
>
> **Where it stops:** you can see a hundred front cards at a glance, but a computer must read each run through a small buffer and refill it from disk. Disks reward reading long stretches in order, so the real design is about buffer sizes and sequential I/O, not just card handling.

The same pattern appears in big-data systems: MapReduce and Spark sort map output into spill files and merge them, and LSM-tree databases (RocksDB, Cassandra) merge sorted files during compaction.

## Key takeaways
- Generate sorted runs, then merge their buffered fronts with a heap.
- Run budgets must leave room for buffers and process overhead; extra merge passes add disk traffic.

## Further reading
- [Merge sort and its complexity — Princeton Algorithms](https://algs4.cs.princeton.edu/22mergesort/)
- [PostgreSQL memory budgets and temporary files](https://www.postgresql.org/docs/current/runtime-config-resource.html)
