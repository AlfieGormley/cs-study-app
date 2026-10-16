---
id: qp-nested-loop-mechanics
title: Nested loops and indexed probes
level: intermediate
minutes: 4
sourceLesson: qp-join-algorithms
summary: Nested loops and indexed probes with worked examples and explicit assumptions.
---

These examples use PostgreSQL 18. SQL Fundamentals supplies the shop relations: `customers(id, name, email, city, country)`, `orders(id, customer_id, status, ordered_on, total)`, `products(id, price)` and `order_items(order_id)`. IDs join orders to customers and items to orders. Dates use `date`, IDs use `integer`, and totals use `numeric`. Each query fragment uses these names; ellipses and standalone WHERE clauses need the surrounding SELECT shown by their context.

All historical plan fragments and timings in this unit are **illustrative inputs**, not reproduced benchmarks or promises. Their row/page counts describe a hypothetical dataset; actual plans vary with statistics, indexes, settings, cache state and PostgreSQL version. Assume serial execution unless a parallel worker process is shown.

A join is logically simple: pair every row of one input with every row of the other, and keep the pairs that satisfy the condition. Doing exactly that is far too slow for big tables, so databases have three main physical algorithms. Slow joins may involve an unsuitable choice among these algorithms, but slow queries can also have other causes.

The two inputs are called the **outer** and **inner** sides (in a hash join, the **probe** and **build** sides). In a Postgres plan, the first child of a join node is the outer and the second is the inner.

## Nested loop join

The obvious algorithm: for each outer row, look through the inner input for matches.

```python
def nested_loop(outer, inner, cond):
    for r in outer:
        # Rescan inner for each outer row.
        for s in inner:
            if cond(r, s):
                yield r, s
```

The miniature needs a reusable inner iterable, such as a list, rather than a one-shot generator. Its predicate is a Python callable; SQL equality needs a separate test for SQL NULL.

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

It becomes a great algorithm when the inner side is a **database index lookup** instead of a full scan. Then each outer row costs one index probe, a few page reads:

```sql
-- Only low-ID orders reach the probes.
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

Nested loop is also the **only** algorithm that handles any join condition. PostgreSQL hash and merge joins need a suitable hash-joinable or merge-joinable equality clause. A pure condition like `p.price < q.price - 199` therefore needs a nested loop in PostgreSQL 18. Other database engines can implement specialised inequality joins.

> [!tip] Memoize
> Since Postgres 14, a `Memoize` node can sit above the inner side of a nested loop and cache results by join key. If many outer rows share the same key, repeat lookups are served from the cache. You'll see `Hits` and `Misses` counts in EXPLAIN ANALYZE.

## Key takeaways
- A plain nested loop tests every pair; an indexed inner lookup changes the cost of each outer iteration.
- PostgreSQL 18 needs a suitable equality clause for hash or merge joins; pure inequality joins use nested loops.

## Further reading
- [Hash join — Wikipedia](https://en.wikipedia.org/wiki/Hash_join)
- [Sort-merge join — Wikipedia](https://en.wikipedia.org/wiki/Sort-merge_join)
- [Nested loop join — Wikipedia](https://en.wikipedia.org/wiki/Nested_loop_join)
- [Planner/optimiser: join strategies — PostgreSQL docs](https://www.postgresql.org/docs/18/planner-optimizer.html)
- [Resource consumption: work_mem and hash_mem_multiplier — PostgreSQL docs](https://www.postgresql.org/docs/18/runtime-config-resource.html)

