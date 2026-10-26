---
id: disc-relation-closures
title: "Reachability and relation closures"
level: basic
minutes: 2
summary: "Transitive closure links pairs joined by positive-length paths, including self-pairs reached by cycles."
sourceLesson: disc-relations
---

## Closures

Often you have a relation that is "almost" what you want. The **transitive closure** is the smallest transitive relation containing it: it links a to b whenever a chain of one or more links leads from a to b.

A positive-length path counts, even if it returns to its starting vertex. Thus a directed cycle makes its vertices reachable from themselves; an isolated vertex does not acquire a self-link merely through transitive closure.

"Can user A reach user B through follows?" and "does package X depend on Y, directly or indirectly?" are transitive-closure questions.

You can compute reachability with a matrix-based algorithm such as Warshall, or search outward from each vertex using adjacency lists. Sparse graphs can favour the search approach.

```formula reference
T_W = O(n^3)
T_S = O(n × (n + m))
where
T_W: running time of Warshall's algorithm, which works on the adjacency matrix
T_S: running time of a breadth-first or depth-first search (BFS or DFS) from every vertex, using adjacency lists
n: the number of elements (vertices)
m: the number of related pairs (edges)
O( ): big-O: grows no faster than the expression inside, up to a constant factor
In words: A matrix-based closure algorithm has cubic growth in the vertex count. Searching from every vertex can use the smaller edge count of a sparse graph, though actual speed also depends on representation and constants.
```

The growth bounds do not promise a particular wall-clock speedup: constants and memory access patterns matter. SQL can compute reachability with a recursive CTE; cycles require duplicate elimination or another stopping rule.

The empty relation on an empty set is already reflexive, symmetric and transitive. For other sets, the **reflexive closure** adds the diagonal, the **symmetric closure** adds reverse edges. The reflexive, symmetric, transitive closure of any relation is an equivalence relation: it groups vertices into connected components after ignoring any edge directions.

> [!analogy] Real-world analogy: Connecting journeys
> A route map may show only direct legs, while a journey planner asks which destinations can be reached with changes.
>
> **How it maps:** Direct edges are the original relation; allowing any positive number of legs gives transitive closure. A round trip can make a station reachable from itself.
>
> **Where it stops:** Real journeys have timetables and costs. Plain reachability ignores those extra constraints.

## Key takeaways

- Transitive closure links pairs joined by positive-length paths, including self-pairs reached by cycles.
- Reflexive and symmetric closures add self-links and reverse links respectively.

## Further reading

- [Binary relation — Wikipedia](https://en.wikipedia.org/wiki/Binary_relation)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
