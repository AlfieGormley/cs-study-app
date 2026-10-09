---
id: graph-mst
title: Minimum spanning trees and Union-Find
level: intermediate
minutes: 13
summary: The cut property, Kruskal's and Prim's algorithms, and the Union-Find structure whose path compression and union by rank make operations effectively constant time.
---

You need to connect 6 offices with fibre. Assume each possible link has a positive installation cost. Every office must be reachable from every other, and you want to spend as little as possible. You will never buy a link that closes a loop, because a loop always contains a link you could drop while keeping everything connected.

So the answer is a **tree** that spans every vertex: a **minimum spanning tree (MST)**. For a connected undirected graph it has a fixed number of edges and the smallest possible total weight:

```formula
|T| = n − 1
W(T) = Σ w(e)   for e in T
W(T) = 1 + 2 + 2 + 3 + 5 = 13
where
T: a spanning tree: a set of edges that connects every vertex with no cycle
|T|: the number of edges in T
n: the number of vertices; 6 offices in the example
e: one edge of T
w(e): the weight (cost) of edge e
W(T): the total weight of the tree
Σ: add up over every edge e in T
In words: a spanning tree always has one edge fewer than it has vertices, and the MST is the spanning tree whose edge weights add up to the least.
```

Throughout this lesson, n is the number of vertices, m the number of edges, and O(…) is Big O notation: how the running time grows, ignoring constant factors.

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

A **cut** splits the vertices into two non-empty groups. An edge **crosses** the cut if it has one end on each side:

```formula
(S, V − S)
where
V: the set of all vertices
S: the vertices on one side of the cut; not empty, and not all of V
V − S: every vertex not in S (the other side)
( , ): the pair of sides that makes up the cut
In words: a cut is a way of dividing the vertices into two non-empty groups.
```

For example, S = {A, C} cuts the example graph; the crossing edges are A–B 4, B–C 2, C–D 8 and C–E 10, and the lightest is B–C.

> [!note] Cut property
> For any cut, the lightest edge crossing it belongs to some MST. If it is strictly the lightest, it belongs to every MST.

Proof sketch: take an MST T that does not contain the lightest crossing edge e. Adding e to T creates a cycle, and that cycle must cross the cut a second time at some edge f. Exchange f for e:

```formula
W(T′) = W(T) + w(e) − w(f) ≤ W(T)
where
T: an MST that does not contain e
e: the lightest edge crossing the cut
f: another edge of the new cycle that crosses the cut
w(e), w(f): their weights, with w(e) ≤ w(f)
T′: T with f removed and e added
W(T), W(T′): the total weights of the two trees
≤: is at most
In words: exchanging f for the lighter crossing edge never makes the tree heavier, so a tree containing e is also minimum.
```

T′ is still a spanning tree, so some MST contains e.

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

The only hard part is the cycle test: "are u and v already connected by chosen edges?" Running a BFS each time would cost O(n) per edge, for n vertices. That is what **Union-Find** is for.

## Union-Find (disjoint set union)

Union-Find maintains a partition of the vertices into disjoint sets, with two operations:

- `find(x)`: which set is x in? (Returns the set representative, the set's root.)
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

Attach the **lower-rank** root under the higher-rank root. After path compression, rank need not equal the current height. Each root keeps a `rank`, an upper bound on its tree's height. A rank only goes up when two trees of equal rank are joined, which at least doubles the smaller size:

```formula
2^r ≤ s ≤ n
r ≤ log_2(n)
r ≤ log_2(10^6) ≈ 20
where
r: the rank of a root (an upper bound on its tree's height)
s: the number of nodes in that tree
n: the total number of elements; 10^6 in the example
log_2: the base-2 logarithm: how many times you can halve n before reaching 1
≤: is at most
≈: approximately equal to
In words: a tree of rank r has at least 2 to the power r nodes, so with a million elements no tree is more than about 20 levels tall.
```

So heights stay O(log n) even without the second trick.

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

Initialising n singleton sets costs O(n). With rank and compression, the total cost is:

```formula
T = O(n + m × α(n))
α(n) ≤ 4
where
n: the number of elements (vertices)
m: the number of find and union operations; in Kruskal, about two finds per edge
α(n): the inverse Ackermann function: a function of n that grows so slowly it stays at most about 4 for any n that fits in a real computer (the exact constant depends on the definition used)
T: the total time for initialisation plus all m operations
O(…): Big O: grows at most this fast, up to a constant factor
≤: is at most
In words: after setting up the n sets, each operation costs a tiny, effectively constant amount on average.
```

So a million operations on a million elements cost on the order of a few million steps in total. Inverse-Ackermann definitions vary by small constants; the function grows extremely slowly. This is an amortised growth bound, not a claim that each call performs at most four instructions. Individual calls can take O(log n).

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

**Time:** sorting dominates:

```formula
T = O(n + m × log(m + 1) + m × α(n))
m ≤ n^2   so   log(m + 1) = O(log(n + 1))
T = O(m × log(n))
where
n: the number of vertices
m: the number of edges
log: the logarithm (base 2)
α(n): the inverse Ackermann function, at most about 4 in practice
T: Kruskal's total running time
O(…): Big O: grows at most this fast, up to a constant factor
≤: is at most
In words: sorting m edges costs about m log m, Union-Find adds almost nothing, and since a simple graph has at most n² edges, log m is at most about twice log n.
```

The last line holds for connected simple graphs. For a million edges, log₂ m ≈ 20, so the sort costs on the order of 2 × 10⁷ comparisons.

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

It looks almost exactly like Dijkstra. The one difference is the key used to order the heap:

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

In the example, D reached from B (distance 3 from A via C) gets Dijkstra key 8 but Prim key 5.

**Time:** for n vertices and m edges, the shown lazy heap uses O(n + m log(m + 1)) time and O(n + m) space. For connected simple graphs this is O(m log n). An indexed decrease-key heap gives O((n + m) log(n + 1)); array selection gives O(n² + m), attractive for dense graphs without guaranteeing the fastest measured runtime.

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

A thousand vertices need at most 10 rounds. Isolated components in a disconnected graph cannot merge. It parallelises well and is used in distributed and GPU MST implementations.

## Where MSTs are used

- **Network design**: cabling, pipelines, power grids (the problem Borůvka originally studied in 1926, for electrifying Moravia).
- **Clustering**: run Kruskal but stop when k components remain (k is the number of clusters you want). For a complete graph of pairwise dissimilarities, the result is single-linkage clustering, maximising the minimum distance between clusters. On a sparse graph, spacing refers only to edges present in that graph.
- **Approximation algorithms**: doubling an MST and shortcutting repeated vertices gives a tour at most 2× optimal for metric TSP (where going direct is never longer than a detour). See the formula after this list.
- **Union-Find on its own**: incremental undirected connectivity, image segmentation, percolation simulations, and type unification in compilers.

The 2× bound for the travelling salesman problem comes from two inequalities:

```formula
L ≤ 2 × W(MST) ≤ 2 × L*
L ≤ 2 × 100 = 200
where
L: the length of the tour built from the doubled MST
W(MST): the total weight of the minimum spanning tree; 100 in the example
L*: the length of the best possible tour
≤: is at most
In words: walking round the tree uses each edge twice, shortcuts never add length, and any tour minus one edge is a spanning tree, so the MST is no heavier than the best tour.
```

So if the MST weighs 100 km, the tour is at most 200 km, and the best tour is at least 100 km.

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
