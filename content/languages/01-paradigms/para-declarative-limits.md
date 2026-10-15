---
id: para-declarative-limits
title: Declarative costs and escape hatches
level: basic
minutes: 3
sourceLesson: para-imperative-declarative
summary: Inspect plans and effectful boundaries when an abstraction hides cost.
---

An engine can hide expensive work behind a short declaration. Inspect both the abstraction and its execution boundary when a readable program unexpectedly becomes slow.

## It's a spectrum

"Imperative" and "declarative" are not two boxes; they are relative. A comprehension is more declarative than a `for` loop, but less declarative than SQL, because you still chose the data structure and evaluation order.

A useful test: how much of the execution order and intermediate state is visible in your code? The more there is, the more imperative it is.

## Trade-offs and pitfalls

Declarative code is usually shorter, has fewer places for bugs to hide (no off-by-one loop counter, no forgotten reset of an accumulator), and expresses intent directly. But the abstraction leaks.

- Performance cliffs. You do not control the plan, so when the engine picks badly, things get dramatically slower. For a hypothetical workload, a missing index or stale statistics could turn a 5-millisecond query into a 50-second scan while the SQL text stays identical. These illustrative timings are not measurements or a general cost ratio.
- The "how" sneaks back in. Real systems grow escape hatches: SQL index hints, React's `useMemo`, or explicit Terraform dependency declarations. You end up needing to know the engine's internals anyway.
- Debugging is indirect. Ordinary application breakpoints do not expose every step of the database execution engine. You read `EXPLAIN` output or a React profiler instead.
- Expressiveness limits. Pure SQL cannot easily express "loop until converged". SQL implementations offer procedural extensions; recursive CTEs also express iteration declaratively and can handle some convergence problems.
- Imperative is sometimes clearer. A complex algorithm with early exits, such as a state machine for parsing, is often easiest to read as explicit steps.

> [!warning] An ORM's N+1 trap
> ORMs let you write `for order in orders: print(order.customer.name)`, which looks like simple attribute access. Each `.customer` may fire a separate query, so 1,000 orders cause 1,001 round trips. The declarative-looking code hid an imperative cost. Eager loading with an appropriate join or batch query can avoid those per-object queries.

The name "N+1" comes from counting the queries: one to load the list, then one more per item in it.

```formula
Q = 1 + N
Q = 1 + 1000 = 1001
where
Q: the total number of database queries (round trips) the loop makes
N: the number of orders loaded, here 1,000
In words: one query fetches the orders, then each order triggers one extra query for its customer.
```

At even 1 ms per round trip, 1,001 queries spend about a second just waiting on the database. For this simple relationship and one unbatched result set, an appropriate join or prefetch can reduce the count to one or two queries. Real pagination, batching, database parameter limits and additional relationships can require more queries.

## Key takeaways
- Inspect plans and effectful boundaries when an abstraction hides cost.
- An N+1 access pattern can issue one query per related object.

## Further reading
- [PostgreSQL: understanding execution plans](https://www.postgresql.org/docs/17/using-explain.html)
- [Django: database access optimisation](https://docs.djangoproject.com/en/stable/topics/db/optimization/)
