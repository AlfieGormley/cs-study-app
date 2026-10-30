---
id: qp-explain-loops
title: Inclusive time, loops and row errors
level: intermediate
minutes: 4
sourceLesson: qp-reading-explain
summary: Three rules for reading EXPLAIN ANALYZE numbers: times include children, rows and time are per loop, and the lowest big estimate error is the root cause.
---

Examples use PostgreSQL 18 and the module's scaled-up shop tables (1,000,000 orders, 100,000 customers; the first lesson lists them). Plans are abbreviated and illustrative: real plans and timings depend on the data, statistics, settings, cache state and version. Assume serial execution.

## Three rules for the numbers

### 1. Costs and times are cumulative

A node's cost and time **include its children's**. To find the time spent in one node itself (its *exclusive* time), subtract its children. From the illustrative cities query:

```
Hash Join  (actual time=12.237..44.658)
-> Seq Scan on orders o
     (actual time=0.013..25.815)
-> Hash  (actual time=12.038..12.038)
```

```formula reference
t_excl = t_node − Σ t_child
where
t_excl: the node's exclusive time: the time spent in the node itself, in milliseconds (ms)
t_node: the node's inclusive time, the second number of its `actual time`
t_child: a child's inclusive time, the second number of its `actual time`
Σ: sum: add up the term for every child
ms: millisecond, a thousandth of a second
In words: a node's own time is its reported time minus its children's reported times. Here 44.7 ms for the Hash Join, less 25.8 ms and 12.0 ms for its children, leaves about 6.8 ms of actual joining.
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

```formula reference
n_total = n_loop × L
where
n_total: the total number of rows the node produced across all its executions
n_loop: the `rows` figure: the average number of rows per execution
L: the `loops` figure: the number of times the node was executed, once per outer row for the inner side of a nested loop
In words: multiply the per-loop rows (and, likewise, the per-loop time) by loops. Here 200 lookups of 3 rows each is 600 rows, and 200 lookups of about a microsecond each is about 0.2 ms.
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

The Seq Scan on `imports` expected 1 row and got 600,000. Measure a gap as a ratio, whichever way round is bigger: here the estimate was 600,000 times too low, far beyond the 10x that marks a serious error. A zero estimate or zero actual count needs direct inspection instead of division.

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

