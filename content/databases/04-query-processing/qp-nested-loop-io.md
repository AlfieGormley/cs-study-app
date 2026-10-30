---
id: qp-nested-loop-io
title: Row and block nested-loop I/O
level: intermediate
minutes: 4
sourceLesson: qp-join-algorithms
summary: Why a block nested loop rereads the inner table far fewer times than a row-at-a-time loop, and which table to put on the outer side.
---

This lesson uses the textbook page-I/O model, which counts page transfers between disk and memory. It is a way of reasoning about algorithms, not PostgreSQL's planner cost units.

## Counting page reads

Textbook analyses count page I/Os (each page read from or written to disk counts as one), because that is what dominates when data is on disk. They ignore CPU work and, by convention, the cost of writing the final result. The classic set-up used in this and the next few lessons:

- Table R has 1,000 pages, with 100 rows per page (100,000 rows).
- Table S has 500 pages.
- 102 pages of memory (buffer pages) are available to the join.
- Neither table has an index on the join column.

| Algorithm | Page I/Os |
|---|---|
| Row nested loop | 50,001,000 |
| Block nested loop | 6,000 |
| Sort-merge | 7,500 |
| Sort-merge, merged passes | 4,500 |
| Grace hash | 4,500 |
| Hash, S fits in memory | 1,500 |

The spread is the point: the same join costs anything from 1,500 to 50 million page I/Os depending on the algorithm and the memory it can use.

### Row nested loop

Read R once, then scan all of S once for **each row** of R. That is 100,000 scans of a 500-page table, about 50 million page reads, which swamp the 1,000 pages spent reading R itself.

### Block nested loop

Instead of rescanning S for every row, load as much of R as memory allows (a **block**), then scan S once per block, matching its rows against every R row in memory. Two buffer pages are kept back: one to read S into and one to collect output. The number of times the inner table is reread is what matters:

```formula essential
C_BNL = M + ⌈M / (B − 2)⌉ × N
where
C_BNL: the cost of a block nested loop join, in page I/Os
M: the number of pages in the outer table
N: the number of pages in the inner table
B: the number of memory buffer pages available to the join
B − 2: the pages left to hold one block of the outer table, after reserving one input page for the inner table and one output page
⌈ ⌉: ceiling: round up to the next whole number, because a final part-full block still needs a full scan of the inner table
In words: read the outer table once, and scan the whole inner table once per block of the outer table. More memory means bigger blocks, fewer blocks and fewer rescans.
```

With R as the outer side, its 1,000 pages make 10 blocks of 100 pages, so S is scanned 10 times: 1,000 + 5,000 = 6,000 page I/Os. Swap the sides and S's 500 pages make only 5 blocks, so the 1,000-page R is scanned 5 times: 500 + 5,000 = 5,500. Putting the **smaller table on the outer side** usually wins because it produces fewer blocks. Ceiling effects mean this is a heuristic: compare both orientations when the sizes are close.

Two levers follow directly from the relationship. Doubling the memory roughly halves the number of rescans, and a table small enough to fit in one block needs only a single scan of the inner table.

The model assumes the inner table is read from disk every time. If it fits in the operating system's cache, real costs are lower.

## Key takeaways
- Row nested loop rereads the inner once per outer row; block nested loop does so once per outer block.
- The smaller table usually belongs on the outer side, and more memory means fewer inner rescans; page-I/O counts exclude CPU and final output writes.

## Further reading
- [Hash join — Wikipedia](https://en.wikipedia.org/wiki/Hash_join)
- [Sort-merge join — Wikipedia](https://en.wikipedia.org/wiki/Sort-merge_join)
- [Nested loop join — Wikipedia](https://en.wikipedia.org/wiki/Nested_loop_join)
- [Planner/optimiser: join strategies — PostgreSQL docs](https://www.postgresql.org/docs/18/planner-optimizer.html)
- [Resource consumption: work_mem and hash_mem_multiplier — PostgreSQL docs](https://www.postgresql.org/docs/18/runtime-config-resource.html)

