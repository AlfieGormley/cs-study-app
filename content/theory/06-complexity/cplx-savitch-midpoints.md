---
id: cplx-savitch-midpoints
title: "Savitch’s midpoint recursion"
level: advanced
minutes: 3
summary: "Try each candidate midpoint and recurse on two shorter path bounds."
sourceLesson: cplx-space
---

## Savitch's theorem

Does nondeterminism help for space as much as it seems to for time? Much less, it turns out.

**Savitch's theorem (1970)** applies to space-constructible bounds at least logarithmic in input length. Space-constructible means the machine can mark out the permitted workspace within that bound. The standard bounds used here meet this condition.

```formula essential
NSPACE(s) ⊆ SPACE(s^2)   for s ≥ log n
where
NSPACE(s): problems a nondeterministic (guessing) machine decides using at most a constant times s work-tape cells
SPACE(s^2): problems a deterministic machine decides using at most a constant times s squared cells
s: a space-constructible space bound, in cells; the machine can mark off that many cells within that order of space
n: the input size, in bits
log: logarithm base 2
⊆: "is contained in"
≥: is at least
In words: a deterministic simulation needs at most quadratic growth in the original space bound. This is an asymptotic guarantee with hidden constants, not an exact allocation of memory cells.
```

The idea is a midpoint recursion:

```formula essential
R(u, v, t)  iff  ∃ w with
  R(u, w, ⌈t/2⌉) and R(w, v, ⌊t/2⌋)
where
R(u, v, t): "there is a path from vertex u to vertex v of length at most t edges"
u, v: the start and end vertices
w: a candidate midpoint vertex
t: an integer maximum path length of at least two, in edges
⌈ ⌉, ⌊ ⌋: ceiling rounds up and floor rounds down; the two integer half-bounds sum to t
∃: "there exists": at least one such w
In words: a path of at most t edges exists exactly when some middle vertex splits it into two parts bounded by the rounded-up and rounded-down halves. If the path is shorter than the bound, choose the midpoint along that shorter path; allowing a zero-length part handles an endpoint.
```

Try every w, recursing on both halves, and **reuse** the space between the two calls.

```python
def reach(adj, u, v, t):
    # is there a path u -> v of length <= t?
    # (called with t >= 1)
    if t <= 1:
        return u == v or v in adj[u]
    # Integer halves add up to the full
    # bound.
    h = (t + 1) // 2
    return any(reach(adj, u, w, h) and
               reach(adj, w, v, t - h)
               for w in adj)

adj = {0: [1], 1: [2], 2: [3],
       3: [], 4: [0]}
n = len(adj)
print(reach(adj, 0, 3, n))   # True
print(reach(adj, 3, 0, n))   # False
print(reach(adj, 4, 3, n))   # True: via 0
print(reach(adj, 0, 3, 2))   # False: 3 hops
```

The adjacency dictionary must include every vertex, including sinks. The initial bound is a positive integer. The function reads an explicit graph already held by the caller; the space theorem concerns additional workspace, not the memory needed to store that input dictionary. Python frame and integer overhead are larger than the bit-packed model.

## Key takeaways

- Try each candidate midpoint and recurse on two shorter path bounds.
- Sequential recursive invocations reuse workspace.
- The Python example demonstrates the recursion on an explicit graph.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
