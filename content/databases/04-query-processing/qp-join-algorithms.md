---
id: qp-join-algorithms
title: Join algorithms and their costs
level: intermediate
minutes: 15
summary: Nested loop, hash and merge joins. How each one works, what it costs in page reads, when each wins, and what they look like in real PostgreSQL plans.
---

> [!note] Content gap: benchmark provenance
> Reproducible measurement records for the original laptop timings were not available to this audit, so empirical performance claims are omitted. The plan numbers below are retained only as illustrative inputs for learning EXPLAIN, not verified measurements or promised speedups. Measure your own representative workload.


A join is logically simple: pair every row of one input with every row of the other, and keep the pairs that satisfy the condition. Doing exactly that is far too slow for big tables, so databases have three main physical algorithms. Slow joins may involve an unsuitable choice among these algorithms, but slow queries can also have other causes.

The two inputs are called the **outer** and **inner** sides (in a hash join, the **probe** and **build** sides). In a Postgres plan, the first child of a join node is the outer and the second is the inner.

## Nested loop join

The obvious algorithm: for each outer row, look through the inner input for matches.

```python
def nested_loop(outer, inner, cond):
    for r in outer:
        for s in inner:
            if cond(r, s):
                yield r, s
```

Every outer row is tested against every inner row, so the number of tests is the product of the two row counts:

```formula
C = |R| × |S|
C = 30,000 × 100,000
C = 3,000,000,000
where
C: the number of times the join condition is evaluated
R: the outer input, here the pending orders
S: the inner input, here the customers table
|R|: the number of rows in R, about 30,000 pending orders
|S|: the number of rows in S, 100,000 customers
In words: a plain nested loop tests every possible pairing, so 30,000 orders against 100,000 customers means 3 billion tests.
```

Doubling either input doubles the work, and doubling both quadruples it. That's why a plain nested loop is only sensible when at least one side is tiny.

It becomes a great algorithm when the inner side is an **index lookup** instead of a full scan. Then each outer row costs one index probe, a few page reads:

```sql
SELECT o.id, c.name
FROM orders o
JOIN customers c ON c.id = o.customer_id
WHERE o.id < 100;
```

```
Nested Loop  (actual rows=99.00)
-> Index Scan using orders_pkey on o
     Index Cond: (id < 100)
-> Index Scan using customers_pkey on c
     Index Cond: (id = o.customer_id)
     (actual rows=1.00 loops=99)
Execution Time: 0.405 ms
```

The `loops=99` on the inner node means it ran once per outer row. Ninety-nine primary-key probes: 0.4 ms.

Nested loop is also the **only** algorithm that handles any join condition. Hash and merge joins need equality, so a condition like `p.price < q.price - 199` always gets a nested loop.

> [!tip] Memoize
> Since Postgres 14, a `Memoize` node can sit above the inner side of a nested loop and cache results by join key. If many outer rows share the same key, repeat lookups are served from the cache. You'll see `Hits` and `Misses` counts in EXPLAIN ANALYZE.

## Hash join

Pick the smaller input. Read all of it into an in-memory hash table keyed on the join column (the **build** phase). Then stream the larger input and look each row up in the table (the **probe** phase).

```python
def hash_join(build, probe, bkey, pkey):
    table = {}
    for s in build:
        k = bkey(s)
        table.setdefault(k, []).append(s)
    for r in probe:
        for s in table.get(pkey(r), []):
            yield r, s
```

Write |R| and |S| for the row counts of the two inputs. With well-distributed hashing, building and probing cost expected O(|R| + |S|): the work grows in proportion to the total number of input rows (big-O notation ignores constant factors). On top of that comes the cost of emitting the result. Duplicate keys can produce up to |R| × |S| output rows, and those cannot be emitted in time that grows only with the inputs. In Postgres:

```
Hash Join  (actual rows=30066.00)
  Hash Cond: (o.customer_id = c.id)
-> Seq Scan on orders o
     Filter: (status = 'pending'::text)
-> Hash
     Buckets: 131072  Batches: 1
     Memory Usage: 4540kB
   -> Seq Scan on customers c
Execution Time: 36.958 ms
```

`Batches: 1` means the whole hash table fitted in memory. Postgres caps the memory a hash table may use with two settings:

```formula
L_hash = M_work × k_hash
L_hash = 4 MB × 2
L_hash = 8 MB
where
L_hash: the most memory one hash table may use before Postgres splits the join into batches on disk, in megabytes (MB)
M_work: the `work_mem` setting, the memory budget for one sort or hash operation; default 4 MB
k_hash: the `hash_mem_multiplier` setting, which lets hash operations use a multiple of `work_mem`; default 2.0 since PostgreSQL 15
MB: megabyte; in PostgreSQL settings 1 MB = 1,024 kB
In words: by default a hash table may grow to twice `work_mem`, which is 8 MB.
```

The customers hash table used 4,540 kB, about 4.4 MB, so it fits in one batch. The limit applies to each hash operation separately, so a query with three hash joins can use up to three times as much.

### When the build side doesn't fit

If the build side is too large, Postgres uses a **hybrid hash join**. It splits both inputs into partitions (batches) by hashing the join key, keeps the first batch in memory and writes the rest to temporary files. Matching rows always land in the same batch number on both sides, so each batch can be joined on its own. Rerunning the join of all orders with `work_mem` cut to 1 MB:

```
Hash  Buckets: 65536  Batches: 4
      Memory Usage: 1392kB
Buffers: temp read=2421 written=2421
Execution Time: 159.560 ms
```

Same answer, but 4 batches, temporary file I/O and about 16% slower (160 ms against 138 ms). The effect of spilling on run time depends on workload, storage and cache state.

Hash joins need an equality condition and give no output order. They are the usual choice for joining large unsorted inputs.

## Merge join (sort-merge)

If both inputs are sorted on the join key, walk them together like the merge step of merge sort. Advance whichever side has the smaller key; when the keys are equal, emit the match.

```python
def merge_join(left, right, key):
    # both sorted; left keys unique
    i = j = 0
    while (i < len(left)
           and j < len(right)):
        a = key(left[i])
        b = key(right[j])
        if a < b:
            i += 1
        elif a > b:
            j += 1
        else:
            yield left[i], right[j]
            j += 1
```

With the unique-left-key assumption in this miniature, the merge is O(|R| + |S|), where |R| and |S| are the row counts of the two inputs: each step advances one of the two positions, so the work grows in proportion to the total number of rows. General duplicate-key joins must also account for output size and any repeated processing of matching groups. If an input isn't already sorted, it must be sorted first. Sorting n rows costs O(n log n), where n is the input's row count and log n grows very slowly (about 20 for a million rows in base 2), and a big sort may spill to disk. Merge join is attractive when **an index already provides the order**, or when the query needs that order anyway (`ORDER BY` on the join key).

Forcing a merge join for the pending-orders query (by disabling hash joins):

```
Merge Join
  Merge Cond: (c.id = o.customer_id)
-> Index Only Scan using customers_pkey
-> Sort  Sort Key: o.customer_id
     Sort Method: quicksort  Memory: 769kB
   -> Seq Scan on orders o
        Filter: (status = 'pending')
Execution Time: 36.220 ms
```

`customers` comes out of its primary-key index already in `id` order, and only the 30,066 pending orders need sorting, in memory. The time is essentially the same as the hash join, which is why the planner's estimates for the two were close.

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

The number of times the inner table is rescanned dominates, so put the smaller table on the outside. With the 500-page S as the outer and the 1,000-page R as the inner:

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

### Sort-merge

First sort both tables on the join key with an **external merge sort**, the algorithm databases use for data bigger than memory. Pass 0 reads a memory-load of pages at a time, sorts it and writes it back out as a sorted **run**. Each later pass merges up to B − 1 runs into one, using one buffer page per run plus one for output. Every pass reads and writes every page once. The number of passes is:

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

### Grace hash

Partition both tables by hashing the join key into B − 1 partitions each, writing the partitions to disk. Matching rows always land in partitions with the same number, so each pair of partitions is then joined on its own in memory:

```formula
C_GH = 2 × (M + N) + (M + N)
C_GH = 3 × (1,000 + 500)
C_GH = 4,500
where
C_GH: the cost of a Grace hash join, in page I/Os
M: the number of pages in R, here 1,000
N: the number of pages in S, here 500
In words: partitioning reads and writes both tables (2 I/Os per page), then joining the partition pairs reads them once more (1 I/O per page).
```

This needs each partition of the smaller table to fit in memory. Here S's 500 pages split into 101 partitions of about 5 pages, which fit easily. If the hash spreads keys badly, some partitions are too big and must be partitioned again.

### Hash, when S fits in memory

If all of S fits in memory, build the hash table from S and stream R past it: each table is read once, 1,000 + 500 = 1,500 page I/Os. That's the best any join can do, because every page has to be read anyway.

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
h: the height of the B-tree: the number of pages read to walk from the root to a leaf
n: the number of entries in the index, here 1,000,000
f: the fanout, the number of child pointers per page; a few hundred for small keys in 8 KiB pages, 300 here as an illustration
log_f: the logarithm to base f: how many times you must divide by f to get down to 1
log_{300}: the logarithm to base 300; log_300(1,000,000) ≈ 2.42, because 300 × 300 = 90,000 is too few and 300 × 300 × 300 = 27,000,000 is more than enough
⌈ ⌉: ceiling: round up to the next whole number
In words: a tree whose pages each point to about 300 others reaches a million entries in 3 levels, and 27 million in the same 3.
```

The upper levels are read on almost every lookup, so they are usually already in memory, and a real probe often needs fewer than four disk reads.

## Choosing between them

| | Nested loop | Hash | Merge |
|---|---|---|---|
| Join condition | Any | Equality | Equality |
| Best when | Small outer, indexed inner | Large unsorted inputs | Inputs already sorted |
| Memory | Little | Build side | Little (if presorted) |
| Output order | Outer's order | None | Join key |

The illustrative plan costs show why an access path can matter. Joining pending orders to customers:

| Plan | Estimated cost |
|---|---|
| Hash join | 23,290 |
| Merge join | 25,539 |
| Nested loop + index | 30,572 |
| Nested loop, no index | 46,172,536 |

Without an index on the inner side, the nested loop is about 2,000 times more expensive. That's the plan you get when an index is missing **and** no equality condition exists, or when the planner wrongly believes the outer side has one row.

At larger scale, joining all 1,000,000 orders to their 3,000,000 order items, the hash join (8 batches, 587 ms) beat a merge join that had to sort 3 million rows through a 35 MB temporary file (850 ms).

## Outer, semi and anti joins

All three algorithms come in variants for other join types, and you'll see the names in plans:

- `Hash Left Join`, `Merge Full Join`: outer joins. Postgres can't run a `FULL OUTER JOIN` as a nested loop, because the nested loop has no cheap way to remember which inner rows never matched.
- `Semi Join`: from `EXISTS` or `IN`. Stops at the first matching row for each outer row.
- `Anti Join`: from `NOT EXISTS`. Emits outer rows with no match.
- `Hash Right Join`: the planner swapped sides so the smaller input is hashed, even though the SQL said `LEFT JOIN`.

## Key takeaways
- Nested loop handles any condition. It is excellent with a small outer side and an index on the inner side, and catastrophic without one.
- Hash join builds a table from the smaller input and probes it with the larger. It needs equality, and spills into batches when the build side exceeds `work_mem x hash_mem_multiplier`.
- Merge join walks two sorted inputs together. It shines when indexes already provide the order.
- In page I/Os, block nested loop reads the inner table once per memory-sized block of the outer, while Grace hash and sort-merge with merged passes read and write each table about three times in total.
- The planner picks between them using row estimates, so bad estimates lead to bad joins (next lesson).

## Further reading
- [Hash join — Wikipedia](https://en.wikipedia.org/wiki/Hash_join)
- [Sort-merge join — Wikipedia](https://en.wikipedia.org/wiki/Sort-merge_join)
- [Nested loop join — Wikipedia](https://en.wikipedia.org/wiki/Nested_loop_join)
- [Planner/optimiser: join strategies — PostgreSQL docs](https://www.postgresql.org/docs/current/planner-optimizer.html)
- [Resource consumption: work_mem and hash_mem_multiplier — PostgreSQL docs](https://www.postgresql.org/docs/current/runtime-config-resource.html)
