---
id: graph-mst
title: Minimum spanning trees and Union-Find
level: intermediate
minutes: 13
summary: The cut property, Kruskal's and Prim's algorithms, and the Union-Find structure whose path compression and union by rank make operations effectively constant time.
---

You need to connect 6 offices with fibre. Assume each possible link has a positive installation cost. Every office must be reachable from every other, and you want to spend as little as possible. You will never buy a link that closes a loop, because a loop always contains a link you could drop while keeping everything connected.

So the answer is a **tree** that spans every vertex: a **minimum spanning tree (MST)**. For a connected undirected graph with n vertices it has exactly n − 1 edges and the smallest possible total weight.

## The example

```
A ---4--- B ---5--- D ---6--- F
  \       |      /  |      /
     1    2    8    2    3
       \  | /       | /
          C --10--- E
```

Edges: A–B 4, A–C 1, B–C 2, B–D 5, C–D 8, C–E 10, D–E 2, D–F 6, E–F 3.

The MST is A–C 1, B–C 2, D–E 2, E–F 3, B–D 5, with total weight **13**.

## Why greedy works: the cut property

A **cut** splits the vertices into two non-empty groups S and V − S. An edge **crosses** the cut if it has one end on each side.

> [!note] Cut property
> For any cut, the lightest edge crossing it belongs to some MST. If it is strictly the lightest, it belongs to every MST.

Proof sketch: take an MST T that does not contain the lightest crossing edge e. Adding e to T creates a cycle, and that cycle must cross the cut a second time at some edge f. Swap f for e: still a spanning tree, and no heavier, since w(e) ≤ w(f). So some MST contains e.

The companion **cycle property** says the heaviest edge on any cycle is never needed (if it is strictly heaviest). Both Kruskal and Prim are just ways of repeatedly applying the cut property.

A consequence: **if all edge weights are distinct, the MST is unique.**

## Kruskal's algorithm

Sort all edges by weight. Walk through them, adding each edge unless it would form a cycle with edges already chosen.

On the example:

| Edge | Weight | Action |
|---|---|---|
| A–C | 1 | add |
| B–C | 2 | add |
| D–E | 2 | add |
| E–F | 3 | add |
| A–B | 4 | skip: A, B joined |
| B–D | 5 | add (5 edges: done) |

Each added edge is the lightest edge crossing the cut between its endpoint's current component and everything else, so the cut property guarantees it is safe.

The only hard part is the cycle test: "are u and v already connected by chosen edges?" Running a BFS each time would cost O(n) per edge. That is what **Union-Find** is for.

## Union-Find (disjoint set union)

Union-Find maintains a partition of the vertices into disjoint sets, with two operations:

- `find(x)`: which set is x in? (Returns a representative, the set's root.)
- `union(a, b)`: merge the sets containing a and b.

Each set is a tree of parent pointers; the root represents the set.

```
parent: 0  1  2  3  4  5
        0  0  1  3  3  4

  0        3
  |        |
  1        4
  |        |
  2        5
```

`find(2)` follows 2 → 1 → 0. `union(2, 5)` links root 3 under root 0 (or vice versa).

Done naively, these trees can degenerate into long chains and `find` becomes O(n). Two tricks fix that.

### Union by rank

Attach the **lower-rank** root under the higher-rank root. After path compression, rank need not equal the current height. Each root keeps a `rank`, an upper bound on its tree's height. A tree of rank r has at least 2ʳ nodes, so heights stay O(log n) even without the second trick.

### Path compression

During `find`, point every node on the path straight at the root. Until later unions change the root, a subsequent `find` from one of those non-root nodes follows one parent link.

```
before find(2)     after
  0                  0
  |                 / \
  1                1   2
  |
  2
```

### The code

```python
class DSU:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            root = self.find(self.parent[x])
            self.parent[x] = root  # flatten
        return self.parent[x]

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False  # already joined
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True
```

Union by rank keeps recursion depth O(log n), much smaller than a naive chain; it must still fit the runtime’s configured recursion limit.

### Inverse Ackermann

Initialising n singleton sets costs O(n). With rank and compression, m subsequent operations cost O(m α(n)) amortised, giving O(n + m α(n)) overall. Inverse-Ackermann definitions vary by small constants; the function grows extremely slowly. This is an amortised growth bound, not a claim that each call performs at most four instructions. Individual calls can take O(log n).

| Variant | Cost per op |
|---|---|
| Naive | O(n) worst |
| Union by rank only | O(log n) |
| Path compression only | O(log n) amortised |
| Both | O(α(n)) amortised |

### Kruskal in full

```python
def kruskal(n, edges):  # (w, u, v)
    dsu = DSU(n)
    tree, total = [], 0
    for w, u, v in sorted(edges):
        if dsu.union(u, v):
            tree.append((u, v, w))
            total += w
            if len(tree) == n - 1:
                break
    return total, tree
```

**Time:** O(m log m) for the sort, plus O(m α(n)) for Union-Find. The sort dominates. Including O(n) initialisation, the full bound is O(n + m log(m + 1)). For simple graphs m ≤ n², so log(m + 1) = O(log(n + 1)), so for connected simple graphs this is also written O(m log n).

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
        if in_tree[u]:
            continue
        in_tree[u] = True
        total += w
        if frm != -1:
            tree.append((frm, u, w))
        for v, wv in adj[u]:
            if not in_tree[v]:
                item = (wv, v, u)
                heapq.heappush(pq, item)
    return total, tree
```

From A on the example: A, then C (1), B (2 via C), D (5 via B), E (2 via D), F (3 via E). Total 13, the same tree found in a different order.

It looks almost exactly like Dijkstra. The one difference is the key: Dijkstra uses `dist[u] + w` (the distance from the source), whereas Prim uses just `w` (the cost of the single edge that attaches v).

**Time:** the shown lazy heap uses O(n + m log(m + 1)) time and O(n + m) space. For connected simple graphs this is O(m log n). An indexed decrease-key heap gives O((n + m) log(n + 1)); array selection gives O(n² + m), attractive for dense graphs without guaranteeing the fastest measured runtime.

## Kruskal or Prim?

| | Kruskal | Prim |
|---|---|---|
| Input | Edge list | Adjacency list |
| Time, connected simple graph | O(m log(m + 1)) | O(m log(n + 1)) |
| Dense graphs | Sort hurts | O(n²) array |
| Grows | A forest | One tree |
| Disconnected | Gives forest | One component |

Both are fine for most problems. Kruskal is simpler to write if you have a DSU handy; Prim with an array is the choice for complete graphs, such as points in the plane where every pair is an edge.

A third algorithm, **Borůvka's**, selects a cheapest outgoing edge from every component. Resolve equal weights consistently or use Union-Find to discard cycle-forming selected edges. On a connected graph, a round at least halves the number of components until one remains; isolated components in a disconnected graph cannot merge. It parallelises well and is used in distributed and GPU MST implementations.

## Where MSTs are used

- **Network design**: cabling, pipelines, power grids (the problem Borůvka originally studied in 1926, for electrifying Moravia).
- **Clustering**: run Kruskal but stop when k components remain. For a complete graph of pairwise dissimilarities, the result is single-linkage clustering, maximising the minimum distance between clusters. On a sparse graph, spacing refers only to edges present in that graph.
- **Approximation**: doubling an MST and shortcutting repeated vertices gives a tour at most 2× optimal for metric TSP.
- **Union-Find on its own**: incremental undirected connectivity, image segmentation, percolation simulations, and type unification in compilers.

## Pitfalls

- **MST is not a shortest-path tree.** The MST minimises total weight; the path between two vertices inside it can be much longer than their shortest path.
- **Directed graphs** need a minimum spanning *arborescence* (Chu–Liu/Edmonds' algorithm). Kruskal and Prim do not apply.
- **Disconnected input**: no spanning tree exists. Kruskal returns a minimum spanning forest; check `len(tree) == n - 1`.
- **Negative weights are fine.** Only the relative order of weights matters, unlike Dijkstra.

## Key takeaways
- An MST connects all n vertices with n − 1 edges of minimum total weight; it is unique when weights are distinct.
- The cut property (the lightest edge across any cut is safe) justifies both greedy algorithms.
- Kruskal sorts edges and uses Union-Find to skip cycles: O(n + m log(m + 1)), including initialisation.
- Union-Find with union by rank and path compression costs O(α(n)) amortised per operation, effectively constant.
- Prim grows a tree with single-edge keys: the shown lazy version is O(n + m log(m + 1)); O(m log n) for connected simple graphs. Array selection is O(n² + m).

## Further reading
- [Minimum spanning tree — Wikipedia](https://en.wikipedia.org/wiki/Minimum_spanning_tree)
- [Kruskal's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Kruskal%27s_algorithm)
- [Prim's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Prim%27s_algorithm)
- [Disjoint-set data structure — Wikipedia](https://en.wikipedia.org/wiki/Disjoint-set_data_structure)
- [Disjoint Set Union — cp-algorithms](https://cp-algorithms.com/data_structures/disjoint_set_union.html)
- [Kruskal with DSU — cp-algorithms](https://cp-algorithms.com/graph/mst_kruskal_with_dsu.html)
