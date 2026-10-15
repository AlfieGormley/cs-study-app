---
id: cplx-parameter-branching
title: "Confine exponential search to a parameter"
level: intermediate
minutes: 4
summary: "FPT permits an arbitrary computable parameter factor with a fixed polynomial input exponent."
sourceLesson: cplx-coping
---

## Option 4: parameterised algorithms

Sometimes the hardness lives in one small number. A problem is **fixed-parameter tractable (FPT)** in parameter k if it can be solved in this much time:

```formula
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

The recursion tree has depth at most k and branching factor 2, so at most 2 to the power k leaves, each doing work proportional to the number of edges m:

```formula
T = O(2^k m)
2^20 ≈ 1.05 × 10^6
C(10000, 20) ≈ 4.0 × 10^{61}
1.2738^20 ≈ 126
where
T: the running time, in basic steps
O(...): Big O: grows at most as fast as a constant times the expression inside
k: the cover-size budget, here 20
m: the number of edges; each call filters the edge list once
2^k: 2 to the power k: the most leaves a binary recursion of depth k can have
N, r: nonnegative integer counts, with r at most N; 10,000 and 20 here
C(N, r): "N choose r": the number of ways to pick r items from N; here, all 20-vertex subsets of 10,000 vertices
In words: with a budget of 20, the search tree has about a million leaves, while brute force would test about 4 × 10^61 subsets. Refined branching shrinks the exponential part to about 126.
```

So a 10,000-vertex network with a cover of size 20 has a search-tree bound of about a million leaves, each with edge-processing costs; practical runtime still requires measurement, while brute force over all 20-vertex subsets is hopeless. A representative refined algorithm (Chen, Kanj and Xia, 2010) has an exponential factor with base about 1.2738 in the budget, plus a term proportional to budget times vertex count. This is a published bound, not a claim about the current record.

The code assumes a finite simple undirected graph and a nonnegative integer budget. It keeps Python edge lists in memory; the bound counts list operations rather than claiming that an abstract bit-packed machine runs at the same speed. Refined branching bounds cited here are representative published results, not a claim to list the latest record.

## Key takeaways

- FPT permits an arbitrary computable parameter factor with a fixed polynomial input exponent.
- Branching on an edge’s two endpoints gives a vertex-cover search tree of bounded depth.
- Operation-count estimates do not predict measured wall time.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
