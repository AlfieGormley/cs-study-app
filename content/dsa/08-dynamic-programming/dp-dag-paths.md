---
id: dp-dag-paths
title: Evaluate path recurrences on a DAG
level: advanced
minutes: 3
summary: A topological order finalises every predecessor before its outgoing edges.
sourceLesson: dp-advanced
---

## DP over DAGs: the unifying view

Draw each state as a node and each "depends on" relation as an edge. For the finite recurrences here, dependencies are acyclic, so this graph is a **DAG**. More general cyclic Bellman equations may instead require iterative methods. Then:

- **Bottom-up evaluation** is processing nodes in topological order.
- **Memoisation** is DFS on that DAG with caching.
- **Some optimisation DPs**, such as sequence alignment, are shortest/longest path problems in that DAG.
- **Some counting DPs** count paths in the DAG. Others combine independent child choices by multiplication, so the dependency graph alone is not a path-counting recurrence.

Edit distance, for example, is the shortest path through a grid DAG from the pair of empty prefixes to the pair of complete strings, with edges of weight 0 or 1. Knapsack is a longest path through a DAG of (item, weight limit) nodes.

When the problem itself is a DAG, apply this directly:

```python
def longest_path(n, edges, order):
    # order: a topological order
    best = [0] * n
    out = [[] for _ in range(n)]
    for u, v, w in edges:
        out[u].append((v, w))
    # Every incoming predecessor is final.
    for u in order:
        for v, w in out[u]:
            # Extend the best path ending at
            # u.
            best[v] = max(best[v],
                          best[u] + w)
    return max(best, default=0)
```

The inner line is the **relaxation** step:

```formula
best[v] = max(best[v], best[u] + w)
T = O(V + E)
where
best[v]: the largest total weight of any path found so far that ends at vertex v
u: a vertex whose value is already final (it comes earlier in the topological order)
v: the vertex at the end of the edge from u
w: the weight of the edge from u to v
max: the larger of the two values
T: the running time
V: the number of vertices (n in the code)
E: the number of edges
O(...): Big-O, growing at most in proportion to the expression inside
In words: a path to v can be the best path to u plus the edge u to v; processing vertices in topological order means every u is final before its edges are used, and every vertex and edge is handled once.
```

Given consecutively numbered vertices starting at zero, valid edges with integer weights and a complete topological order, this computes the best path starting anywhere, allowing a zero-edge path of value 0. For single-source **shortest paths**, initialise only the source to 0 and all other distances to +∞, use min-relaxation, and return the distance array rather than its maximum. Negative edge weights are valid in a DAG.

Real uses: **critical path method** in project scheduling (longest path through task dependencies), scheduling lower bounds with unlimited parallel resources, and the **Viterbi algorithm** (most likely path through a layered DAG of hidden states over time).

For shortest paths with nonnegative weights, the correctness proof of Dijkstra's algorithm gives a safe order for finalising distances even on cyclic graphs. This is not a topological order of all graph edges.

## Key takeaways
- A topological order finalises every predecessor before its outgoing edges.
- DAG longest and shortest paths support negative edges.
- Acyclic DP dependencies and safe shortest-path settling orders are different ideas.

## Further reading
- [Topological sorting](https://cp-algorithms.com/graph/topological-sort.html)
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
