---
id: qp-plan-operators
title: Read a tree of physical operators
level: basic
minutes: 3
sourceLesson: qp-execution
summary: How a plan is a tree of physical operators, read from the leaves up, and how it can reorder the logical SQL.
---

Examples use PostgreSQL 18 and the module's scaled-up shop tables (1,000,000 orders, 100,000 customers; the first lesson lists them). Plans are abbreviated and illustrative: real plans and timings depend on the data, statistics, settings, cache state and version. Assume serial execution.

## A plan is a tree of operators

Take this question: "which three cities have the most pending orders?"

```sql
-- Group pending orders before top three.
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

In this illustrative run the whole query took about 47 ms. Almost all of it went on the two scans, reading 8,382 pages between them.

Notice what the planner did with your SQL. You wrote a join and then a filter, but the plan filters `orders` **inside the scan**, before the join. That's **predicate pushdown**: throwing rows away as early as possible so later operators handle less data. The logical order of SQL clauses (FROM, WHERE, GROUP BY, SELECT, ORDER BY, LIMIT) defines what the answer *means*; the planner is free to compute it in any order that gives the same answer.

## Logical and physical operators

The SQL describes **logical** operations: scan a table, join two inputs, group. The plan picks a **physical** algorithm for each one.

| Logical | Physical choices in Postgres |
|---|---|
| Read a table | Seq Scan, Index Scan, Index Only Scan, Bitmap Heap Scan |
| Join | Nested Loop, Hash Join, Merge Join |
| Group | HashAggregate, GroupAggregate |
| Order | Sort, Incremental Sort, or an index already in order |

Choosing between these is the optimiser's job, and the following units are about how it chooses.

> [!analogy] Real-world analogy: a recipe and a cook's method
> A recipe says "chop the onions, then fry them with the mince". It does not say whether to use a knife or a food processor, or whether to chop everything before turning on the hob.
>
> **How it maps:** the SQL is the recipe: it fixes what the finished dish must be (the logical operations). The plan is the cook's method: it picks a physical tool for each step (Hash Join or Nested Loop, Seq Scan or Index Scan) and may reorder steps, such as filtering before joining, when the dish comes out the same.
>
> **Where it stops:** a cook can taste and adjust while cooking. A PostgreSQL plan is fixed once execution starts; it does not switch algorithms halfway because the estimates turned out wrong.

## Key takeaways
- Read rows from leaves towards the root; control requests flow down the plan tree.
- A predicate referring only to orders can move below this inner join when semantics are preserved; aggregation reduces rows before the final sort.

## Further reading
- [Overview of PostgreSQL internals: the path of a query](https://www.postgresql.org/docs/18/query-path.html)
- [The PostgreSQL executor](https://www.postgresql.org/docs/18/executor.html)
- [Using EXPLAIN — PostgreSQL docs](https://www.postgresql.org/docs/18/using-explain.html)
- [Query plan — Wikipedia](https://en.wikipedia.org/wiki/Query_plan)
- [Parallel query — PostgreSQL docs](https://www.postgresql.org/docs/18/parallel-query.html)

