---
id: qp-hash-join-mechanics
title: Hash joins and memory batches
level: intermediate
minutes: 4
sourceLesson: qp-join-algorithms
summary: Hash joins and memory batches with worked examples and explicit assumptions.
---

These examples use PostgreSQL 18. SQL Fundamentals supplies the shop relations: `customers(id, name, email, city, country)`, `orders(id, customer_id, status, ordered_on, total)`, `products(id, price)` and `order_items(order_id)`. IDs join orders to customers and items to orders. Dates use `date`, IDs use `integer`, and totals use `numeric`. Each query fragment uses these names; ellipses and standalone WHERE clauses need the surrounding SELECT shown by their context.

All historical plan fragments and timings in this unit are **illustrative inputs**, not reproduced benchmarks or promises. Their row/page counts describe a hypothetical dataset; actual plans vary with statistics, indexes, settings, cache state and PostgreSQL version. Assume serial execution unless a parallel worker process is shown.

## Hash join

Prefer a build input with a small projected size, subject to join semantics and available paths. Read all of it into an in-memory hash table keyed on the join column (the **build** phase). Then stream the larger input and look each row up in the table (the **probe** phase).

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

Let n and m be the two input row counts. With well-distributed hashing, building and probing cost expected O(n + m): the work grows in proportion to the total number of input rows (big-O notation ignores constant factors). On top of that comes the cost of emitting the result. Duplicate keys can produce the product of the input row counts in output rows, and those cannot be emitted in time that grows only with the inputs. In Postgres:

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
L_hash: the nominal memory budget for one hash operation before batching, rather than a strict cap on all executor memory, in megabytes (MB)
M_work: the `work_mem` setting, the memory budget for one sort or hash operation; default 4 MB
k_hash: the `hash_mem_multiplier` setting, which lets hash operations use a multiple of `work_mem`; default 2.0 since PostgreSQL 15
MB: megabyte; in PostgreSQL settings 1 MB = 1,024 kB
In words: by default a hash table may grow to twice `work_mem`, which is 8 MB.
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

Same answer, but 4 batches, temporary file I/O and about 16% slower (160 ms against 138 ms). The effect of spilling on elapsed execution time depends on workload, storage and cache state.

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

