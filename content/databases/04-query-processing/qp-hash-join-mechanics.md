---
id: qp-hash-join-mechanics
title: Hash joins and memory batches
level: intermediate
minutes: 4
sourceLesson: qp-join-algorithms
summary: How a hash join builds a table from one input and probes it with the other, how PostgreSQL picks the build side, and what spilling into batches looks like.
---

Examples use PostgreSQL 18 and the module's scaled-up shop tables (1,000,000 orders, 100,000 customers; the first lesson lists them). Plans are abbreviated and illustrative: real plans and timings depend on the data, statistics, settings, cache state and version. Assume serial execution.

## Hash join

Pick the input that is smaller after its filters and column projection, subject to join semantics. Read all of it into an in-memory hash table keyed on the join column (the **build** phase). Then stream the larger input and look each row up in the table (the **probe** phase).

```python
def hash_join(build, probe, bkey, pkey):
    table = {}
    for s in build:
        k = bkey(s)
        # Retain every duplicate build row.
        table.setdefault(k, []).append(s)
    for r in probe:
        for s in table.get(pkey(r), []):
            yield r, s
```

This miniature joins non-NULL, hashable keys using Python equality. SQL equality does not match NULL keys: a SQL-style inner hash join must omit them rather than treating Python None as an ordinary matching key.

Let n and m be the two input row counts. With well-distributed hashing, building and probing cost expected O(n + m): the work grows in proportion to the total number of input rows (big-O notation ignores constant factors). On top of that comes the cost of emitting the result. Duplicate keys can produce the product of the input row counts in output rows, and those cannot be emitted in time that grows only with the inputs.

> [!analogy] Real-world analogy: a cloakroom
> At a theatre cloakroom, coats go on numbered hooks as people arrive. After the show, each person hands over a ticket and the attendant walks straight to that hook rather than searching every coat.
>
> **How it maps:** hanging coats is the build phase, filling a hash table keyed on the join column. Handing over tickets is the probe phase: each row of the other input goes straight to its bucket. The rack must be complete before anyone collects, which is why the build side is a blocking step.
>
> **Where it stops:** one ticket matches one coat, but a join key can match many build rows, and every match is emitted. A cloakroom also never needs to send half its coats to a store room; a hash join that runs out of memory must split its work into batches on disk.

Here is an illustrative join of the pending orders to customers, where the query above the join needs only a few narrow customer columns:

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

Here customers was the build side. The choice follows the estimates, not the table names: when the same join selected every column of both tables, PostgreSQL 18.6 hashed the 30,000 filtered orders instead, because after filtering they were the smaller input.

`Batches: 1` means the whole hash table fitted in memory. Postgres caps the memory a hash table may use with two settings:

```formula reference
L_hash = M_work × k_hash
where
L_hash: the nominal memory budget for one hash operation before it splits into batches, rather than a strict cap on all executor memory, in megabytes (MB)
M_work: the `work_mem` setting, the memory budget for one sort or hash operation; default 4 MB
k_hash: the `hash_mem_multiplier` setting, which lets hash operations use a multiple of `work_mem`; default 2.0 since PostgreSQL 15
MB: megabyte; in PostgreSQL settings 1 MB = 1,024 kB
In words: by default a hash table may grow to twice `work_mem`, which is 8 MB, before PostgreSQL splits the join into batches.
```

The customers hash table used 4,540 kB, about 4.4 MB, so it fits in one batch. The budget applies per operation and can also multiply across concurrent processes and sessions. Actual overhead and skew make it unsafe to treat it as an exact bound on query memory.

### When the build side doesn't fit

If the build side is too large, Postgres uses a **hybrid hash join**. It splits both inputs into partitions (batches) by hashing the join key, keeps the first batch in memory and writes the rest to temporary files. Matching rows always land in the same batch number on both sides, so each batch can be joined on its own. Rerunning the join of all orders with `work_mem` cut to 1 MB:

```
Hash  Buckets: 65536  Batches: 4
      Memory Usage: 1392kB
Buffers: temp read=2421 written=2421
Execution Time: 159.560 ms
```

Same answer, but 4 batches, temporary file I/O and, in this illustrative run, about 16% slower (160 ms against 138 ms). The effect of spilling on elapsed execution time depends on workload, storage and cache state.

Hash joins need a hash-joinable equality clause and do not promise result order. They are often attractive for large unsorted inputs; width, skew, result size and other paths still matter.

## Key takeaways
- A hash build retains duplicate keys; output size can dominate input-linear hashing work.
- Multiple batches and temporary-file traffic indicate spilling; memory budgets multiply across operations and processes.

## Further reading
- [Hash join — Wikipedia](https://en.wikipedia.org/wiki/Hash_join)
- [Sort-merge join — Wikipedia](https://en.wikipedia.org/wiki/Sort-merge_join)
- [Nested loop join — Wikipedia](https://en.wikipedia.org/wiki/Nested_loop_join)
- [Planner/optimiser: join strategies — PostgreSQL docs](https://www.postgresql.org/docs/18/planner-optimizer.html)
- [Resource consumption: work_mem and hash_mem_multiplier — PostgreSQL docs](https://www.postgresql.org/docs/18/runtime-config-resource.html)

