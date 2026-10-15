---
id: disc-relation-closures
title: "Reachability and relation closures"
level: basic
minutes: 3
summary: "Transitive closure links pairs joined by positive-length paths, including self-pairs reached by cycles."
sourceLesson: disc-relations
---

## Closures

Often you have a relation that is "almost" what you want. The **transitive closure** is the smallest transitive relation containing it: it links a to b whenever a chain of one or more links leads from a to b.

```formula
a R⁺ b   means   a R x_1 R x_2 … R x_k R b
1 R 2 and 2 R 3   so   1 R⁺ 3
where
R: the original relation
R⁺: the transitive closure of R, read "R plus"
a, b: elements of the set
x_1, x_2, x_k: the intermediate elements on the chain
k: the number of intermediate vertices; when there are none, read the chain simply as a R b
…: and so on along the chain
In words: R⁺ adds a direct link for every path of length one or more in R. If 1 links to 2 and 2 links to 3, the closure links 1 to 3.
```

"Can user A reach user B through follows?" and "does package X depend on Y, directly or indirectly?" are transitive-closure questions.

Two standard ways to compute it, viewing the relation as a directed graph:

```formula
T_W = O(n^3)
T_S = O(n × (n + m))
where
T_W: running time of Warshall's algorithm, which works on the adjacency matrix
T_S: running time of a breadth-first or depth-first search (BFS or DFS) from every vertex, using adjacency lists
n: the number of elements (vertices)
m: the number of related pairs (edges)
O( ): big-O: grows no faster than the expression inside, up to a constant factor
In words: Warshall's algorithm costs about n^3 steps whatever the relation looks like; a search from every vertex costs about n searches of n + m steps each.
```

For a sparse relation with 10,000 vertices and 50,000 edges, cubing 10,000 gives a trillion steps while 10,000 × 60,000 is 600 million, so the searches win on the asymptotic bound. That is not a promise of a fixed wall-clock speedup, since constant factors and memory access patterns differ. SQL computes reachability with a recursive CTE.

The empty relation on an empty set is already reflexive, symmetric and transitive. For other sets, the **reflexive closure** adds the diagonal, the **symmetric closure** adds reverse edges. The reflexive, symmetric, transitive closure of any relation is an equivalence relation: it groups vertices into connected components after ignoring any edge directions.

## Key takeaways

- Transitive closure links pairs joined by positive-length paths, including self-pairs reached by cycles.
- Reflexive and symmetric closures add self-links and reverse links respectively.

## Further reading

- [Binary relation — Wikipedia](https://en.wikipedia.org/wiki/Binary_relation)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
