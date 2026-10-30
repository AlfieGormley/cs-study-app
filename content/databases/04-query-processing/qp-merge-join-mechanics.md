---
id: qp-merge-join-mechanics
title: Merge joins and duplicate keys
level: intermediate
minutes: 3
sourceLesson: qp-join-algorithms
summary: How a merge join walks two sorted inputs together, and when existing order makes it cheaper than hashing.
---

Examples use PostgreSQL 18 and the module's scaled-up shop tables (1,000,000 orders, 100,000 customers; the first lesson lists them). Plans are abbreviated and illustrative: real plans and timings depend on the data, statistics, settings, cache state and version. Assume serial execution.

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

> [!analogy] Real-world analogy: matching two alphabetical lists
> A teacher has a class register and a pile of marked tests, both in surname order. She runs a finger down each: if the register name comes first alphabetically she moves down the register, if the test comes first she moves to the next test, and when they match she records the mark.
>
> **How it maps:** the two lists are the sorted inputs and the fingers are the two positions in the merge. Moving whichever finger points at the smaller key is the merge step, and each finger only ever moves forwards, so the work grows with the length of both lists.
>
> **Where it stops:** if the lists arrive unsorted, someone must sort them first, and that sort can cost more than the merge. Duplicate surnames on both sides also force the real algorithm to revisit a group of matches, which a single pass of two fingers does not show.

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

`customers` comes out of its primary-key index already in `id` order, and only the 30,066 pending orders need sorting, in memory. The run time was close to the hash join's, and so were the planner's cost estimates for the two plans; the hash join was still estimated slightly cheaper, which is why it was the default choice.

## Key takeaways
- Merge joins need compatible sorted inputs and an eligible equality condition in PostgreSQL.
- The miniature assumes unique left keys; a general implementation must handle duplicate groups and output size.

## Further reading
- [Hash join — Wikipedia](https://en.wikipedia.org/wiki/Hash_join)
- [Sort-merge join — Wikipedia](https://en.wikipedia.org/wiki/Sort-merge_join)
- [Nested loop join — Wikipedia](https://en.wikipedia.org/wiki/Nested_loop_join)
- [Planner/optimiser: join strategies — PostgreSQL docs](https://www.postgresql.org/docs/18/planner-optimizer.html)
- [Resource consumption: work_mem and hash_mem_multiplier — PostgreSQL docs](https://www.postgresql.org/docs/18/runtime-config-resource.html)

