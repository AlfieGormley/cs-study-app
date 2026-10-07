---
id: adv-union-find
title: Union-Find in depth
level: intermediate
minutes: 13
summary: The disjoint-set forest, why path compression and union by rank or size make it almost O(1), and how it powers Kruskal's algorithm, connectivity and accounts merging.
---

**Union-Find** (also called a **disjoint-set union**, or DSU) keeps track of elements split into non-overlapping groups. It supports two operations:

- `find(x)`: which group is `x` in? It returns a **representative** element for the group.
- `union(a, b)`: merge the groups containing `a` and `b`.

Two elements are in the same group exactly when `find(a) == find(b)`. That one comparison answers "are these connected?" for road networks, friend circles, pixels in an image or accounts that share an email address.

It is tiny to implement, and with two simple tricks each operation costs so little that for any input you could ever store it is effectively constant.

## The idea: a forest of parent pointers

Each group is a tree. Every element points to a parent; the root points to itself and is the group's representative. All you store is one array, `parent`.

```
parent = [0, 0, 1, 3, 3]

  0       3
  |       |
  1       4
  |
  2
groups: {0, 1, 2} and {3, 4}
```

- `find(x)` follows parent pointers up to the root.
- `union(a, b)` finds both roots and makes one the parent of the other.

The naive version has a problem. Union in an unlucky order (`union(1, 0)`, `union(2, 1)`, `union(3, 2)` and so on, always hanging the old tree under the new element) builds a chain, and `find` on the bottom element walks all n links. A sequence of operations costs O(n) each in the worst case.

## Fix 1: union by size or by rank

When merging, **hang the smaller tree under the larger one**. "Smaller" can mean:

- **size**: number of elements in the tree, or
- **rank**: an upper bound on the tree's height. Two rank-r trees merge into a rank-(r + 1) tree; otherwise the lower rank goes under the higher and ranks do not change.

For union by size, an element only gets deeper when its tree is merged under a tree at least as big. Each time that happens, the size of the tree containing it at least **doubles**. A size can only double log2(n) times before it exceeds n, so no element is ever more than log2(n) levels deep. That makes `find` O(log n) in the worst case.

For union by rank, a separate induction shows that a rank-r root represents at least 2^r elements: rank rises only when two equal-rank roots merge. Parent ranks strictly increase, so height is at most rank ≤ floor(log2 n).

Size is often more useful in practice, because you get the group sizes for free ("how big is the largest friend circle?").

## Fix 2: path compression

`find` already walks from `x` to the root. While doing so, **repoint every node on the path directly at the root**. Without an intervening union, the next `find` on a non-root node on that path takes one parent step.

```
before find(4)        after find(4)
     0                     0
     |                  / | | \
     1                 1  2 3  4
     |
     2
     |
     3
     |
     4
```

Variants such as **path halving** (point each node at its grandparent as you go) achieve the same bounds in a single pass.

## The full structure

```python
class DSU:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n
        self.count = n   # number of sets

    def find(self, x):
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        # second pass: compress the path
        while self.parent[x] != root:
            nxt = self.parent[x]
            self.parent[x] = root
            x = nxt
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False   # already joined
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        # smaller tree goes under bigger
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]
        self.count -= 1
        return True
```

> [!tip] Iterative find in Python
> The textbook recursive `find` (`parent[x] = find(parent[x])`) is elegant, but an unbalanced variant can create a chain exceeding the interpreter's recursion limit. Union by size or rank already prevents such linear-depth chains. The two-pass loop above has no such limit.

Note that `union` returns whether a merge actually happened. That boolean is what most applications use.

## How fast is it?

| Version | Cost per operation |
|---|---|
| Naive | O(n) worst case |
| Union by size or rank | O(log n) worst case |
| Path compression only | O(log n) amortised |
| Both | O(α(n)) amortised |

**α(n)** is the inverse Ackermann function. The Ackermann function grows so absurdly fast that under common conventions, its inverse is at most 4 for any n up to a number vastly larger than the count of atoms in the observable universe. In practice, treat each operation as constant time; just say "amortised inverse Ackermann" when asked.

This bound, proved by Robert Tarjan in 1975, is also tight: Fredman and Saks showed in 1989 that a matching inverse-Ackermann lower bound holds in the cell-probe model with logarithmic-size words for suitable operation sequences.

"Amortised" matters. An individual `find` can still walk a long path once, but it flattens that path as it goes, so m operations after initialisation cost O(m α(n)); allocating n singleton sets additionally costs O(n).

> [!note] Rank after compression
> Path compression changes heights but never updates ranks. That is fine: rank was only ever an *upper bound* on height, but the inverse-Ackermann proof also uses rank-growth and node-count invariants, not just this upper bound.

## Application 1: Kruskal's minimum spanning tree

Kruskal's algorithm builds a minimum spanning tree by taking edges cheapest first and keeping an edge only if it joins two different components. "Different components?" is exactly `find(u) != find(v)`, and keeping the edge is `union(u, v)`.

```python
def kruskal(n, edges):
    # edges: list of (weight, u, v)
    dsu = DSU(n)
    total, used = 0, []
    for w, u, v in sorted(edges):
        if dsu.union(u, v):
            total += w
            used.append((u, v))
    return total, used
```

Initialising the DSU costs O(V), sorting O(E log E), and processing edges O(E α(V)). For a connected graph with V ≥ 2, the comparison-sort term dominates asymptotically. Disconnected graphs may instead be dominated by initialisation; the code returns a minimum spanning forest. You can stop early once `used` has V − 1 edges.

## Application 2: connectivity and cycle detection

- **Number of connected components**: start with `count = n` and decrement on every successful union. Edges can arrive one at a time ("number of islands II", or a network where links come up over time), and you can answer after each one.
- **Cycle detection in an undirected graph**: adding edge (u, v) when `find(u) == find(v)` closes a cycle. `union` returning `False` is the signal. This is the "redundant connection" problem.
- **Percolation**: a grid percolates when a virtual top node and a virtual bottom node end up in the same set, a classic Monte Carlo experiment.

Compared with BFS or DFS, union-find shines when edges arrive **incrementally**. A straightforward BFS connectivity check may traverse the current graph for each request; union-find just absorbs each new edge.

## Application 3: accounts merge

Each account is a name plus a list of emails. In this exercise, sharing an email is a trusted signal to merge accounts, and we take its transitive closure: A shares with B and B shares with C, so all three join one component. Directly sharing an email is not itself transitive. Assume each account has at least one email and merged accounts have consistent names; real entity resolution needs stronger domain rules.

Union the account indices through shared emails:

```python
def merge_accounts(accounts):
    dsu = DSU(len(accounts))
    owner = {}   # email -> account index
    for i, acc in enumerate(accounts):
        for email in acc[1:]:
            if email in owner:
                dsu.union(i, owner[email])
            else:
                owner[email] = i
    groups = {}
    for email, i in owner.items():
        r = dsu.find(i)
        groups.setdefault(r, [])
        groups[r].append(email)
    return [[accounts[r][0]] + sorted(es)
            for r, es in groups.items()]
```

The same shape appears in **entity resolution** (deduplicating customer records that share a phone number or address), clustering, and compilers: type inference in ML-family languages unifies type variables with a union-find structure.

## Variants worth knowing

- **Weighted union-find** stores, for each node, a value relative to its parent (an offset, a ratio, a parity bit). `find` accumulates values along the path. This solves "evaluate division" (`a / b = 2`, `b / c = 3`, so `a / c = 6`) and "is this graph bipartite?" online.
- **Offline deletion**: union-find cannot split a set. If edges are *removed* over time, a standard trick is to process the operations in reverse, so removals become additions.
- **Hash-map parents**: when elements are strings or sparse coordinates, use a dict instead of a list, creating entries on first sight.

## Pitfalls

- **Comparing parents, not roots.** `parent[a] == parent[b]` is not the same as being connected. Always compare `find(a)` and `find(b)`.
- **Linking non-roots.** `parent[b] = a` instead of `parent[find(b)] = find(a)` loses the rest of b's tree.
- **Forgetting it is undirected.** Union-find has no notion of direction, so it cannot detect cycles in a directed graph or find strongly connected components. Use DFS-based algorithms for those.

## Key takeaways
- Union-Find stores a forest of parent pointers; two elements are connected exactly when they have the same root.
- Union by size or rank caps tree height at log2(n); path compression flattens paths as `find` walks them.
- Together they give O(α(n)) amortised per operation, effectively constant, with a matching lower bound under the stated cell-probe assumptions.
- It powers Kruskal's MST (where sorting dominates on connected graphs), incremental connectivity, undirected cycle detection and accounts merging.
- It cannot split sets or handle direction; reverse the operations or use graph search instead.

## Further reading
- [Disjoint-set data structure — Wikipedia](https://en.wikipedia.org/wiki/Disjoint-set_data_structure)
- [Disjoint Set Union — cp-algorithms](https://cp-algorithms.com/data_structures/disjoint_set_union.html)
- [Kruskal's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Kruskal%27s_algorithm)
- [Ackermann function — Wikipedia](https://en.wikipedia.org/wiki/Ackermann_function)
