---
id: qp-join-search
title: Searching the join-order space
level: intermediate
minutes: 3
sourceLesson: qp-statistics-optimiser
summary: Why the number of possible join orders explodes, how dynamic programming over table subsets tames it, and when PostgreSQL switches to a genetic search.
---

Examples use PostgreSQL 18 and the module's scaled-up shop tables (1,000,000 orders, 100,000 customers; the first lesson lists them). Plans are abbreviated and illustrative: real plans and timings depend on the data, statistics, settings, cache state and version. Assume serial execution.

The optimiser predicts cardinalities, applies a cost model, and searches candidate plans. Cardinality errors can dominate plan quality: the Leis et al. study in Further reading documents this on its evaluated workloads.

## Searching the plan space

For each table the planner generates the candidate access paths (seq scan, each usable index, bitmap scans). It then has to choose a **join order**, and that space explodes:

| Tables | Left-deep orders | All tree shapes |
|---|---|---|
| 3 | 6 | 12 |
| 5 | 120 | 1,680 |
| 10 | 3,628,800 | 17,643,225,600 |

```formula reference
L(n) = n!
T(n) = (2 × n − 2)! / (n − 1)!
where
L(n): the number of left-deep join orders for n tables: each step joins one more base table to the result so far, so an order is just a sequence of the tables
T(n): the number of join trees of any shape (left-deep or bushy), counting which input goes on which side of each join
n: the number of tables being joined
!: factorial: multiply all the whole numbers from 1 up to the number, so 3! = 1 × 2 × 3 = 6
In words: the number of possible join orders grows faster than exponentially with the number of tables, so trying them all is hopeless beyond a handful of tables.
```

These counts assume every table can join to every other; they exclude the choice of join algorithm and orders that the query's semantics forbid.

Postgres uses System R-style **dynamic programming**. It finds the best way to join every pair of tables, then every set of three built from those, and so on. It keeps the cheapest plan for each subset, plus any plan that produces a useful sort order (an "interesting order") that might avoid a sort later. Working over subsets rather than full orderings is what makes it tractable. Ten tables have only 1,024 subsets (each table is either in a subset or not: 2 choices, ten times over), against 3.6 million left-deep orders.

The work per subset still varies, because each subset can be split in several ways and each split has several physical join methods, but the count stays far below the number of trees.

> [!analogy] Real-world analogy: planning a multi-stop delivery round
> A driver with five drops could compare every possible route, but with twenty drops there are far too many. A sensible planner instead works out the best way to cover each small group of nearby stops once, then builds bigger groups from those, never recomputing a group it has already solved.
>
> **How it maps:** the drops are tables and a route is a join order. Remembering the best plan for each group of stops is dynamic programming over subsets of tables. With very many stops, settling for a good route found by trial and improvement is GEQO's genetic search.
>
> **Where it stops:** a delivery route's cost is mostly fixed distances; a join plan's cost depends on estimated row counts, so a "best" join order can still be poor if those estimates are wrong.

At or above `geqo_threshold` (default 12) FROM items, exhaustive search is too slow, so Postgres switches to **GEQO**, a genetic algorithm that finds a good plan rather than the best. Separately, `join_collapse_limit` (default 8) caps how many explicit `JOIN`s are merged into one list for reordering.

## Key takeaways
- Dynamic programming reuses subset paths and retains useful ordering alternatives.
- Join restrictions, pruning, collapse limits and GEQO constrain search; the cheapest estimated candidate need not run fastest.

## Further reading
- [Statistics used by the planner — PostgreSQL docs](https://www.postgresql.org/docs/18/planner-stats.html)
- [Row estimation examples — PostgreSQL docs](https://www.postgresql.org/docs/18/row-estimation-examples.html)
- [Multivariate statistics examples — PostgreSQL docs](https://www.postgresql.org/docs/18/multivariate-statistics-examples.html)
- [Access path selection in a relational DBMS (Selinger et al., 1979)](https://courses.cs.duke.edu/compsci516/cps216/spring03/papers/selinger-etal-1979.pdf)
- [How Good Are Query Optimizers, Really? (Leis et al., VLDB 2015)](https://www.vldb.org/pvldb/vol9/p204-leis.pdf)
- [Genetic query optimiser — PostgreSQL docs](https://www.postgresql.org/docs/18/geqo.html)

