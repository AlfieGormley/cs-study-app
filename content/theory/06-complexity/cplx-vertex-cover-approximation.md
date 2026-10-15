---
id: cplx-vertex-cover-approximation
title: "A matching gives a two-approximation"
level: intermediate
minutes: 4
summary: "Approximation gives up exactness while keeping a quality guarantee."
sourceLesson: cplx-coping
---

## Option 3: approximation algorithms

An approximation algorithm runs in polynomial time and always returns a solution that is provably close to the best one. The closeness is measured by a factor α:

```formula
ALG_min ≤ α OPT_min
ALG_max ≥ OPT_max / α
where
ALG_min: the cost of the solution the algorithm returns, for a problem where lower cost is better (lower is better, e.g. a route length)
OPT_min: the cost of the best possible solution to the same input
ALG_max: the value the algorithm achieves, for a maximisation problem (higher is better, e.g. clauses satisfied)
OPT_max: the best possible value for the same input
α: alpha, the approximation factor, at least 1; it may depend on input size, and α = 1 means always optimal
In words: an α-approximation is never worse than the optimum by more than a factor α, in either direction. A 2-approximation for a route problem never returns a route more than twice the shortest.
```

The guarantee holds on every input, without the algorithm ever knowing OPT. Some authors write maximisation guarantees as a factor below 1 instead (for example "0.5-approximation" for the same thing as 2 here), so check the convention.

### Vertex cover: a 2-approximation in five lines

A vertex cover is a set of vertices that touches every edge. Repeatedly take an edge with neither end covered, and add **both** endpoints.

```python
def vc_2approx(edges):
    cover = set()
    for u, v in edges:
        # Pick only edges disjoint from past
        # picks.
        if not ({u, v} & cover):
            cover |= {u, v}
    return cover

path = [(1, 2), (2, 3), (3, 4)]
print(vc_2approx(path))   # {1, 2, 3, 4}
# optimum is {2, 3}: ratio exactly 2
```

Why it's within factor 2: the edges we picked form a **graph matching** M (no two share a vertex). Any cover, including the optimal one, must contain at least one endpoint of each matched edge, and those endpoints are all different. That gives a lower bound on the optimum and an exact count for our cover:

```formula
OPT ≥ |M|
|C| = 2|M|
|C| = 2|M| ≤ 2OPT
where
M: the matching: the edges the algorithm picked, no two sharing a vertex
|M|: the number of edges in M
OPT: the size (number of vertices) of a smallest vertex cover
C: the cover the algorithm returns; |C| is its number of vertices
In words: every cover needs a different vertex for each picked edge, so the best cover has at least |M| vertices. The algorithm takes exactly two per picked edge, so it is never more than twice the best.
```

The path example shows the bound is tight: the algorithm picks the first and last edges, which form a two-edge matching, and returns four vertices. The two middle vertices cover all three edges, so the minimum cover has size two and the approximation ratio is exactly two. An exhaustive finite audit compares the algorithm with optimum covers on every simple graph with up to five vertices; all returned sets cover every edge and satisfy the factor-two bound. The matching proof gives the guarantee for arbitrary simple graphs.

## Key takeaways

- Approximation gives up exactness while keeping a quality guarantee.
- Taking both ends of uncovered edges builds a cover from a matching.
- Every cover needs one distinct endpoint per matched edge, proving the factor two.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
- [The Design of Approximation Algorithms — Williamson and Shmoys](https://www.designofapproxalgs.com/book.pdf)
