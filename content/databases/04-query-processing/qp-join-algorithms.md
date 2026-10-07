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

With |R| outer rows and |S| inner rows, that's |R| x |S| comparisons. Joining 30,000 pending orders to 100,000 customers this way is 3 billion comparisons.

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

With well-distributed hashing, building and probing cost expected O(|R| + |S|), plus the cost of emitting the result. Duplicate keys can produce O(|R| × |S|) output rows; those cannot be emitted in linear input time. In Postgres:

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

`Batches: 1` means the whole hash table fitted in memory. Postgres allows a hash table `work_mem x hash_mem_multiplier` bytes, which is 4 MB x 2 = 8 MB by default, so 4.5 MB fits.

### When the build side doesn't fit

If the build side is too large, Postgres uses a **hybrid hash join**. It splits both inputs into partitions (batches) by hashing the join key, keeps the first batch in memory and writes the rest to temporary files. Matching rows always land in the same batch number on both sides, so each batch can be joined on its own. Rerunning the join of all orders with `work_mem` cut to 1 MB:

```
Hash  Buckets: 65536  Batches: 4
      Memory Usage: 1392kB
Buffers: temp read=2421 written=2421
Execution Time: 159.560 ms
```

Same answer, but 4 batches, temporary file I/O and 15% slower (160 ms against 138 ms). The runtime effect of spilling depends on workload, storage and cache state.

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

With the unique-left-key assumption in this miniature, the merge is O(|R| + |S|). General duplicate-key joins must also account for output size and any repeated processing of matching groups. If an input isn't already sorted, it must be sorted first, which costs O(n log n) and may spill to disk. Merge join is attractive when **an index already provides the order**, or when the query needs that order anyway (`ORDER BY` on the join key).

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

Textbook analyses count page I/Os, because that's what dominates when data is on disk. Use the classic set-up:

- R has M = 1,000 pages, 100 rows per page (100,000 rows).
- S has N = 500 pages.
- B = 102 pages of memory are available.

| Algorithm | Formula | Pages |
|---|---|---|
| Row nested loop | M + rows(R) x N | 50,001,000 |
| Block nested loop | M + ⌈M/(B-2)⌉ x N | 6,000 |
| Sort-merge | 5(M + N) | 7,500 |
| Sort-merge, merged passes | 3(M + N) | 4,500 |
| Grace hash | 3(M + N) | 4,500 |
| Hash, S fits in memory | M + N | 1,500 |

Where these come from:

- **Row nested loop**: read R once, then scan all of S for each of R's 100,000 rows.
- **Block nested loop**: load R 100 pages at a time and scan S once per block. That's 10 blocks, so S is read 10 times. Making the smaller table the outer side gives 500 + 5 x 1,000 = 5,500.
- **Sort-merge**: sorting a table in two passes reads and writes it twice (4 I/Os per page). The merge reads both once more: 5(M + N). If the final merge pass of each sort feeds the join directly, the sorted output is never written: 3(M + N).
- **Grace hash**: partition both tables (read and write each: 2(M + N)), then join partition pairs (read each once more: M + N).

> [!note] What about index nested loop?
> Cost is M + rows(R) x (cost of one probe). With a 3-level B-tree plus a heap page, that's about 4 random reads per outer row. For 100,000 outer rows that's 400,000 random reads, far worse than hashing. For 100 outer rows it's 400, far better. Index nested loop wins when the outer side is small.

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
- `Semi Join`: from `EXISTS` or `IN`. Stops at the first match per outer row.
- `Anti Join`: from `NOT EXISTS`. Emits outer rows with no match.
- `Hash Right Join`: the planner swapped sides so the smaller input is hashed, even though the SQL said `LEFT JOIN`.

## Key takeaways
- Nested loop handles any condition. It is excellent with a small outer side and an index on the inner side, and catastrophic without one.
- Hash join builds a table from the smaller input and probes it with the larger. It needs equality, and spills into batches when the build side exceeds `work_mem x hash_mem_multiplier`.
- Merge join walks two sorted inputs together. It shines when indexes already provide the order.
- In page I/Os, block nested loop costs about M + (M/B) x N, while sort-merge and Grace hash cost about 3(M + N).
- The planner picks between them using row estimates, so bad estimates lead to bad joins (next lesson).

## Further reading
- [Hash join — Wikipedia](https://en.wikipedia.org/wiki/Hash_join)
- [Sort-merge join — Wikipedia](https://en.wikipedia.org/wiki/Sort-merge_join)
- [Nested loop join — Wikipedia](https://en.wikipedia.org/wiki/Nested_loop_join)
- [Planner/optimiser: join strategies — PostgreSQL docs](https://www.postgresql.org/docs/current/planner-optimizer.html)
- [Resource consumption: work_mem and hash_mem_multiplier — PostgreSQL docs](https://www.postgresql.org/docs/current/runtime-config-resource.html)
