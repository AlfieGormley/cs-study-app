---
id: qp-external-join-io
title: External sort passes and fused merge joins
level: intermediate
minutes: 3
sourceLesson: qp-join-algorithms
summary: How an external merge sort handles data bigger than memory, why more memory means fewer passes, and how feeding the final merge straight into the join saves I/O.
---

This lesson uses the textbook page-I/O model, which counts page transfers between disk and memory. It is a way of reasoning about algorithms, not PostgreSQL's planner cost units.

## External sort and merge join I/O

Use the same textbook set-up as the nested-loop lesson: R occupies 1,000 pages, S occupies 500 pages and the join has 102 buffer pages. CPU and final output writes are excluded; inputs start on disk.

### Sorting data bigger than memory

A merge join needs both inputs sorted on the join key. When a table is bigger than memory, databases use an **external merge sort**:

1. **Pass 0** reads a memory-load of pages at a time, sorts it and writes it back out as a sorted **run**.
2. **Each later pass** merges several runs into one longer run, using one buffer page per input run plus one for output.
3. Every pass reads and writes every page once, so the number of passes drives the cost.

```formula reference
n_pass = 1 + ⌈log_{B−1}(⌈P / B⌉)⌉
where
n_pass: the number of passes an external merge sort makes over the data, for a non-empty table and at least three buffer pages
P: the number of pages in the table being sorted
B: the number of memory buffer pages available
⌈P / B⌉: the number of sorted runs that pass 0 writes, one per memory-load of B pages
log_{B−1}: the logarithm to base B − 1: how many times you must divide by B − 1 to get down to 1. Each merge pass combines up to B − 1 runs into one
⌈ ⌉: ceiling: round up to the next whole number, because you can't make part of a pass
In words: one pass to make memory-sized sorted runs, then enough merge passes to combine them, where each pass can merge one fewer run than there are buffer pages. With 102 buffers, R's 1,000 pages make 10 runs and one merge pass combines them all, so the sort takes two passes.
```

Memory matters enormously here. S's 500 pages also sort in two passes (5 runs, merged at once). Sorting R with only 3 buffer pages would instead write 334 runs and then merge them two at a time, taking 10 passes in all: five times as much I/O for the same data.

### Sort-merge join

Two passes, each reading and writing every page, cost 4 I/Os per page. The merge join then reads both sorted tables once more, so the whole join costs 5 I/Os per page of R and S together: 7,500 for these 1,500 pages.

### Feeding the final merge into the join

The last merge pass of each sort does not have to write its output. If both final merges feed the join directly, the fully sorted tables are never written out:

- pass 0 reads and writes each page (2 I/Os per page);
- the combined merge-and-join pass reads each run once (1 I/O per page).

That is 3 I/Os per page, 4,500 here, the same as a Grace hash join. It works only if every run from both tables can be open at once: R makes 10 runs and S makes 5, so the 15 input buffers fit easily within 102. Duplicate-key groups may need extra buffering or rescans, which this model leaves out.

## Key takeaways
- External sort creates runs and merges them using the available input buffers.
- A fused final merge can avoid writing sorted inputs, provided both merge streams and matching groups fit the buffer budget.

## Further reading
- [Hash join — Wikipedia](https://en.wikipedia.org/wiki/Hash_join)
- [Sort-merge join — Wikipedia](https://en.wikipedia.org/wiki/Sort-merge_join)
- [Nested loop join — Wikipedia](https://en.wikipedia.org/wiki/Nested_loop_join)
- [Planner/optimiser: join strategies — PostgreSQL docs](https://www.postgresql.org/docs/18/planner-optimizer.html)
- [Resource consumption: work_mem and hash_mem_multiplier — PostgreSQL docs](https://www.postgresql.org/docs/18/runtime-config-resource.html)


