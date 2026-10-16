---
id: qp-join-variants
title: Join choices and outer, semi and anti variants
level: intermediate
minutes: 3
sourceLesson: qp-join-algorithms
summary: Join choices and outer, semi and anti variants using explicit models and assumptions.
---

These examples use PostgreSQL 18. SQL Fundamentals supplies the shop relations: `customers(id, name, email, city, country)`, `orders(id, customer_id, status, ordered_on, total)`, `products(id, price)` and `order_items(order_id)`. IDs join orders to customers and items to orders. Dates use `date`, IDs use `integer`, and totals use `numeric`. Each query fragment uses these names; ellipses and standalone WHERE clauses need the surrounding SELECT shown by their context.

All historical plans and figures below are illustrative model inputs. Actual execution depends on version, workload and settings.

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

At larger scale, joining all 1,000,000 orders to their 3,000,000 order items, the hash join (8 batches, 587 ms) beat a merge join that had to sort 3 million rows through a 35 MB temporary file (850 ms).

A physical path may provide useful ordering to another node, but SQL results have a guaranteed order only with ORDER BY. Outer joins and duplicate groups can limit which path ordering is useful.

## Outer, semi and anti joins

All three algorithms come in variants for other join types, and you'll see the names in plans:

- `Hash Left Join`, `Merge Full Join`: outer joins. Postgres can't run a `FULL OUTER JOIN` as a nested loop, because the nested loop has no cheap way to remember which inner rows never matched.
- `Semi Join`: from `EXISTS` or `IN`. Stops at the first matching row for each outer row.
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


