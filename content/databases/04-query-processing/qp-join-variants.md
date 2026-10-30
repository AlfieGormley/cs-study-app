---
id: qp-join-variants
title: Join choices and outer, semi and anti variants
level: intermediate
minutes: 3
sourceLesson: qp-join-algorithms
summary: How nested loop, hash and merge joins compare, and the outer, semi and anti join variants that appear in plans.
---

Examples use PostgreSQL 18 and the module's scaled-up shop tables (1,000,000 orders, 100,000 customers; the first lesson lists them). Plans are abbreviated and illustrative: real plans and timings depend on the data, statistics, settings, cache state and version. Assume serial execution.

## Choosing between them

| | Nested loop | Hash | Merge |
|---|---|---|---|
| Join condition | Any | Equality | Equality |
| Best when | Small outer, indexed inner | Large unsorted inputs | Inputs already sorted |
| Memory | Little | Build side | Little (if presorted) |
| Internal path order | May preserve outer | None promised | May preserve merge keys |

The illustrative plan costs show why an access path can matter. Joining pending orders to customers:

| Plan | Estimated cost |
|---|---|
| Hash join | 23,290 |
| Merge join | 25,539 |
| Nested loop + index | 30,572 |
| Nested loop, no index | 46,172,536 |

Without an index on the inner side, the nested loop is about 2,000 times more expensive. That's the plan you get when an index is missing **and** no equality condition exists, or when the planner wrongly believes the outer side has one row.

At larger scale, joining all 1,000,000 orders to their 3,000,000 order items with no index on `order_items.order_id`, one illustrative run had the hash join (8 batches, 587 ms) beat a merge join that had to sort 3 million rows through a 35 MB temporary file (850 ms). With an index on `order_items(order_id)`, a merge join can read both inputs in key order without that sort, so the comparison can change; measure on your own data.

A physical path may provide useful ordering to another node, but SQL results have a guaranteed order only with ORDER BY. Outer joins and duplicate groups can limit which path ordering is useful.

## Outer, semi and anti joins

All three algorithms come in variants for other join types, and you'll see the names in plans:

- `Hash Left Join`, `Merge Full Join`: outer joins. Postgres can't run a `FULL OUTER JOIN` as a nested loop, because the nested loop has no cheap way to remember which inner rows never matched.
- `Semi Join`: from `EXISTS` or `IN`. Stops at the first matching row for each outer row. The planner may instead remove duplicates from the subquery's rows and use an ordinary join; in a PostgreSQL 18.6 test, `EXISTS` over all orders became a HashAggregate of customer IDs feeding a plain Hash Join.
- `Anti Join`: from `NOT EXISTS`. Emits outer rows with no match.
- `Hash Right Join`: the planner swapped sides so the smaller input is hashed, even though the SQL said `LEFT JOIN`.

## Key takeaways
- Join cost depends on outer cardinality, input ordering, memory and usable access paths.
- Join variants preserve different rows; input swaps can change the displayed direction, and only ORDER BY promises result order.

## Further reading
- [Hash join — Wikipedia](https://en.wikipedia.org/wiki/Hash_join)
- [Sort-merge join — Wikipedia](https://en.wikipedia.org/wiki/Sort-merge_join)
- [Nested loop join — Wikipedia](https://en.wikipedia.org/wiki/Nested_loop_join)
- [Planner/optimiser: join strategies — PostgreSQL docs](https://www.postgresql.org/docs/18/planner-optimizer.html)
- [Resource consumption: work_mem and hash_mem_multiplier — PostgreSQL docs](https://www.postgresql.org/docs/18/runtime-config-resource.html)


