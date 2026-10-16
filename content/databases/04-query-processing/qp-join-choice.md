---
id: qp-join-choice
title: Index probe costs and cost crossovers
level: intermediate
minutes: 4
sourceLesson: qp-join-algorithms
summary: Index probe costs and cost crossovers with explicit page-I/O assumptions.
---

These examples use PostgreSQL 18. SQL Fundamentals supplies the shop relations: `customers(id, name, email, city, country)`, `orders(id, customer_id, status, ordered_on, total)`, `products(id, price)` and `order_items(order_id)`. IDs join orders to customers and items to orders. Dates use `date`, IDs use `integer`, and totals use `numeric`. Each query fragment uses these names; ellipses and standalone WHERE clauses need the surrounding SELECT shown by their context.

All historical plan fragments and timings in this unit are **illustrative inputs**, not reproduced benchmarks or promises. Their row/page counts describe a hypothetical dataset; actual plans vary with statistics, indexes, settings, cache state and PostgreSQL version. Assume serial execution unless a parallel worker process is shown.

## Index nested-loop I/O

Use a 1,000-page outer table R with 100,000 rows and an indexed inner table S. This deliberately cold, simplified page-I/O model excludes CPU and final output writes.

### Index nested loop

> [!note] What about index nested loop?
> Instead of scanning S for each outer row, probe an index on S's join column. With a 3-level B-tree plus a heap page, that's about 4 random reads per outer row.

```formula
C_INL = M + |R| × c_probe
C_INL = 1,000 + 100,000 × 4
C_INL = 401,000
where
C_INL: the cost of an index nested loop join, in page I/Os
M: the number of pages in the outer table R, here 1,000
R: the outer table
|R|: the number of rows in R, here 100,000
c_probe: the page reads for one index lookup: 3 to walk down a 3-level B-tree, plus 1 for the heap page holding the row, so about 4
In words: one index lookup per outer row, so the cost grows with the number of outer rows, not the size of S.
```

For 100,000 outer rows that's about 400,000 random reads, far worse than hashing. For 100 outer rows it's about 400 probe reads, far better. Index nested loop wins when the outer side is small.

Why only 3 levels? Each B-tree page holds hundreds of keys, so every level multiplies the number of reachable entries by hundreds:

```formula
h = ⌈log_f(n)⌉
h = ⌈log_{300}(1,000,000)⌉
h = ⌈2.42⌉ = 3
where
h: an idealised number of page levels on a root-to-leaf path, assuming fanout and leaf capacity both equal f; real occupancy and page metadata change height
n: greater than one; the number of entries in the idealised index, here 1,000,000
f: a value greater than one for the assumed fanout, the number of child pointers per page; a few hundred for small keys in 8 KiB pages, 300 here as an illustration
log_f: the logarithm to base f: how many times you must divide by f to get down to 1
log_{300}: the logarithm to base 300; log_300(1,000,000) ≈ 2.42, because 300 × 300 = 90,000 is too few and 300 × 300 × 300 = 27,000,000 is more than enough
⌈ ⌉: ceiling: round up to the next whole number
In words: a tree whose pages each point to about 300 others reaches a million entries in 3 levels, and 27 million in the same 3.
```

The upper levels are read on almost every lookup, so they are usually already in memory, and a real probe often needs fewer than four disk reads.

## Key takeaways
- A cold index probe pays for B-tree traversal and heap access; cached tree levels can reduce physical reads.
- Compare the probe model with hashing using the actual outer row count and workload-specific costs.

## Further reading
- [Hash join — Wikipedia](https://en.wikipedia.org/wiki/Hash_join)
- [Sort-merge join — Wikipedia](https://en.wikipedia.org/wiki/Sort-merge_join)
- [Nested loop join — Wikipedia](https://en.wikipedia.org/wiki/Nested_loop_join)
- [Planner/optimiser: join strategies — PostgreSQL docs](https://www.postgresql.org/docs/18/planner-optimizer.html)
- [Resource consumption: work_mem and hash_mem_multiplier — PostgreSQL docs](https://www.postgresql.org/docs/18/runtime-config-resource.html)


