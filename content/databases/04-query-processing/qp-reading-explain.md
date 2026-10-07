---
id: qp-reading-explain
title: Reading EXPLAIN plans (Postgres)
level: intermediate
minutes: 15
summary: How to read PostgreSQL EXPLAIN and EXPLAIN ANALYZE output field by field, find where the time really went, spot misestimates, and recognise the red flags that point to a fix.
---

> [!note] Content gap: benchmark provenance
> Reproducible measurement records for the original laptop timings were not available to this audit, so empirical performance claims are omitted. The plan numbers below are retained only as illustrative inputs for learning EXPLAIN, not verified measurements or promised speedups. Measure your own representative workload.


`EXPLAIN` is the single most useful tool for understanding a slow query. It shows the plan the optimiser chose, with its estimates. `EXPLAIN ANALYZE` also runs the query and shows what actually happened. The skill is reading the output quickly and knowing which numbers matter.

The following abbreviated PostgreSQL 18-style plan fragments are illustrative exercises.

## The variants

```sql
-- plan and estimates only; doesn't run
EXPLAIN SELECT ...;

-- runs it, adds actual rows, time, buffers
EXPLAIN ANALYZE SELECT ...;

-- the options worth knowing
EXPLAIN (ANALYZE, BUFFERS, VERBOSE,
         SETTINGS, FORMAT JSON) SELECT ...;
```

- **ANALYZE** executes the statement and reports actual figures.
- **BUFFERS** reports pages touched. Since Postgres 18 it's included automatically with ANALYZE; on older versions, ask for it.
- **VERBOSE** adds output column lists and schema-qualified names.
- **SETTINGS** lists any planner settings that differ from the defaults. Very useful when someone sends you a plan.
- **FORMAT JSON** gives machine-readable output for visualisers.
- **TIMING OFF** keeps row counts but skips per-node timing, which can have noticeable overhead on some systems.

> [!warning] EXPLAIN ANALYZE really runs the statement
> `EXPLAIN ANALYZE DELETE FROM orders` deletes the orders. Wrap data-changing statements in a transaction you roll back:
> `BEGIN; EXPLAIN ANALYZE DELETE ...; ROLLBACK;`
> Rollback does not undo sequence increments or external side effects from functions or triggers. Use disposable data when those effects are possible.

## Anatomy of one node

```sql
EXPLAIN ANALYZE
SELECT * FROM orders
WHERE status = 'pending';
```

```
Seq Scan on orders
  (cost=0.00..19853.00 rows=30767 width=26)
  (actual time=0.025..26.566
   rows=30066.00 loops=1)
  Filter: (status = 'pending'::text)
  Rows Removed by Filter: 969934
  Buffers: shared hit=7011 read=342
Planning Time: 0.133 ms
Execution Time: 27.149 ms
```

| Field | Meaning |
|---|---|
| `cost=0.00..19853.00` | Estimated startup..total cost, in planner units |
| `rows=30767` | Estimated rows output |
| `width=26` | Estimated average row size in bytes |
| `actual time=0.025..26.566` | Real ms to first row..last row |
| `rows=30066.00` | Real rows output, per loop |
| `loops=1` | Times this node was executed |
| `Rows Removed by Filter` | Rows read but rejected |
| `Buffers: shared hit` | Pages found in Postgres's cache |
| `Buffers: shared read` | Pages fetched from the OS or disk |

From this one node: the estimate (30,767) was within 2% of the truth, the scan read every one of the 7,353 pages (7,011 + 342), and it threw away 97% of the rows it read. The last fact is the important one. Reading a million rows to keep 30,000 is a sign that an index might help (lesson 5).

The `.00` on actual rows is new in Postgres 18. It's there because `rows` is an **average per loop**, and averages needn't be whole numbers, as you'll see below.

## Three rules for the numbers

### 1. Costs and times are cumulative

A node's cost and time **include its children's**. To find the time spent in one node itself (its *exclusive* time), subtract its children. From the cities query in lesson 1:

```
Hash Join  (actual time=12.237..44.658)
-> Seq Scan on orders o
     (actual time=0.013..25.815)
-> Hash  (actual time=12.038..12.038)
```

```
exclusive = 44.658 - 25.815 - 12.038
          = 6.8 ms in the join itself
```

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

```
inner rows  = 3.00 x 200 = 600
inner time ~ 0.001 ms x 200 = 0.2 ms
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

The Seq Scan on `imports` expected 1 row and got 600,000. That's the root cause. The nested loop above it was a reasonable choice for 1 row and a poor one for 600,000: 3.6 million page accesses. After `ANALYZE imports`, the planner chose a hash join with about 19,000.

> [!tip] Estimates the other way are dangerous too
> An overestimate can make the planner reject an index and scan a whole table. Any big gap is worth explaining.

## Red flags and what they mean

| You see | It suggests |
|---|---|
| Estimate off by 10x+ | Stale stats, correlated columns, or a function on a column |
| Large `Rows Removed by Filter` | A missing or unusable index |
| `Sort Method: external merge  Disk:` | Sort spilled; `work_mem` too small, or an index could supply the order |
| `Batches:` greater than 1 | Hash spilled to temp files |
| High `loops` on an expensive inner node | Nested loop over too many outer rows |
| `Heap Fetches` high on an Index Only Scan | Visibility map out of date; vacuum |
| `Heap Blocks: lossy` | Bitmap too big for `work_mem`; rows rechecked per page |
| `Buffers: ... read` dominates | Data not cached; cold cache or working set too big |

### Sorts that spill

```sql
EXPLAIN ANALYZE
SELECT * FROM orders ORDER BY total;
```

```
Sort  (actual time=238.774..288.495
       rows=1000000.00 loops=1)
  Sort Key: total
  Sort Method: external merge
    Disk: 36344kB
  Buffers: temp read=9084 written=9101
```

With the default 4 MB `work_mem`, sorting a million rows wrote 36 MB to temporary files. Interestingly, `work_mem = 64MB` *still* spilled: the in-memory quicksort needed 71 MB (`Memory: 71451kB` at 256 MB), because in-memory sorting carries per-row overhead the compact on-disk format doesn't. With an `ORDER BY ... LIMIT 10` instead, the plan uses `top-N heapsort  Memory: 26kB` and never spills.

### Index Cond versus Filter

```
Index Scan using customers_email_pattern_idx
  Index Cond: ((email ~>=~ 'c42@'::text)
    AND (email ~<~ 'c42A'::text))
  Filter: (email ~~ 'c42@%'::text)
```

**Index Cond** is used to navigate the index, so it limits which entries are read. **Filter** is checked on each row after it's fetched. A condition that appears only under Filter isn't narrowing the index search at all. Here the `LIKE 'c42@%'` prefix was converted into a range for the index, then rechecked as a filter.

### New in Postgres 18: Index Searches

```
Index Scan Backward
  using orders_date_cust_idx
  Index Cond: (customer_id = 42)
  Index Searches: 1031
```

`Index Searches` counts how many separate descents into the index happened. Normally it's 1 per loop. Here, an index on `(ordered_on, customer_id)` was used for a query on `customer_id` alone, and Postgres 18's **skip scan** made 1,031 descents, one per distinct date it had to check. Lesson 5 explains why a better index needs just 1.

## Reading BUFFERS

Each buffer is an 8 KB page, so `Buffers: shared hit=7011 read=342` is about 55 MB served from shared memory and 2.7 MB from outside it.

- **hit**: already in shared buffers.
- **read**: requested from the operating system. It might still have come from the OS page cache, so a `read` is not necessarily a disk read. Turn on `track_io_timing` to see the real I/O time.
- **dirtied / written**: pages this query modified or had to write out (for example, setting hint bits on freshly loaded rows).
- **temp read / written**: temporary files from spilling sorts and hashes.

Buffer access counts complement timing, but they are not independent of system state. The hit/read split depends on cache warmth, and repeated accesses may revisit the same page. The illustrative totals (3.6 million versus 19,000) suggest very different work, but do not imply that every access becomes a separate disk read on a cold cache.

## A method for slow queries

1. Get the real plan: `EXPLAIN (ANALYZE, BUFFERS)` against production-sized data. A plan from a 1,000-row dev table tells you little.
2. Note the total `Execution Time`.
3. Find the nodes with the largest **exclusive** time (subtract children, multiply by loops).
4. Walk up from the leaves looking for the first big estimate error.
5. Check the red flags table.
6. Change one thing (an index, ANALYZE, a rewrite), then re-run and compare buffers and time.

For long plans, paste the text into a visualiser such as [explain.depesz.com](https://explain.depesz.com/) or [explain.dalibo.com](https://explain.dalibo.com/), which compute exclusive times and highlight misestimates for you.

To catch slow plans in production without running EXPLAIN by hand, use the **auto_explain** module, which logs the plans of statements slower than a threshold, and **pg_stat_statements**, which records total time and calls per normalised query so you know which queries to look at first.

> [!note] Other databases
> MySQL has `EXPLAIN ANALYZE` (8.0.18+) with a similar tree format. SQLite's `EXPLAIN QUERY PLAN` is much terser:
> `SCAN o`, then `SEARCH c USING INTEGER PRIMARY KEY (rowid=?)`, then `USE TEMP B-TREE FOR GROUP BY`. That was our cities query: a nested loop of primary-key lookups, with a temporary B-tree for the grouping.

## Caveats

- EXPLAIN ANALYZE doesn't send the result rows to the client, so network transfer time isn't included. Postgres 17 added a `SERIALIZE` option to measure the cost of converting rows to output format.
- The first run may read from disk and the second from cache. Run twice, and look at `read` against `hit`.
- Per-node timing has overhead. If the plan has millions of tiny loops, use `TIMING OFF` and rely on row counts and buffers.

## Key takeaways
- `EXPLAIN` shows estimates; `EXPLAIN ANALYZE` runs the query and adds actual rows, times, loops and (since Postgres 18, by default) buffers.
- Times and costs include children. Subtract children to get a node's own time, and multiply per-loop figures by `loops`.
- The lowest node where estimated and actual rows differ by 10x or more is usually the root cause of a bad plan.
- Learn the red flags: large Rows Removed by Filter, external merge sorts, multiple hash batches, high loops, Heap Fetches.
- Compare buffer accesses as well as time. Interpret cache hits, reads and repeated visits separately.

## Further reading
- [Using EXPLAIN — PostgreSQL docs](https://www.postgresql.org/docs/current/using-explain.html)
- [EXPLAIN command reference — PostgreSQL docs](https://www.postgresql.org/docs/current/sql-explain.html)
- [auto_explain — PostgreSQL docs](https://www.postgresql.org/docs/current/auto-explain.html)
- [pg_stat_statements — PostgreSQL docs](https://www.postgresql.org/docs/current/pgstatstatements.html)
- [PostgreSQL 18 release notes](https://www.postgresql.org/docs/18/release-18.html)
- [EXPLAIN QUERY PLAN — SQLite docs](https://www.sqlite.org/eqp.html)
