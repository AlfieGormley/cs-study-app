---
id: qp-explain-loops
title: Inclusive time, loops and row errors
level: intermediate
minutes: 5
sourceLesson: qp-reading-explain
summary: Inclusive time, loops and row errors with worked examples and explicit assumptions.
---

These examples use PostgreSQL 18. SQL Fundamentals supplies the shop relations: `customers(id, name, email, city, country)`, `orders(id, customer_id, status, ordered_on, total)`, `products(id, price)` and `order_items(order_id)`. IDs join orders to customers and items to orders. Dates use `date`, IDs use `integer`, and totals use `numeric`. Each query fragment uses these names; ellipses and standalone WHERE clauses need the surrounding SELECT shown by their context.

All historical plan fragments and timings in this unit are **illustrative inputs**, not reproduced benchmarks or promises. Their row/page counts describe a hypothetical dataset; actual plans vary with statistics, indexes, settings, cache state and PostgreSQL version. Assume serial execution unless a parallel worker process is shown.

## Three rules for the numbers

### 1. Costs and times are cumulative

A node's cost and time **include its children's**. To find the time spent in one node itself (its *exclusive* time), subtract its children. From the illustrative cities query:

```
Hash Join  (actual time=12.237..44.658)
-> Seq Scan on orders o
     (actual time=0.013..25.815)
-> Hash  (actual time=12.038..12.038)
```

```formula
t_excl = t_node − Σ t_child
t_excl = (44.658 − 25.815 − 12.038) ms
t_excl ≈ 6.8 ms
where
t_excl: the node's exclusive time: the time spent in the node itself, in milliseconds (ms)
t_node: the node's inclusive time, the second number of its `actual time`, here 44.658 ms for the Hash Join
t_child: a child's inclusive time, the second number of its `actual time`: 25.815 ms for the orders scan and 12.038 ms for the Hash
Σ: sum: add up the term for every child
≈: approximately equal to
ms: millisecond, a thousandth of a second
In words: of the 44.7 ms reported for the Hash Join, about 6.8 ms was spent joining; the rest was its children.
```

For serial totals, multiply both the parent's and each child's average time by their own `loops` before subtracting; the displayed example has one loop at every node. With parallel execution, loops may include executions by several processes. Multiplying averages by loops gives aggregate instrumented execution time, not elapsed wall-clock time; overlapping worker times cannot simply be subtracted from the leader time. Worker details, rescans and instrumentation overhead make exclusive-time subtraction only a diagnostic approximation.

So most of the 47 ms went on the orders scan (26 ms), not the join.

### 2. Multiply by loops

`actual time` and `rows` are **per loop**. The inner side of a nested loop runs once per outer row:

```
Nested Loop  (actual rows=600.00 loops=1)
-> Index Only Scan using orders_pkey
     (actual rows=200.00 loops=1)
-> Index Scan using order_items_order_id_idx
     (actual time=0.000..0.001
      rows=3.00 loops=200)
     Index Searches: 200
     Buffers: shared hit=1191 read=9
```

```formula
n_total = n_loop × L
n_total = 3.00 × 200 = 600
t_total ≈ t_loop × L
t_total ≈ 0.001 ms × 200 = 0.2 ms
where
n_total: the total number of rows the node produced across all its executions
n_loop: the `rows` figure: the average number of rows per execution, here 3.00
L: the `loops` figure: the number of times the node was executed, here 200 (once per outer row)
t_total: the total time spent in the node across all executions, in milliseconds (ms)
t_loop: the per-execution time, the second number of `actual time`, here 0.001 ms
≈: approximately equal to (the per-loop time is a rounded average)
ms: millisecond, a thousandth of a second
In words: 200 lookups of 3 rows each is 600 rows, and 200 lookups of about a microsecond each is about 0.2 ms.
```

`Buffers` are already **totals** across all loops, not per loop: 1,200 page accesses, 6 per lookup.

### 3. Compare estimated rows with actual rows

This is the most important check. Walk up from the leaves and find the **lowest node where the estimate and the actual differ by 10x or more**. Everything above it was planned on wrong information.

```
Nested Loop  (rows=3)
  (actual rows=1800000.00)
-> Seq Scan on imports m  (rows=1)
     (actual rows=600000.00)
     Filter: (batch = 2)
-> Index Scan using order_items_order_id_idx
     (rows=3) (actual rows=3.00
      loops=600000)
Buffers: shared hit=3589400
```

The Seq Scan on `imports` expected 1 row and got 600,000. When both counts are positive, measure the gap as a ratio, whichever way round is bigger. A zero estimate or zero actual count needs direct inspection instead of division:

```formula
r = max(n_act / n_est, n_est / n_act)
r = max(600,000 / 1, 1 / 600,000)
r = 600,000
where
r: the misestimate factor: how many times too high or too low the estimate was; 1 means exact
n_act: the actual rows per loop, from `actual rows`, here 600,000
n_est: the estimated rows, the `rows` figure in the first brackets, here 1
max: the larger of the two values
In words: the estimate was 600,000 times too low, far beyond the 10x that marks a serious error.
```

That's the root cause. The nested loop above it was a reasonable choice for 1 row and a poor one for 600,000: 3.6 million page accesses. After `ANALYZE imports`, the planner chose a hash join with about 19,000.

> [!tip] Estimates the other way are dangerous too
> An overestimate can make the planner reject an index and scan a whole table. Any big gap is worth explaining.

## Key takeaways
- Rows and time are averages per loop; buffers are totals.
- Serial inclusive-time subtraction is approximate; parallel worker time can overlap. Investigate estimate errors from the leaves upwards.

## Further reading
- [Using EXPLAIN — PostgreSQL docs](https://www.postgresql.org/docs/18/using-explain.html)
- [EXPLAIN command reference — PostgreSQL docs](https://www.postgresql.org/docs/18/sql-explain.html)
- [auto_explain — PostgreSQL docs](https://www.postgresql.org/docs/18/auto-explain.html)
- [pg_stat_statements — PostgreSQL docs](https://www.postgresql.org/docs/18/pgstatstatements.html)
- [PostgreSQL 18 release notes](https://www.postgresql.org/docs/18/release-18.html)
- [EXPLAIN QUERY PLAN — SQLite docs](https://www.sqlite.org/eqp.html)

