---
id: qp-query-pipeline
title: From SQL text to a plan
level: basic
minutes: 3
sourceLesson: qp-execution
summary: The stages a PostgreSQL query passes through, from parsing and name resolution to planning and execution.
---

SQL is **declarative**: you say *what* rows you want, not *how* to find them. Something has to turn that description into a concrete program of loops, lookups and sorts. That something is the query processor, and it is the reason the same query can take 2 milliseconds on Monday and 20 seconds on Tuesday.

This module uses the shop tables from SQL Fundamentals, scaled up so that performance actually matters: `customers(id, name, email, city, country)`, `orders(id, customer_id, status, ordered_on, total)`, `products(id, price)` and `order_items(order_id, ...)`.

```
customers   100,000 rows   1,029 pages
products     10,000 rows      74 pages
orders     1,000,000 rows  7,353 pages
order_items 3,000,000 rows 16,217 pages
```

The plans in this module are abbreviated PostgreSQL 18 plans for a generated dataset of about this size. About 3% of orders are pending, 7% cancelled and 90% shipped, spread over 2,400 days from 2020. Customers are spread evenly over eight cities (12,500 each), and each has about ten orders. Treat the row counts and timings as illustrative: a similar dataset on your machine gives similar shapes but different numbers. Assume serial execution (`max_parallel_workers_per_gather = 0`), so no parallel workers appear.

## The pipeline

For an ordinary PostgreSQL optimisable query, the stages are as follows. Utility commands can take different paths; other engines use related architectures with different details.

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
2. **Analyser** (or binder). Looks names up in the system catalog: does `orders` exist, does it have a `status` column, what type is it? It produces PostgreSQL's analysed query tree, with every name resolved. "Column does not exist" errors come from here.
3. **Rewriter.** Applies rules. The main one is **view expansion**: a query against a view is rewritten into a query against the view's underlying tables, so the planner can optimise the whole thing together. Row-level security policies are added here too.
4. **Planner/optimiser.** Considers many ways to run the query and estimates the cost of each. It outputs one **plan**.
5. **Executor.** Runs the plan and streams rows back to the client.

> [!analogy] Real-world analogy: a restaurant order
> A waiter takes your order and checks it is written legibly. The kitchen checks each dish is on today's menu, expands "set menu B" into its three courses, and the head chef decides which cook makes what, in which order. Then the cooks do the work and plates go out as they are ready.
>
> **How it maps:** checking legibility is the parser (grammar only). Checking dishes exist is the analyser resolving table and column names against the catalog. Expanding the set menu is the rewriter expanding a view. The head chef's plan is the planner choosing a plan, and the cooks are the executor.
>
> **Where it stops:** a chef plans from experience, while the planner estimates costs from stored statistics, and it can pick a poor plan when those statistics are wrong. Rows also stream back as soon as the executor produces them, rather than in courses.

Planning and execution both have costs. Their relative importance depends on the complexity of the SQL statement, prepared-plan reuse and workload; short OLTP statements can spend a substantial share of their time planning.

> [!note] Prepared statements skip work
> A prepared statement is parsed and analysed once. Later executions can reuse a cached plan, which can save planning work when a generic plan is reused. A custom plan still plans for each supplied parameter value; the later unit on parameter plans covers the trade-off.

## Key takeaways
- Parsing checks grammar; analysis resolves names and types; rewriting expands ordinary views before planning.
- Prepared statements can reuse a generic plan, but parameter-specific custom plans still incur planning work.

## Further reading
- [Overview of PostgreSQL internals: the path of a query](https://www.postgresql.org/docs/18/query-path.html)
- [The PostgreSQL executor](https://www.postgresql.org/docs/18/executor.html)
- [Using EXPLAIN — PostgreSQL docs](https://www.postgresql.org/docs/18/using-explain.html)
- [Query plan — Wikipedia](https://en.wikipedia.org/wiki/Query_plan)
- [Parallel query — PostgreSQL docs](https://www.postgresql.org/docs/18/parallel-query.html)

