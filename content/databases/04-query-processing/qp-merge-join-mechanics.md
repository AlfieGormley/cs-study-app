---
id: qp-merge-join-mechanics
title: Merge joins and duplicate keys
level: intermediate
minutes: 3
sourceLesson: qp-join-algorithms
summary: Merge joins and duplicate keys with worked examples and explicit assumptions.
---

These examples use PostgreSQL 18. SQL Fundamentals supplies the shop relations: `customers(id, name, email, city, country)`, `orders(id, customer_id, status, ordered_on, total)`, `products(id, price)` and `order_items(order_id)`. IDs join orders to customers and items to orders. Dates use `date`, IDs use `integer`, and totals use `numeric`. Each query fragment uses these names; ellipses and standalone WHERE clauses need the surrounding SELECT shown by their context.

All historical plan fragments and timings in this unit are **illustrative inputs**, not reproduced benchmarks or promises. Their row/page counts describe a hypothetical dataset; actual plans vary with statistics, indexes, settings, cache state and PostgreSQL version. Assume serial execution unless a parallel worker process is shown.

## Merge join (sort-merge)

If both inputs are sorted on the join key, walk them together like the merge step of merge sort. Advance whichever side has the smaller key; when the keys are equal, emit the match.

```python
def merge_join(left, right, key):
    # Sorted non-NULL keys; left unique.
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
            # Retain left for right ties.
            yield left[i], right[j]
            j += 1
```

On equality, keeping the left position allows all duplicate right keys to match it. This miniature does not handle duplicate left keys or SQL NULL semantics; a general merge join must revisit or buffer matching groups and handle unmatched outer rows separately.

With the unique-left-key assumption in this miniature, the merge is O(n + m), where n and m are the row counts of the two inputs: each step advances one of the two positions, so the work grows in proportion to the total number of rows. General duplicate-key joins must also account for output size and any repeated processing of matching groups. If an input isn't already sorted, it must be sorted first. Sorting n rows costs O(n log n), where n is the input's row count and log n grows very slowly (about 20 for a million rows in base 2), and a big sort may spill to disk. Merge join is attractive when **an index already provides the order**, or when the query needs that order anyway (`ORDER BY` on the join key).

An illustrative merge plan for the pending-orders query (disabling hash joins encourages alternatives but does not force a merge, because nested loops remain available):

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

## Key takeaways
- Merge joins need compatible sorted inputs and an eligible equality condition in PostgreSQL.
- The miniature assumes unique left keys; a general implementation must handle duplicate groups and output size.

## Further reading
- [Hash join — Wikipedia](https://en.wikipedia.org/wiki/Hash_join)
- [Sort-merge join — Wikipedia](https://en.wikipedia.org/wiki/Sort-merge_join)
- [Nested loop join — Wikipedia](https://en.wikipedia.org/wiki/Nested_loop_join)
- [Planner/optimiser: join strategies — PostgreSQL docs](https://www.postgresql.org/docs/18/planner-optimizer.html)
- [Resource consumption: work_mem and hash_mem_multiplier — PostgreSQL docs](https://www.postgresql.org/docs/18/runtime-config-resource.html)

