---
id: qp-execution
title: How a query executes
level: basic
minutes: 12
summary: The journey from SQL text to rows. Parsing, rewriting, planning and execution, the plan tree, the iterator model that streams rows between operators, and why the page is the unit of cost.
---

> [!note] Content gap: benchmark provenance
> Reproducible measurement records for the original laptop timings were not available to this audit, so empirical performance claims are omitted. The plan numbers below are retained only as illustrative inputs for learning EXPLAIN, not verified measurements or promised speedups. Measure your own representative workload.


SQL is **declarative**: you say *what* rows you want, not *how* to find them. Something has to turn that description into a concrete program of loops, lookups and sorts. That something is the query processor, and it is the reason the same query can take 2 milliseconds on Monday and 20 seconds on Tuesday.

This module uses the shop schema from SQL Fundamentals, scaled up so that performance actually matters:

```
customers   100,000 rows   1,029 pages
products     10,000 rows      74 pages
orders     1,000,000 rows  7,353 pages
order_items 3,000,000 rows 16,217 pages
```

The examples use PostgreSQL 18 plan terminology and assume serial execution (`max_parallel_workers_per_gather = 0`) for readability. Plan fragments are abbreviated. The supplied row and page counts define the illustrative dataset.

## The pipeline

Every statement goes through the same stages. The names below are PostgreSQL's, but MySQL, SQL Server and Oracle all have the same shape.

```
 SQL text
    |
 [Parser]     syntax -> parse tree
    |
 [Analyser]   names, types -> query tree
    |
 [Rewriter]   expand views and rules
    |
 [Planner]    choose the cheapest plan
    |
 [Executor]   run the plan, emit rows
    |
 result rows
```

1. **Parser.** Checks the grammar and builds a parse tree. A typo like `SELEC` fails here, before any table is touched.
2. **Analyser** (or binder). Looks names up in the system catalog: does `orders` exist, does it have a `status` column, what type is it? It produces a query tree with every name resolved. "Column does not exist" errors come from here.
3. **Rewriter.** Applies rules. The main one is **view expansion**: a query against a view is rewritten into a query against the view's underlying tables, so the planner can optimise the whole thing together. Row-level security policies are added here too.
4. **Planner/optimiser.** Considers many ways to run the query and estimates the cost of each. It outputs one **plan**.
5. **Executor.** Runs the plan and streams rows back to the client.

Parsing and planning a typical OLTP query take tens of microseconds to a millisecond. Execution is where the time usually goes, and planning is what decides how much time execution needs.

> [!note] Prepared statements skip work
> A prepared statement is parsed and analysed once. Later executions can reuse a cached plan, which saves the planning cost on every call. Lesson 6 covers the trap this sets.

## A plan is a tree of operators

Take this question: "which three cities have the most pending orders?"

```sql
SELECT c.city, count(*) AS n
FROM orders o
JOIN customers c ON c.id = o.customer_id
WHERE o.status = 'pending'
GROUP BY c.city
ORDER BY n DESC
LIMIT 3;
```

`EXPLAIN` shows the plan PostgreSQL chose. Simplified, it is:

```
Limit
-> Sort  [count(*) DESC, top-N]
   -> HashAggregate  [by c.city]
      -> Hash Join  [o.customer_id = c.id]
         -> Seq Scan on orders o
              Filter: status = 'pending'
         -> Hash
            -> Seq Scan on customers c
```

Read it from the **leaves upwards**. Each node is an operator that takes rows from its children and produces rows for its parent:

| Node | Rows out |
|---|---|
| Seq Scan orders | 30,066 of 1,000,000 |
| Seq Scan customers | 100,000 |
| Hash Join | 30,066 |
| HashAggregate | 8 (one per city) |
| Sort, Limit | 3 |

The whole query took about 47 ms. Almost all of it went on the two scans, reading 8,382 pages between them.

Notice what the planner did with your SQL. You wrote a join and then a filter, but the plan filters `orders` **inside the scan**, before the join. That's **predicate pushdown**: throwing rows away as early as possible so later operators handle less data. The logical order of SQL clauses (FROM, WHERE, GROUP BY, SELECT, ORDER BY, LIMIT) defines what the answer *means*; the planner is free to compute it in any order that gives the same answer.

## Logical and physical operators

The SQL describes **logical** operations: scan a table, join two inputs, group. The plan picks a **physical** algorithm for each one.

| Logical | Physical choices in Postgres |
|---|---|
| Read a table | Seq Scan, Index Scan, Index Only Scan, Bitmap Heap Scan |
| Join | Nested Loop, Hash Join, Merge Join |
| Group | HashAggregate, GroupAggregate |
| Order | Sort, Incremental Sort, or an index already in order |

Choosing between these is the optimiser's job, and the next three lessons are about how it chooses.

## The iterator (Volcano) model

How do the operators pass rows to each other? Most row-store databases, Postgres included, use the **iterator model**, named after Goetz Graefe's Volcano system from around 1990. Every operator implements the same tiny interface:

- `open()`: get ready (allocate memory, open children).
- `next()`: return the next row, or "done".
- `close()`: release resources.

The top operator calls `next()` on its child, which calls `next()` on *its* child, and so on down to a scan that reads a row from a page. Rows are **pulled** up the tree one at a time.

Python generators behave exactly like this, so here is a working miniature:

```python
reads = 0

def seq_scan(table):
    global reads
    for row in table:
        reads += 1
        yield row

def filter_rows(child, pred):
    for row in child:
        if pred(row):
            yield row

def limit(child, n):
    if n == 0:
        return
    for i, row in enumerate(child, 1):
        yield row
        if i == n:
            return
```

Run a `LIMIT 2` over six orders where ids 2, 4 and 5 are pending:

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

Postgres read 85 rows and 2 pages out of 7,353, and finished in 0.012 ms.

## Pipelines and blocking operators

Some operators can emit their first row before seeing all of their input. A scan, a filter and the probe side of a hash join all **stream**: rows flow straight through.

Others are **blocking** (also called pipeline breakers). They must consume their entire input before producing anything:

- **Sort**: the smallest value might be the last row read.
- **Hash** (the build side of a hash join): the table must be complete before any probe can trust a miss.
- **HashAggregate**: a group's count isn't final until every row is seen.

This is why `EXPLAIN` shows two costs for each node, like `cost=0.00..19853.00`. The first number is the **startup cost** (work before the first row), the second the **total cost** (work for all rows). A Sort has a high startup cost; a Seq Scan's is zero. When a query has `LIMIT`, the planner prefers plans with low startup cost, because it may never need the total.

## Pages: the unit of cost

Tables and indexes are stored in fixed-size **pages** (normally 8 KiB in PostgreSQL and 16 KiB in MySQL InnoDB; both have configurable page-size options). The `orders` table holds about 136 rows per page. The database reads whole pages, never single rows, so the main question for any plan is **how many pages does it touch, and are they in memory?**

- A page found in Postgres's shared buffer cache is a **hit**: a memory access, well under a microsecond.
- A page that isn't is a **read**. It might come from the operating system's cache (microseconds) or from the SSD (tens to hundreds of microseconds).

Reading pages in order (a sequential scan) is cheaper per page than jumping around (random access), because the storage and the OS can read ahead. Postgres encodes that by charging `seq_page_cost = 1` per sequential page and `random_page_cost = 4` per random one by default. Lesson 3 shows how those numbers turn into a plan's cost.

## Other execution models

The iterator model pays a function call per row per operator. That overhead is noticeable for analytical queries over billions of rows, so other designs exist:

- **Vectorised execution** (DuckDB, ClickHouse, Snowflake): `next()` returns a batch of around a thousand values from one column at a time, so loops are tight and CPU-cache friendly.
- **Compiled execution** (HyPer, Umbra, SingleStore): the plan is compiled to machine code that fuses operators into a single loop. Postgres has a limited form of this: it can **JIT-compile** expressions with LLVM for expensive queries.
- **Parallel execution**: Postgres can split a scan across worker processes and gather their results through a `Gather` node. You'll see `Gather` and `Parallel Seq Scan` in real plans on big tables.

The ideas in this module (plans as trees, join algorithms, cost estimation) apply to all of them.

## Key takeaways
- A query passes through parse, analyse, rewrite, plan and execute. Planning decides how much work execution must do.
- A plan is a tree of physical operators. Read it from the leaves up; rows flow upwards.
- In the iterator model each operator pulls rows from its children with `next()`, so a `LIMIT` stops the work beneath it early.
- Sort, hash builds and hash aggregation are blocking. That shows up as high startup cost.
- Cost is mostly pages touched, and whether they were cached. Sequential page reads are cheaper than random ones.

## Further reading
- [Overview of PostgreSQL internals: the path of a query](https://www.postgresql.org/docs/current/query-path.html)
- [The PostgreSQL executor](https://www.postgresql.org/docs/current/executor.html)
- [Using EXPLAIN — PostgreSQL docs](https://www.postgresql.org/docs/current/using-explain.html)
- [Query plan — Wikipedia](https://en.wikipedia.org/wiki/Query_plan)
- [Parallel query — PostgreSQL docs](https://www.postgresql.org/docs/current/parallel-query.html)
