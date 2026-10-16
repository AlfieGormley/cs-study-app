---
id: qp-plan-operators
title: Read a tree of physical operators
level: basic
minutes: 3
sourceLesson: qp-execution
summary: Read a tree of physical operators with worked examples and explicit assumptions.
---

These examples use PostgreSQL 18. SQL Fundamentals supplies the shop relations: `customers(id, name, email, city, country)`, `orders(id, customer_id, status, ordered_on, total)`, `products(id, price)` and `order_items(order_id)`. IDs join orders to customers and items to orders. Dates use `date`, IDs use `integer`, and totals use `numeric`. Each query fragment uses these names; ellipses and standalone WHERE clauses need the surrounding SELECT shown by their context.

All historical plan fragments and timings in this unit are **illustrative inputs**, not reproduced benchmarks or promises. Their row/page counts describe a hypothetical dataset; actual plans vary with statistics, indexes, settings, cache state and PostgreSQL version. Assume serial execution unless a parallel worker process is shown.

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

Choosing between these is the optimiser's job, and the following units are about how it chooses.

## Key takeaways
- Read rows from leaves towards the root; control requests flow down the plan tree.
- A predicate referring only to orders can move below this inner join when semantics are preserved; aggregation reduces rows before the final sort.

## Further reading
- [Overview of PostgreSQL internals: the path of a query](https://www.postgresql.org/docs/18/query-path.html)
- [The PostgreSQL executor](https://www.postgresql.org/docs/18/executor.html)
- [Using EXPLAIN — PostgreSQL docs](https://www.postgresql.org/docs/18/using-explain.html)
- [Query plan — Wikipedia](https://en.wikipedia.org/wiki/Query_plan)
- [Parallel query — PostgreSQL docs](https://www.postgresql.org/docs/18/parallel-query.html)

