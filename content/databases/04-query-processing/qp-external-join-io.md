---
id: qp-external-join-io
title: External sort passes and fused merge joins
level: intermediate
minutes: 5
sourceLesson: qp-join-algorithms
summary: External sort passes and fused merge joins with explicit page-I/O assumptions.
---

These examples use PostgreSQL 18. SQL Fundamentals supplies the shop relations: `customers(id, name, email, city, country)`, `orders(id, customer_id, status, ordered_on, total)`, `products(id, price)` and `order_items(order_id)`. IDs join orders to customers and items to orders. Dates use `date`, IDs use `integer`, and totals use `numeric`. Each query fragment uses these names; ellipses and standalone WHERE clauses need the surrounding SELECT shown by their context.

All historical plan fragments and timings in this unit are **illustrative inputs**, not reproduced benchmarks or promises. Their row/page counts describe a hypothetical dataset; actual plans vary with statistics, indexes, settings, cache state and PostgreSQL version. Assume serial execution unless a parallel worker process is shown.

## External sort and hash I/O

Use the same textbook fixture: R occupies 1,000 pages, S occupies 500 pages and the join has 102 buffer pages. CPU and final output writes are excluded; inputs start on disk.

### Sort-merge

First sort both tables on the join key with an **external merge sort**, the algorithm databases use for data bigger than memory. Pass 0 reads a memory-load of pages at a time, sorts it and writes it back out as a sorted **run**. Each later pass merges as many runs as there are available input buffers into one, using one buffer page per run plus one for output. Every pass reads and writes every page once. For a non-empty table and at least three buffer pages, the number of passes in this textbook model is:

```formula
n_pass = 1 + ⌈log_{B−1}(⌈P / B⌉)⌉
n_pass = 1 + ⌈log_{101}(⌈1,000 / 102⌉)⌉
n_pass = 1 + ⌈log_{101}(10)⌉
n_pass = 1 + ⌈0.5⌉ = 1 + 1 = 2
where
n_pass: the number of passes an external merge sort makes over the data
P: the number of pages in the table being sorted, here 1,000 for R
B: the number of memory buffer pages available, here 102
⌈P / B⌉: the number of sorted runs that pass 0 writes, one per memory-load of B pages; here 10
log_{B−1}: the logarithm to base B − 1: how many times you must divide by B − 1 to get down to 1. Each merge pass divides the number of runs by up to B − 1
log_{101}: the logarithm to base 101 (B − 1 with B = 102); log_101(10) is about 0.5, because 101^0.5 ≈ 10
⌈ ⌉: ceiling: round up to the next whole number, because you can't make part of a pass
In words: with 102 buffer pages, pass 0 makes 10 runs and a single merge pass combines all 10, so sorting takes two passes.
```

S, with 500 pages, also needs two passes (5 runs, merged in one pass). With very little memory the number of passes grows: sorting R with only 3 buffer pages, pass 0 would write 334 runs of 3 pages, and merging them two at a time would take 9 more passes, 10 in all. That's why more sort memory helps so much.

Two passes, each reading and writing every page, is 4 I/Os per page. The merge join then reads both sorted tables once more:

```formula
C_SM = 2 × n_pass × (M + N) + (M + N)
C_SM = 2 × 2 × 1,500 + 1,500
C_SM = 6,000 + 1,500 = 7,500
where
C_SM: the cost of a sort-merge join, in page I/Os
n_pass: the passes each sort makes, here 2
2: each pass reads every page once and writes it once
M: the number of pages in R, here 1,000
N: the number of pages in S, here 500
In words: sorting costs 4 I/Os per page of both tables, and the merge reads them once more, so 5 I/Os per page in total.
```

Here R creates 10 runs and S creates 5. Merging both streams together needs one input buffer per run, plus join/output bookkeeping: 15 input buffers fit within the 102-page budget. Duplicate-key groups may need additional buffering or rescans; the following model excludes that extra work.

If the final merge pass of each sort feeds the join directly, the fully sorted tables are never written out. Only pass 0 reads and writes, and the merge pass reads once:

```formula
C_fused = 2 × (M + N) + (M + N)
C_fused = 3 × (1,000 + 500)
C_fused = 4,500
where
C_fused: the cost of a sort-merge join whose final merge pass feeds the join directly, in page I/Os
M: the number of pages in R, here 1,000
N: the number of pages in S, here 500
In words: write the sorted runs once (2 I/Os per page) and read them once while merging and joining (1 I/O per page): 3 I/Os per page.
```

## Key takeaways
- External sort creates runs and merges them using the available input buffers.
- A fused final merge can avoid writing sorted inputs, provided both merge streams and matching groups fit the buffer budget.

## Further reading
- [Hash join — Wikipedia](https://en.wikipedia.org/wiki/Hash_join)
- [Sort-merge join — Wikipedia](https://en.wikipedia.org/wiki/Sort-merge_join)
- [Nested loop join — Wikipedia](https://en.wikipedia.org/wiki/Nested_loop_join)
- [Planner/optimiser: join strategies — PostgreSQL docs](https://www.postgresql.org/docs/18/planner-optimizer.html)
- [Resource consumption: work_mem and hash_mem_multiplier — PostgreSQL docs](https://www.postgresql.org/docs/18/runtime-config-resource.html)


