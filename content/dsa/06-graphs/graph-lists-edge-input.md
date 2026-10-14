---
id: graph-lists-edge-input
title: Adjacency lists and edge-list input
level: basic
minutes: 4
sourceLesson: graph-fundamentals
summary: Initialise isolates and sinks before adding edges.
---

Earlier units established direction, paths and density. Here n counts vertices and m counts edges; deg(u) is vertex u’s degree.

## Representation 1: adjacency list

For each vertex, store a list of its neighbours. In Python, a dict of lists (or a list of lists when vertices are numbered 0..n−1).

```
graph:  0 - 1, 0 - 2, 1 - 2, 2 - 3

adj = {
  0: [1, 2],
  1: [0, 2],
  2: [0, 1, 3],
  3: [2],
}
```

```python
def build_adj(vertices, edges,
              directed=False):
    adj = {v: [] for v in vertices}
    # Visit each input edge once.
    for u, v in edges:
        # Store this direction of the edge.
        adj[u].append(v)
        if not directed:
            # Undirected edges need both
            # directions.
            adj[v].append(u)
    return adj
```

Pass every vertex explicitly, including isolates and directed sinks; each edge endpoint must belong to that set. Complexity assumes constant-size labels and expected O(1) dictionary/set operations. For a weighted graph, store pairs: `adj[u].append((v, w))`.

The memory is one slot per vertex plus one list entry per edge end:

```formula
S = n + 2m
S = 4 + 2 × 4 = 12
where
S: the number of stored items (dictionary keys plus list entries) in an undirected adjacency list
n: the number of vertices
m: the number of edges; each undirected edge is stored in both endpoints' lists
In words: the storage grows with the vertex count plus twice the edge count; for a directed graph it is n + m.
```

The example has four vertices and four edges: four keys plus eight neighbour entries, twelve items in all. In the costs below, n is the number of vertices, m the number of edges and deg(u) the degree of vertex u. O(…) is Big O notation: how the cost grows as the graph grows, ignoring constant factors.

- **Space:** O(n + m). Each undirected edge is stored twice, each directed edge once.
- **Iterate neighbours of u:** O(1 + deg(u)), which is exactly what BFS, DFS and Dijkstra need.
- **Is there an edge u→v?** O(1 + deg(u)) by scanning. Replace the inner lists with sets to make it O(1) on average.

This is the default for almost every algorithm in this module.

## Representation 3: edge list

Just a list of `(u, v)` or `(u, v, w)` tuples.

```python
# Triples store start, end and weight.
edges = [(0, 1, 4), (0, 2, 1), (2, 1, 2)]
```

Here m is the number of edges.

- **Space:** O(m) for edges, plus any separately stored vertex set.
- Requires a full scan for "who are u's neighbours?" (O(m) scan).
- Perfect when an algorithm processes edges as a whole: **Kruskal's** MST sorts the edges, and **Bellman–Ford** relaxes every edge each round.

It is also how graphs usually arrive: a CSV of flights, a table of `follower_id, followee_id` rows. You read the edge list, then build whatever structure the algorithm needs.

## Comparison

As before, n is the number of vertices, m the number of edges and deg u the degree of vertex u.

| Operation | List | Matrix | Edges |
|---|---|---|---|
| Space | O(n + m) | O(n²) | O(m) |
| Edge u→v? | O(1 + deg u) | O(1) | O(m) |
| Neighbours | O(1 + deg u) | O(n) | O(m) |
| Add edge | O(1) amortised | O(1) | O(1) amortised |

Traversing all vertices costs O(n + m) with adjacency lists and O(n²) with a matrix. A traversal from one source scans only reachable vertices; the displayed bounds are whole-graph upper bounds. These are growth rates, not measured elapsed times.

## Pitfalls

- **Forgetting the reverse edge** in an undirected graph: add both `adj[u].append(v)` and `adj[v].append(u)`, or some intended paths may be lost.
- **Isolated vertices** vanish from an adjacency dict built only from edges. If vertex 7 has no edges, it never appears, and a "count components" loop will undercount. Initialise all n vertices first.
- **Parallel edges and graph self-loops.** Real data often contains duplicates. Decide whether they matter (they change degree counts and can break algorithms that assume a simple graph).
- **Recursion limits.** Python limits recursion depth (inspect `sys.getrecursionlimit()`); a sufficiently long path can raise `RecursionError`. Prefer iterative versions for large inputs.

## Key takeaways
- Initialise isolates and sinks before adding edges.
- Use lists to scan neighbours and an edge list to process edges globally.

## Further reading
- [Primary reference for this unit](https://networkx.org/documentation/stable/reference/classes/digraph.html)
- [Adjacency list — Wikipedia](https://en.wikipedia.org/wiki/Adjacency_list)
- [Kruskal's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Kruskal%27s_algorithm)
