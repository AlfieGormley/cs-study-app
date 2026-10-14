---
id: graph-prim-boruvka
title: Prim keys, dense graphs and Borůvka rounds
level: intermediate
minutes: 4
sourceLesson: graph-mst
summary: Prim uses an attaching-edge cost, while Dijkstra uses a path cost.
---

The running example has A–B 4, A–C 1, B–C 2, B–D 5, C–D 8, C–E 10, D–E 2, D–F 6 and E–F 3. Its MST weighs 13. The code numbers vertices from zero; letter names are used for the explanatory trace. Here n counts vertices and m counts edges.

## Prim's algorithm

Prim grows **one tree** from a start vertex. At each step it adds the lightest edge leaving the tree. (Cut property again: the cut is "tree versus everything else".)

```python
import heapq

def prim(n, adj, s=0):
    if n == 0:
        return 0, []
    if not 0 <= s < n:
        raise ValueError("invalid start")
    in_tree = [False] * n
    pq = [(0, s, -1)]  # (weight, v, from)
    total, tree = 0, []
    while pq:
        w, u, frm = heapq.heappop(pq)
        # Ignore other queued ways to attach
        # u.
        if in_tree[u]:
            continue
        in_tree[u] = True
        total += w
        # The initial root has no attaching
        # edge.
        if frm != -1:
            tree.append((frm, u, w))
        for v, wv in adj[u]:
            if not in_tree[v]:
                item = (wv, v, u)
                heapq.heappush(pq, item)
    return total, tree
```

From A on the example: A, then C (1), B (2 via C), D (5 via B), E (2 via D), F (3 via E). Total 13, the same tree found in a different order.

It looks almost exactly like Dijkstra. The one difference is the key used to order the min-heap:

```formula
key_D(v) = dist(u) + w(u, v)
key_P(v) = w(u, v)
where
u: a vertex already in the tree (or already settled)
v: a neighbour of u not yet in it
w(u, v): the weight of the edge between them
dist(u): u's shortest distance from the source
key_D(v): Dijkstra's priority for v: the total distance from the source
key_P(v): Prim's priority for v: just the cost of the single edge that attaches v
In words: Dijkstra asks "how far is v from the start?", Prim asks "how cheaply can v be attached?".
```

In the example, D reached from B (distance three from A via C) gets Dijkstra key eight but Prim key five.

**Time:** for n vertices and m edges, the shown lazy min-heap uses O(n + m log(m + 1)) time and O(n + m) space. For connected simple graphs this is O(m log n). An indexed decrease-key min-heap gives O((n + m) log(n + 1)); array selection gives O(n² + m), attractive for dense graphs without guaranteeing the fastest measured runtime.

## Kruskal or Prim?

In the table, n is the number of vertices and m the number of edges.

| | Kruskal | Prim |
|---|---|---|
| Input | Edge list | Adjacency list |
| Time, connected simple graph | O(m log(m + 1)) | O(m log(n + 1)) |
| Dense graphs | Sort hurts | O(n²) array |
| Grows | A forest | One tree |
| Disconnected | Gives forest | One component |

Both are fine for most problems. Kruskal is simpler to write if you have a DSU handy; Prim with an array is the choice for complete graphs, such as points in the plane where every pair is an edge.

A third algorithm, **Borůvka's**, selects a cheapest outgoing edge from every component. Resolve equal weights consistently or use Union-Find to discard cycle-forming selected edges. On a connected graph, every component joins at least one other in each round, so the count at least halves:

```formula
c_{i+1} ≤ c_i / 2
R ≤ ⌈log_2(n)⌉
R ≤ ⌈log_2(1000)⌉ = 10
where
c_i: the number of components before round i; c_1 = n
c_{i+1}: the number after that round
i: the round number
n: the number of vertices; 1,000 in the example
R: the number of rounds until one component remains
log_2: the base-2 logarithm
⌈ ⌉: ceiling: round up to a whole number
≤: is at most
In words: halving the component count each round reaches one component in about log₂ n rounds.
```

A thousand vertices need at most 10 rounds. Isolated components in a disconnected graph cannot merge. Its per-component edge choices expose parallel work, and distributed and GPU MST implementations use variants of this approach. Synchronisation, communication and hardware determine their performance.

## Key takeaways
- Prim uses an attaching-edge cost, while Dijkstra uses a path cost.
- Array selection is a useful dense-graph alternative to min-heaps.
- Borůvka merges components in logarithmically many rounds on connected input.

## Further reading
- [Primary reference for this unit](https://algs4.cs.princeton.edu/43mst/)
- [Prim's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Prim%27s_algorithm)
- [GPU MST research implementation](https://userweb.cs.txstate.edu/~burtscher/research/ECL-MST/)
- [Engineering massively parallel MST algorithms](https://arxiv.org/abs/2302.12199)
