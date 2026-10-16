---
id: qp-hash-partition-io
title: Hash partitioning and in-memory join I/O
level: intermediate
minutes: 3
sourceLesson: qp-join-algorithms
summary: Hash partitioning and in-memory join I/O using explicit models and assumptions.
---

These examples use PostgreSQL 18. SQL Fundamentals supplies the shop relations: `customers(id, name, email, city, country)`, `orders(id, customer_id, status, ordered_on, total)`, `products(id, price)` and `order_items(order_id)`. IDs join orders to customers and items to orders. Dates use `date`, IDs use `integer`, and totals use `numeric`. Each query fragment uses these names; ellipses and standalone WHERE clauses need the surrounding SELECT shown by their context.

All historical plans and figures below are illustrative model inputs. Actual execution depends on version, workload and settings.

This unit uses R occupying 1,000 pages, S occupying 500 pages and a budget of 102 buffer pages. CPU work, partition slack and final output writes are excluded.

### Grace hash

Partition both tables by hashing the join key into one fewer partition than the available buffer pages, writing the partitions to disk. Matching rows always land in partitions with the same number, so each pair of partitions is then joined on its own in memory:

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

The current 500-page S does not fit the 102-page fixture; this next case instead assumes a larger memory budget sufficient for S and hash overhead.

If all of S fits in memory, build the hash table from S and stream R past it: each table is read once, 1,000 + 500 = 1,500 page I/Os. This is the full-input scan lower bound for this unindexed model. It does not apply to joins that can skip data using indexes or other knowledge.

## Key takeaways
- Grace hash reads and writes partitions, then reads them for joining; the simple model excludes skew and output writes.
- The single-read in-memory case needs enough space for the build table and hash overhead.

## Further reading
- [Hash join — Wikipedia](https://en.wikipedia.org/wiki/Hash_join)
- [Sort-merge join — Wikipedia](https://en.wikipedia.org/wiki/Sort-merge_join)
- [Nested loop join — Wikipedia](https://en.wikipedia.org/wiki/Nested_loop_join)
- [Planner/optimiser: join strategies — PostgreSQL docs](https://www.postgresql.org/docs/18/planner-optimizer.html)
- [Resource consumption: work_mem and hash_mem_multiplier — PostgreSQL docs](https://www.postgresql.org/docs/18/runtime-config-resource.html)


