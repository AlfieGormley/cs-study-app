---
id: disc-topological-order-vector-clocks
title: "Topological order, comparators and vector clocks"
level: basic
minutes: 3
summary: "A topological ordering respects every dependency in a finite DAG."
sourceLesson: disc-relations
---

### Topological sorting

A **linear extension** of a poset is a total order that respects it: a list of all the elements in which everything strictly below another element comes earlier.

```formula
a ≺ b   ⇒   pos(a) < pos(b)
where
a, b: elements of the poset
≺: is strictly below in the partial order (for a build: is a prerequisite of)
⇒: implies
pos: the position of an element in the chosen list (1 for first, 2 for second, …)
<: is less than
In words: a valid order never lists something before one of its prerequisites. Elements with no order between them can go either way round.
```

For a finite DAG of prerequisite-to-dependent edges, finding one is **topological sorting**, and it exists precisely because there are no cycles (a cycle of distinct vertices conflicts with antisymmetry of reachability, and a self-loop would need a target to come strictly before itself).

```python
from graphlib import TopologicalSorter

# target: its prerequisites
deps = {
    'app': {'lib', 'config'},
    'lib': {'utils'},
    'config': set(),
    'utils': set(),
}
ts = TopologicalSorter(deps)
# Emit prerequisites before their targets.
print(list(ts.static_order()))
# e.g. ['config', 'utils', 'lib', 'app']
```

There are usually many valid orders: for any two incomparable elements, some linear extension puts the first earlier and another puts the second earlier. All choices must still respect the other constraints. Build and dependency tools use dependency ordering when prerequisites form a DAG. Cycle policies vary: pip documents an installation fallback for dependency cycles, so not every such tool rejects them.

> [!example] Vector clocks are a partial order
> In a store that tracks versions with vector clocks, each version carries a list of counters, one for each tracked participant. One version is below another when none of its counters is larger. Two versions where neither is below the other are **concurrent**: incomparable in the partial order. Riak and Dynamo-style stores surface these as siblings for the application to merge.

```formula
V ≤ W   means   V_i ≤ W_i   for every i
[2, 1, 0] ≤ [2, 2, 1]
[2, 1, 0] ∥ [1, 2, 0]
where
V, W: two vector clocks: lists of counters, one per participant
V_i, W_i: counter number i in V and in W
i: a position in the list, one per participant
≤: on the left, the order on whole clocks; on the right, ordinary "less than or equal to" on two counters
∥: is incomparable with (concurrent)
[ ]: a vector clock written as its list of counters
In words: one clock is below another when it is behind or level on every counter. [2, 1, 0] and [1, 2, 0] each lead on one counter, so neither is below the other: the two versions were written concurrently.
```

## Pitfalls

- **Inconsistent comparators.** Sorting assumes a total (pre)order. A comparator that isn't transitive (say, rock-paper-scissors, or one that compares floats with NaN) can make sort output depend on the input order, or make Java's `TimSort` throw "Comparison method violates its general contract!".
- **NaN breaks reflexivity.** `float('nan') == float('nan')` is `False`, so IEEE 754 floats are not an equivalence relation under `==`. For ordinary float-NaN lookups, retaining the identical key object permits retrieval even though NaN is not equal to itself; another separately created float NaN does not match it.
- **Assuming a total order where only a partial one exists.** Wall-clock timestamps can tie and need not match causality. Lamport timestamps respect causal order but do not detect concurrency; a process-ID tie-breaker can make them total. Vector clocks can expose concurrency under their model.

## Key takeaways

- A topological ordering respects every dependency in a finite DAG.
- Vector clocks form a partial order; comparator and equality contracts need mathematical consistency.

## Further reading

- [Topological sorting — Wikipedia](https://en.wikipedia.org/wiki/Topological_sorting)
- [graphlib — Python docs](https://docs.python.org/3/library/graphlib.html)
- [Vector clock — Wikipedia](https://en.wikipedia.org/wiki/Vector_clock)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
