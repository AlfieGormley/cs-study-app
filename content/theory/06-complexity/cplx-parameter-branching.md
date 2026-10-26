---
id: cplx-parameter-branching
title: "Confine exponential search to a parameter"
level: intermediate
minutes: 4
summary: "FPT permits an arbitrary computable parameter factor with a fixed polynomial input exponent."
sourceLesson: cplx-coping
---

## Option 4: parameterised algorithms

Sometimes the hardness lives in one small number. FPT means a computable parameter-only factor multiplied by a polynomial in total input length whose exponent is fixed independently of the parameter. A fixed parameter can make an exact algorithm useful, but neither factor is automatically small. A problem is **fixed-parameter tractable (FPT)** in parameter k if it can be solved in this much time:

```formula essential
T(n, k) = f(k) poly(n)
where
T(n, k): the running time, in basic steps
n: the input size, in bits
k: the parameter, a number you expect to be small, such as the solution size
f(k): any computable function of k alone, possibly exponential such as 2^k, but not involving n
poly(n): some polynomial in n, such as n^2 or n^3
In words: all the explosive growth is confined to the small parameter k; for a fixed k, the time grows only polynomially with the input, with an exponent that does not depend on k.
```

### Vertex cover by bounded branching

Any cover must contain u or v for an edge (u, v). Branch on both choices, with budget k − 1 each:

```python
def vc_fpt(edges, k):
    # returns a cover of size <= k, or None
    if not edges:
        return set()
    if k == 0:
        return None
    u, v = edges[0]
    for w in (u, v):
        # Choosing w covers all its incident
        # edges.
        rest = [e for e in edges
                if w not in e]
        sub = vc_fpt(rest, k - 1)
        if sub is not None:
            return sub | {w}
    return None

print(vc_fpt([(1, 2), (2, 3), (3, 4)], 2))
# {1, 3}: also a minimum cover
print(vc_fpt([(1, 2), (2, 3), (3, 4)], 1))
# None
```

The recursion tree has depth at most k and branching factor 2, so it has at most 2 to the power k leaves and fewer than twice as many nodes overall. Each nonterminal node filters an edge list of at most m edges for each of its two branches:

```formula reference
T = O(2^k m)
where
T: the running time, in basic steps
O(...): Big O: grows at most as fast as a constant times the expression inside
k: the nonnegative cover-size budget
m: the original number of edges; each branch filters its current edge list
2^k: 2 to the power k: the most leaves a binary recursion of depth k can have
In words: the search-tree factor depends exponentially on the cover budget, while each node filters edges. Fixing the budget keeps growth polynomial in the graph size; this bound counts list work, not wall-clock seconds.
```

Holding the cover budget fixed leaves only polynomial growth as the graph grows. Raising the budget increases the branching part rapidly. Compare this with enumerating every vertex subset of the requested size, where the exponent of graph size grows with that size. Both the budget and edge count matter in practice.

The code assumes a finite simple undirected graph and a nonnegative integer budget. It keeps Python edge lists in memory; the displayed bound counts list operations for a nonempty graph. An empty edge list returns immediately. The bound does not predict a measured runtime.

## Key takeaways

- FPT permits an arbitrary computable parameter factor with a fixed polynomial input exponent.
- Branching on an edge’s two endpoints gives a vertex-cover search tree of bounded depth.
- Operation-count estimates do not predict measured wall time.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
