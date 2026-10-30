---
id: qp-pull-and-blocking
title: Pulling rows and breaking pipelines
level: basic
minutes: 4
sourceLesson: qp-execution
summary: How operators pull rows from their children one at a time, why LIMIT can stop a scan early, and which operators must read everything first.
---

Examples use PostgreSQL 18 and the module's scaled-up shop tables (1,000,000 orders, 100,000 customers; the first lesson lists them). Plans are abbreviated and illustrative: real plans and timings depend on the data, statistics, settings, cache state and version. Assume serial execution.

## The iterator (Volcano) model

How do the operators pass rows to each other? Most row-store databases, Postgres included, use the **iterator model**, named after Goetz Graefe's Volcano system from around 1990. Every operator implements the same tiny interface:

- `open()`: get ready (allocate memory, open children).
- `next()`: return the next row, or "done".
- `close()`: release resources.

The top operator calls `next()` on its child, which calls `next()` on *its* child, and so on down to a scan that reads a row from a page. Rows are **pulled** up the tree one at a time.

Python generators illustrate this pull behaviour. Use a non-negative integer limit; this miniature demonstrates pull control rather than every SQL LIMIT validation rule:

```python
reads = 0

def seq_scan(table):
    global reads
    # Count rows pulled, not rows kept.
    for row in table:
        reads += 1
        yield row

def filter_rows(child, pred):
    for row in child:
        # Reject before the next operator.
        if pred(row):
            yield row

def limit(child, n):
    if n == 0:
        return
    for i, row in enumerate(child, 1):
        yield row
        # Stop pulling from the child.
        if i == n:
            return
```

The first block defines the operators. Initialise this six-row list before running the following plan; only IDs 2, 4 and 5 are pending. The counter counts visits, including rejected rows.

```python
orders = [
    {"id": i, "status":
     "pending" if i in (2, 4, 5)
     else "shipped"}
    for i in range(1, 7)
]
```

Run a `LIMIT 2` over this list:

```python
plan = limit(
    filter_rows(
        seq_scan(orders),
        lambda r: r["status"] == "pending"),
    2)

for row in plan:
    print(row["id"])
print("rows read:", reads)
```

```
2
4
rows read: 4
```

The scan stopped after **four** rows, not six. Once `limit` has its two rows it stops asking, so nobody below it does any more work. Postgres does the same thing. An illustrative plan for `SELECT * FROM orders WHERE status = 'pending' LIMIT 5`:

```
Limit (actual rows=5.00)
  Buffers: shared hit=2
-> Seq Scan on orders
     (actual rows=5.00)
     Filter: (status = 'pending'::text)
     Rows Removed by Filter: 80
```

In this illustrative run Postgres read 85 rows and 2 pages out of 7,353, and finished in 0.012 ms. How many rows it reads before finding five depends on where pending rows happen to sit in the table, but it is a tiny fraction either way.

## Pipelines and blocking operators

Some operators can emit their first row before seeing all of their input. A scan, a filter and the probe side of a hash join all **stream**: rows flow straight through.

Others are **blocking** (also called pipeline breakers). The full operators listed here consume their input before producing results (an Incremental Sort instead blocks only on each presorted group):

- **Sort**: the smallest value might be the last row read.
- **Hash** (the build side of a hash join): the table must be complete before any probe can trust a miss.
- **HashAggregate**: a group's count isn't final until every row is seen.

> [!analogy] Real-world analogy: a sandwich counter and a marking pile
> At a sandwich counter, the person wrapping asks the filler for the next sandwich, who asks the bread-slicer for two slices. Nobody makes more than is asked for, so when the last customer is served the line simply stops. A teacher ranking exam papers by mark is different: she cannot announce the top paper until she has seen every paper.
>
> **How it maps:** each worker is an operator and "next, please" is the `next()` call travelling down the plan. Stopping when customers stop asking is LIMIT ending a streaming pipeline. The teacher is a blocking operator such as Sort or HashAggregate, which must consume all its input before emitting a row.
>
> **Where it stops:** real operators do not run as separate people at the same time; in PostgreSQL's executor one process calls each operator in turn. Some engines also push batches of rows upwards instead of pulling one at a time.

This is why `EXPLAIN` shows two costs for each node, like `cost=0.00..19853.00`. The first number is the **startup cost** (work before the first row), the second the **total cost** (work for all rows). A Sort has a high startup cost; a Seq Scan's is zero. When a query has `LIMIT`, the planner prefers plans with low startup cost, because it may never need the total.

## Key takeaways
- A LIMIT stops a streaming subtree by ceasing to request rows.
- Full sorts, hash builds and hash aggregation consume their inputs first; top-N sorting saves memory without avoiding the scan.

## Further reading
- [Overview of PostgreSQL internals: the path of a query](https://www.postgresql.org/docs/18/query-path.html)
- [The PostgreSQL executor](https://www.postgresql.org/docs/18/executor.html)
- [Using EXPLAIN — PostgreSQL docs](https://www.postgresql.org/docs/18/using-explain.html)
- [Query plan — Wikipedia](https://en.wikipedia.org/wiki/Query_plan)
- [Parallel query — PostgreSQL docs](https://www.postgresql.org/docs/18/parallel-query.html)

