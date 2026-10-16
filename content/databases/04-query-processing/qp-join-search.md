---
id: qp-join-search
title: Searching the join-order space
level: intermediate
minutes: 4
sourceLesson: qp-statistics-optimiser
summary: Searching the join-order space with worked examples and explicit assumptions.
---

These examples use PostgreSQL 18. SQL Fundamentals supplies the shop relations: `customers(id, name, email, city, country)`, `orders(id, customer_id, status, ordered_on, total)`, `products(id, price)` and `order_items(order_id)`. IDs join orders to customers and items to orders. Dates use `date`, IDs use `integer`, and totals use `numeric`. Each query fragment uses these names; ellipses and standalone WHERE clauses need the surrounding SELECT shown by their context.

All historical plan fragments and timings in this unit are **illustrative inputs**, not reproduced benchmarks or promises. Their row/page counts describe a hypothetical dataset; actual plans vary with statistics, indexes, settings, cache state and PostgreSQL version. Assume serial execution unless a parallel worker process is shown.

The optimiser predicts cardinalities, applies a cost model, and searches candidate plans. Cardinality errors can dominate plan quality: the Leis et al. study in Further reading documents this on its evaluated workloads.

## Searching the plan space

For each table the planner generates the candidate access paths (seq scan, each usable index, bitmap scans). It then has to choose a **join order**, and that space explodes:

| Tables | Left-deep orders | All tree shapes |
|---|---|---|
| 3 | 6 | 12 |
| 5 | 120 | 1,680 |
| 10 | 3,628,800 | 17,643,225,600 |

Both columns come from counting arrangements:

```formula
L(n) = n!
T(n) = (2 × n − 2)! / (n − 1)!
L(10) = 10! = 3,628,800
T(10) = 18! / 9! = 17,643,225,600
where
L(n): the number of left-deep join orders for n tables: each step joins one more base table to the result so far, so an order is just a sequence of the tables
T(n): the number of join trees of any shape (left-deep or bushy), counting which input goes on which side of each join
n: the number of tables being joined
!: factorial: multiply all the whole numbers from 1 up to the number, so 3! = 1 × 2 × 3 = 6
In words: the number of possible plans grows faster than exponentially, so trying them all is hopeless beyond a handful of tables.
```

The three-table row follows the same factorial counts: six left-deep orders and twelve ordered, labelled trees. These counts assume unrestricted joins among distinct tables; they exclude physical method choices and illegal reorderings.

Postgres uses System R-style **dynamic programming**. It finds the best way to join every pair of tables, then every set of three built from those, and so on. It keeps the cheapest plan for each subset, plus any plan that produces a useful sort order (an "interesting order") that might avoid a sort later. Working over subsets rather than full orderings is what makes it tractable:

```formula
N_sub = 2^n
N_sub = 2^10 = 1,024
where
N_sub: the number of subsets of the tables, counting the empty set; each table is either in a subset or not, giving 2 choices per table
n: the number of tables being joined, here 10
In words: ten tables have only 1,024 subsets, against 3.6 million orderings.
```

The work per subset still varies, because each subset can be split in several ways and each split has several physical join methods, but the count stays far below the number of trees.

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

