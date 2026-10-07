---
id: disc-relations
title: Relations, equivalence classes and partial orders
level: basic
minutes: 13
summary: Binary relations and their properties, equivalence relations and the partitions they create, partial orders, Hasse diagrams, topological sorting and closures.
---

A function links each input to exactly one output. A **relation** is the looser idea: any collection of links between things. "Follows" on a social network, "depends on" between packages, "is congruent to mod 7" between integers and "happened before" between events in a distributed system are all relations.

Two special kinds of relation do a huge amount of work in computer science. **Equivalence relations** say when two things count as "the same" and split a set into groups. **Partial orders** say when one thing must come "before" another, and are what a build system or a task scheduler sorts.

## What a relation is

A **binary relation** R from A to B is a subset of A × B. We write a R b (or (a, b) ∈ R) when a is related to b. A relation on a single set A is a subset of A × A.

Three equivalent pictures of the same relation on {1, 2, 3}:

```
pairs:   {(1,1), (1,2), (2,3)}

matrix:      1  2  3
          1  1  1  0
          2  0  0  1
          3  0  0  0

graph:   1 --> 2 --> 3
         plus a self-loop 1 --> 1
```

The matrix view shows why there are 2^(n²) relations on an n-element set: each of the n² cells is independently 0 or 1. The graph view is why so much of graph theory is really about relations.

## The four key properties

For a relation R on a set A:

| Property | Definition |
|---|---|
| Reflexive | a R a for every a |
| Symmetric | a R b implies b R a |
| Antisymmetric | a R b and b R a imply a = b |
| Transitive | a R b and b R c imply a R c |

In the matrix: reflexive means the diagonal is all 1s, symmetric means the matrix equals its transpose. In the graph: reflexive means a self-loop on every node, symmetric means every edge has a reverse edge, transitive means every two-step path has a shortcut edge.

> [!warning] Antisymmetric is not "not symmetric"
> Antisymmetric only forbids two-way links between *different* elements. Equality (=) is both symmetric and antisymmetric. The relation {(1, 2), (2, 1), (1, 3)} is neither: (1, 2) has a reverse, but (1, 3) doesn't.

Some everyday examples:

- **≤ on integers**: reflexive, antisymmetric, transitive. Not symmetric.
- **< on integers**: not reflexive (irreflexive), antisymmetric (vacuously), transitive.
- **"Is a friend of"**: symmetric, usually not transitive.
- **"Follows" on a social network**: none of the four in general.

## Equivalence relations

A relation that is **reflexive, symmetric and transitive** is an **equivalence relation**. It formalises "the same in the way we care about".

Examples:

- **Congruence mod n**: a ≡ b (mod n) if n divides a − b. Mod 3 groups integers by remainder.
- **Same connected component** in an undirected graph.
- **Case-insensitive equality** of strings: "Hello" ~ "HELLO".
- **Same hash bucket**: keys related if h(x) = h(y). Any relation of the form "f(x) = f(y)" is an equivalence relation.

The **equivalence class** of a is [a] = { x : x ~ a }, everything equivalent to a. The crucial theorem: **the equivalence classes partition the set**. Every element is in exactly one class, and two classes are either identical or disjoint.

```
Integers mod 3:
[0] = {..., -3, 0, 3, 6, ...}
[1] = {..., -2, 1, 4, 7, ...}
[2] = {..., -1, 2, 5, 8, ...}
```

The converse holds too: any partition defines an equivalence relation ("in the same block"). So the number of equivalence relations on an n-element set equals the number of partitions, the **Bell number**: 1, 1, 2, 5, 15, 52, … for n = 0, 1, 2, 3, 4, 5.

### Equivalence relations in code

The **union-find** (disjoint-set) data structure maintains an equivalence relation as you add facts like "a ~ b". Each class is a tree with a representative at the root. Because the relation is transitive, merging two classes is all you ever need to do.

```python
parent = {}

def find(x):
    parent.setdefault(x, x)
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x

def union(a, b):
    parent[find(a)] = find(b)

union('a', 'b'); union('b', 'c')
find('a') == find('c')   # True
```

Union-find tracks components for Kruskal's algorithm and can support type-variable unification. Full type unification also needs to handle type structure and checks such as the occurs check.

Python's own contract relies on this theory. Well-behaved value equality is normally an equivalence relation, but Python does not enforce these laws and NaN is a standard exception. Hashable objects that compare equal must have equal hashes, and their hash must stay stable while used as keys.

> [!warning] "Approximately equal" is not an equivalence
> Define x ~ y if |x − y| < 0.1. Then 0.0 ~ 0.08 and 0.08 ~ 0.16, but 0.0 and 0.16 are not related. Tolerance-based equality is not transitive, so it cannot be used to bucket values into consistent groups.

## Partial orders

A relation that is **reflexive, antisymmetric and transitive** is a **partial order**, written ≼. A set with a partial order is a **poset**.

Examples:

- ≤ on numbers.
- ⊆ on the subsets of a set.
- "Divides" (a | b) on positive integers.
- "Must be built before" on build targets (taking the reflexive closure).
- "Happened before" on events in a distributed system (Lamport's relation, as a strict order).

"Partial" means some pairs may be **incomparable**: neither a ≼ b nor b ≼ a. {1} and {2} are incomparable under ⊆; so are 2 and 3 under "divides". If every pair is comparable, it is a **total order** (or linear order), like ≤ on integers or alphabetical order on strings.

A **strict** partial order (<) is irreflexive and transitive; you get one from ≼ by removing the diagonal. An acyclic direct-dependency graph need not itself be transitive; its positive-length reachability relation is a strict partial order.

### Hasse diagrams

A **Hasse diagram** draws a poset without clutter: leave out self-loops and any edge implied by transitivity, and put larger elements higher. Here is "divides" on the divisors of 12:

```
        12
       /  \
      4    6
      |  /  \
      2      3
       \    /
        \  /
         1
```

Read upwards: 2 | 4 | 12. 4 and 6 are incomparable, as are 4 and 3.

Vocabulary that comes up in interviews and papers:

- **Minimal** element: nothing is strictly below it. **Least** (minimum) element: below everything. A poset can have several minimal elements but at most one least element.
- **Chain**: a set of pairwise comparable elements. **Antichain**: pairwise incomparable.
- **Upper bound, least upper bound (join)**. In the subset order, the join of two sets is their union. Posets where every pair has a join and a meet are **lattices**; state-based CRDTs use a join operation on a semilattice of states; operation-based CRDTs use different delivery and commutativity conditions.

### Topological sorting

A **linear extension** of a poset is a total order that respects it: if a ≺ b then a comes before b. For a finite DAG, finding one is **topological sorting**, and it exists precisely because there are no cycles (a cycle of distinct vertices conflicts with antisymmetry of reachability, and a self-loop conflicts with strict precedence).

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
print(list(ts.static_order()))
# e.g. ['config', 'utils', 'lib', 'app']
```

There are usually many valid orders: the incomparable elements can come in any relative order. Build and dependency tools use dependency ordering when prerequisites form a DAG. Cycle policies vary: pip documents an installation fallback for dependency cycles, so not every such tool rejects them.

> [!example] Vector clocks are a partial order
> In a store that tracks versions with vector clocks, each version carries counters for its tracked participants. Version V ≤ W if every component of V is ≤ the matching component of W. Two versions where neither is ≤ the other are **concurrent**: incomparable in the partial order. Riak and Dynamo-style stores surface these as siblings for the application to merge.

## Closures

Often you have a relation that is "almost" what you want. The **transitive closure** R⁺ is the smallest transitive relation containing R: a R⁺ b if there is a path of positive length from a to b. "Can user A reach user B through follows?" and "does package X depend on Y, directly or indirectly?" are transitive-closure questions.

Warshall's algorithm computes it in O(n³) from the adjacency matrix. With adjacency lists, a BFS or DFS from every vertex takes O(n(n+m)); this improves the asymptotic bound on sparse graphs, without promising a fixed wall-clock speedup. SQL computes reachability with a recursive CTE.

The **reflexive closure** adds the diagonal, the **symmetric closure** adds reverse edges. The reflexive, symmetric, transitive closure of any relation is an equivalence relation: it groups vertices into connected components after ignoring any edge directions.

## Pitfalls

- **Inconsistent comparators.** Sorting assumes a total (pre)order. A comparator that isn't transitive (say, rock-paper-scissors, or one that compares floats with NaN) can make sort output depend on the input order, or make Java's `TimSort` throw "Comparison method violates its general contract!".
- **NaN breaks reflexivity.** `float('nan') == float('nan')` is `False`, so IEEE 754 floats are not an equivalence relation under `==`. For ordinary float-NaN lookups, retaining the identical key object permits retrieval even though NaN is not equal to itself; another separately created float NaN does not match it.
- **Assuming a total order where only a partial one exists.** Wall-clock timestamps can tie and need not match causality. Lamport timestamps respect causal precedence but do not detect concurrency; a process-ID tie-breaker can make them total. Vector clocks can expose concurrency under their model.

## Key takeaways
- A relation on A is any subset of A × A; matrices and directed graphs are two views of the same thing.
- Equivalence relations (reflexive, symmetric, transitive) partition a set into disjoint classes; union-find maintains them incrementally.
- Partial orders (reflexive, antisymmetric, transitive) allow incomparable elements; total orders don't.
- A topological sort is a linear extension of a partial order, and exists exactly when the dependency graph has no cycles.
- Equality, hashing and sorting in real code silently assume these properties; NaN, tolerances and bad comparators break them.

## Further reading
- [Binary relation — Wikipedia](https://en.wikipedia.org/wiki/Binary_relation)
- [Equivalence relation — Wikipedia](https://en.wikipedia.org/wiki/Equivalence_relation)
- [Partially ordered set — Wikipedia](https://en.wikipedia.org/wiki/Partially_ordered_set)
- [Topological sorting — Wikipedia](https://en.wikipedia.org/wiki/Topological_sorting)
- [graphlib — Python docs](https://docs.python.org/3/library/graphlib.html)
- [Vector clock — Wikipedia](https://en.wikipedia.org/wiki/Vector_clock)
