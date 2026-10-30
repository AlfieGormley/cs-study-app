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

> [!analogy] Real-world analogy: making room on a crowded bench
> A newcomer wants a seat on a bench. If a seat they are happy with is free, they sit. Otherwise they ask someone in a seat they would like whether that person could move to another seat that suits them, and that person may in turn ask someone else to shuffle along.
>
> **How it maps:** people are left vertices, seats are right vertices and "happy with" is an edge. The chain of polite requests is an augmenting path: it ends at a free seat, and everyone along it moves one place, so one more person is seated and nobody loses a seat.
>
> **Where it stops:** real people may refuse or have preferences between seats. Kuhn's search tries every acceptable option in turn and treats all of them as equally good; choosing the best pairing by cost needs the weighted methods below.

With n vertices and m edges in the bipartite graph, the costs differ in how many augmenting-path searches they need:

- Kuhn: one augmenting-path search per left vertex, each of which may scan every edge, so the worst case grows with the number of left vertices times the number of eligible pairs (plus the cost of reading the input).
- **Hopcroft–Karp**: finds many shortest augmenting paths per phase, so it needs only about as many phases as the square root of the vertex count, instead of one search per left vertex: O((n + m) √n), conventionally O(m √n) after isolated vertices are removed. These are worst-case growth bounds, not measured times.
- **Weighted assignment** (minimise total cost while assigning every item on the required side, e.g. driver ETA, the estimated time of arrival): the **Hungarian algorithm**, O(n³) for an n × n assignment, or min-cost flow. Without a required cardinality, an empty matching can minimise non-negative cost.

> [!tip] König's theorem
> In a bipartite graph, the size of a maximum matching equals the size of a minimum **vertex cover** (the fewest vertices touching every edge). So max matching also answers "fewest guards to watch every corridor" when the graph is bipartite. In general graphs, minimum vertex cover is NP-hard.

## Key takeaways
- Unit-capacity flow enforces one partner per vertex.
- Augmenting paths can move existing partners to admit a new one.
- König’s vertex-cover equality is specific to bipartite graphs.

## Further reading
- [Sedgewick and Wayne, Algorithms 4th ed.: 6.5 Reductions](https://algs4.cs.princeton.edu/65reductions/)
- [Maximum flow problem — Wikipedia](https://en.wikipedia.org/wiki/Maximum_flow_problem)
- [Matching (graph theory) — Wikipedia](https://en.wikipedia.org/wiki/Matching_(graph_theory))
- [Hopcroft–Karp algorithm — Wikipedia](https://en.wikipedia.org/wiki/Hopcroft%E2%80%93Karp_algorithm)
