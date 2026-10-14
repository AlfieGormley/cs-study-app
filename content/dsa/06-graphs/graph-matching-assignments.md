---
id: graph-matching-assignments
title: Bipartite matching, reassignment and vertex covers
level: advanced
minutes: 3
sourceLesson: graph-advanced
summary: Unit-capacity flow enforces one partner per vertex.
---

Earlier graph units established bipartite colouring; flow units established integer max flow. The two sides of a bipartite graph represent different sets of entities, and every eligible pairing crosses between them.

## Bipartite matching

A **graph matching** is a set of edges with no shared vertex. In a bipartite graph (workers and jobs, riders and drivers), a **maximum matching** pairs up as many as possible.

### As a flow problem

```
s   -> Ann, Bob, Cat   (cap 1)
Ann -> X, Y            (cap 1)
Bob -> X               (cap 1)
Cat -> Y, Z            (cap 1)
X, Y, Z -> t           (cap 1)
```

Add a source joined to every worker and a sink joined from every job, all capacities 1, and direct the worker→job edges. An integer max flow is a maximum matching: each worker sends at most 1 unit, each job receives at most 1.

### Kuhn's algorithm (augmenting paths)

The flow view specialises into a short DFS. For each left vertex u, try to find a right vertex v that is free, or whose current partner can be moved elsewhere.

```python
def kuhn(left, adj):
    match = {}  # right -> left

    def augment(u, seen):
        for v in adj[u]:
            if v in seen:
                continue
            seen.add(v)
            if v not in match:
                # Reserve this right vertex
                # for u.
                match[v] = u
                return True
            # Move its current partner
            # before reuse.
            if augment(match[v], seen):
                # Reserve this right vertex
                # for u.
                match[v] = u
                return True
        return False

    return sum(augment(u, set())
               for u in dict.fromkeys(left))
```

With Ann→{X, Y}, Bob→{X}, Cat→{Y, Z}: Ann takes X. Bob wants X, so Ann is asked to move, and moves to Y. Cat tries Y: Ann would have to move back to X, which would need Bob to move, and Bob has nowhere else to go. That fails, so Cat takes Z. Result: 3 pairs.

With n vertices and m edges in the bipartite graph:

```formula
T_K = O(n_L + m + n_L m)
T_HK = O((n + m) √n)
T_K ≈ 10^5 × 10^6 = 10^11
T_HK ≈ 1.2 × 10^6 × √(2 × 10^5)
T_HK ≈ 5.4 × 10^8
where
n: the number of vertices; 2 × 10^5 in the example
n_L: the number of left vertices; 10^5 in the example
m: the number of edges; 10^6 in the example
T_K: Kuhn's running-time growth, including scanning left vertices and adjacency; one search per left vertex
T_HK: Hopcroft–Karp: O(√n) phases of O(n + m) each
√: the square root
≈: approximately equal to
O(…): Big O: grows at most this fast, up to a constant factor
In words: Hopcroft–Karp needs only about √n rounds instead of one per vertex, which here is nearly two hundred times less work.
```

Kuhn's bound counts one search per left vertex; these are growth expressions, not measured times.

- Kuhn: O(n_L + m + n_L m), where n_L counts left vertices and m counts eligible pairs. Including the input scan keeps the bound meaningful when there are no edges.
- **Hopcroft–Karp**: finds many shortest augmenting paths per phase, O((n + m) √n), conventionally O(m √n) after isolated vertices are removed.
- **Weighted assignment** (minimise total cost while assigning every item on the required side, e.g. driver ETA, the estimated time of arrival): the **Hungarian algorithm**, O(n³) for an n × n assignment, or min-cost flow. Without a required cardinality, an empty matching can minimise non-negative cost.

> [!tip] König's theorem
> In a bipartite graph, the size of a maximum matching equals the size of a minimum **vertex cover** (the fewest vertices touching every edge). So max matching also answers "fewest guards to watch every corridor" when the graph is bipartite. In general graphs, minimum vertex cover is NP-hard.

## Key takeaways
- Unit-capacity flow enforces one partner per vertex.
- Augmenting paths can move existing partners to admit a new one.
- König’s vertex-cover equality is specific to bipartite graphs.

## Further reading
- [Primary reference for this unit](https://algs4.cs.princeton.edu/65reductions/)
- [Maximum flow problem — Wikipedia](https://en.wikipedia.org/wiki/Maximum_flow_problem)
- [Matching (graph theory) — Wikipedia](https://en.wikipedia.org/wiki/Matching_(graph_theory))
- [Hopcroft–Karp algorithm — Wikipedia](https://en.wikipedia.org/wiki/Hopcroft%E2%80%93Karp_algorithm)
