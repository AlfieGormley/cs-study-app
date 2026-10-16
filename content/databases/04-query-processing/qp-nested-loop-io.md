---
id: qp-nested-loop-io
title: Row and block nested-loop I/O
level: intermediate
minutes: 5
sourceLesson: qp-join-algorithms
summary: Row and block nested-loop I/O with worked examples and explicit assumptions.
---

These examples use PostgreSQL 18. SQL Fundamentals supplies the shop relations: `customers(id, name, email, city, country)`, `orders(id, customer_id, status, ordered_on, total)`, `products(id, price)` and `order_items(order_id)`. IDs join orders to customers and items to orders. Dates use `date`, IDs use `integer`, and totals use `numeric`. Each query fragment uses these names; ellipses and standalone WHERE clauses need the surrounding SELECT shown by their context.

All historical plan fragments and timings in this unit are **illustrative inputs**, not reproduced benchmarks or promises. Their row/page counts describe a hypothetical dataset; actual plans vary with statistics, indexes, settings, cache state and PostgreSQL version. Assume serial execution unless a parallel worker process is shown.

## Costing them in page reads

Textbook analyses count page I/Os (each page read from or written to disk counts as one), because that's what dominates when data is on disk. They ignore CPU work and, by convention, the cost of writing the final result. Use the classic set-up:

- Table R has 1,000 pages, with 100 rows per page (100,000 rows).
- Table S has 500 pages.
- 102 pages of memory (buffer pages) are available to the join.

| Algorithm | Page I/Os |
|---|---|
| Row nested loop | 50,001,000 |
| Block nested loop | 6,000 |
| Sort-merge | 7,500 |
| Sort-merge, merged passes | 4,500 |
| Grace hash | 4,500 |
| Hash, S fits in memory | 1,500 |

The rest of this section shows where each figure comes from.

### Row nested loop

Read R once, then scan all of S once for each of R's rows:

```formula
C_NL = M + |R| × N
C_NL = 1,000 + 100,000 × 500
C_NL = 50,001,000
where
C_NL: the cost of a row-at-a-time nested loop join, in page I/Os
M: the number of pages in the outer table R, here 1,000
N: the number of pages in the inner table S, here 500
R: the outer table
|R|: the number of rows in R, here 100,000 (1,000 pages × 100 rows per page)
In words: each of R's 100,000 rows causes a full 500-page scan of S, so the inner scans swamp the 1,000 pages spent reading R itself.
```

### Block nested loop

Instead of rescanning S for every row, load as much of R as memory allows (a **block**), then scan S once per block, matching its rows against every R row in memory. Two buffer pages are kept back: one to read S into and one to collect output.

```formula
C_BNL = M + ⌈M / (B − 2)⌉ × N
C_BNL = 1,000 + ⌈1,000 / 100⌉ × 500
C_BNL = 1,000 + 10 × 500
C_BNL = 6,000
where
C_BNL: the cost of a block nested loop join, in page I/Os
M: the number of pages in the outer table R, here 1,000
N: the number of pages in the inner table S, here 500
B: the number of memory buffer pages available to the join, here 102
B − 2: the pages left to hold one block of R, after reserving one input page for S and one output page; here 100
⌈ ⌉: ceiling: round up to the next whole number, because a final part-full block still needs a full scan of S
In words: R is read once in 10 blocks of 100 pages, and S is scanned once per block, so S is read 10 times.
```

The number of times the inner table is rescanned dominates, so compare both orientations. The smaller outer table wins in this fixture; ceiling effects mean it is a heuristic rather than a universal rule. With the 500-page S as the outer and the 1,000-page R as the inner:

```formula
C_BNL = N + ⌈N / (B − 2)⌉ × M
C_BNL = 500 + ⌈500 / 100⌉ × 1,000
C_BNL = 500 + 5 × 1,000
C_BNL = 5,500
where
C_BNL: the cost of a block nested loop join, in page I/Os
N: the number of pages in S, now the outer table, here 500
M: the number of pages in R, now the inner table, here 1,000
B: the number of memory buffer pages available, here 102
B − 2: the pages left to hold one block of the outer table, here 100
⌈ ⌉: ceiling: round up to the next whole number
In words: S fits in 5 blocks, so the 1,000-page R is scanned 5 times instead of S being scanned 10 times.
```

The formula assumes the inner table is scanned from disk every time. If it fits in the operating system's cache, real costs are lower.

## Key takeaways
- Row nested loop rereads the inner once per outer row; block nested loop does so once per outer block.
- Compare both orientations with the ceiling formula; page-I/O estimates exclude CPU and final output writes.

## Further reading
- [Hash join — Wikipedia](https://en.wikipedia.org/wiki/Hash_join)
- [Sort-merge join — Wikipedia](https://en.wikipedia.org/wiki/Sort-merge_join)
- [Nested loop join — Wikipedia](https://en.wikipedia.org/wiki/Nested_loop_join)
- [Planner/optimiser: join strategies — PostgreSQL docs](https://www.postgresql.org/docs/18/planner-optimizer.html)
- [Resource consumption: work_mem and hash_mem_multiplier — PostgreSQL docs](https://www.postgresql.org/docs/18/runtime-config-resource.html)

