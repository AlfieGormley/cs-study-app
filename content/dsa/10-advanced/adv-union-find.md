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

The naive version has a problem. Union in an unlucky order (`union(1, 0)`, `union(2, 1)`, `union(3, 2)` and so on, always hanging the old tree under the new element) builds a chain, and `find` on the bottom element walks every link in it: one fewer link than there are elements. If n is the number of elements, a sequence of operations can cost O(n) each in the worst case (O(n) means "grows in proportion to n").

## Fix 1: union by size or by rank

When merging, **hang the smaller tree under the larger one**. "Smaller" can mean:

- **size**: number of elements in the tree, or
- **rank**: an upper bound on the tree's height. Every element starts with rank 0.

The rank rule for merging two roots fits in two lines:

```formula
r_new = r + 1   if r_a = r_b = r
r_new = max(r_a, r_b)   otherwise
where
r_a: the rank of the first root being merged, a whole number starting at 0
r_b: the rank of the second root being merged
r: the shared rank, when both roots have the same rank
r_new: the rank of the merged tree's root
max(r_a, r_b): the larger of the two ranks
In words: two trees of equal rank make a tree one rank higher; otherwise the lower-rank root goes under the higher one and no rank changes.
```

So two rank-2 trees make a rank-3 tree, while a rank-1 tree hung under a rank-3 root leaves the rank at 3.

For union by size, an element only gets deeper when its tree is merged under a tree at least as big. Each time that happens, the size of the tree containing it at least **doubles**. A tree can never hold more than all n elements, which caps how many doublings there can be:

```formula
2^d ≤ n
d ≤ log_2(n)
d ≤ log_2(1,000,000) ≈ 19.9
where
d: the depth of an element: how many parent steps it is below its root
n: the total number of elements in the structure
2^d: 2 multiplied by itself d times; the smallest its tree's size can be after it has been pushed down d times
log_2(n): the base-2 logarithm of n: the power you raise 2 to in order to get n
≤: is at most
≈: approximately equal to
In words: every step deeper at least doubles the element's tree, and a tree cannot outgrow n elements, so no element is ever more than log_2(n) levels deep.
```

With a million elements, no `find` walks more than 19 parent steps. That makes `find` O(log n) in the worst case: its cost grows in proportion to the logarithm of n. The bound assumes every union goes through the size rule; a single careless `parent[b] = a` breaks it.

For union by rank, a separate induction (a proof that the claim holds for rank 0 and stays true after every merge) bounds the tree size by its rank. Rank rises only when two equal-rank roots merge, which at least doubles the smaller one:

```formula
s(x) ≥ 2^{r(x)}
r(x) ≤ ⌊log_2(n)⌋
h(x) ≤ r(x)
r(x) ≤ ⌊log_2(1000)⌋ = 9
where
x: any root in the forest
r(x): the rank of root x, a whole number starting at 0
s(x): the number of elements in x's tree
2^{r(x)}: 2 multiplied by itself r(x) times
h(x): the height of x's tree: the longest path of parent steps from an element up to x
n: the total number of elements
log_2(n): the base-2 logarithm of n
⌊ ⌋: floor: round down to the nearest whole number
≥: is at least
≤: is at most
In words: a root of rank r holds at least 2^r elements, so with n elements no rank, and so no tree height, can exceed log_2(n) rounded down.
```

With 1,000 elements, log_2(1000) ≈ 9.97, so no rank exceeds 9. Parent ranks strictly increase on every path up the tree, which is why the height can be no larger than the root's rank.

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

In this table n is the number of elements and m is the number of operations performed. O(f) means "grows at most in proportion to f".

| Version | Cost per operation |
|---|---|
| Naive | O(n) worst case |
| Union by size or rank | O(log n) worst case |
| Path compression only | O(log n) amortised |
| Both | O(α(n)) amortised |

**α(n)** is the inverse Ackermann function. The Ackermann function A grows so absurdly fast that its inverse barely moves. Under one common convention it is defined like this:

```formula
α(n) = min k such that A(k, k) ≥ n
A(1, 1) = 3
A(2, 2) = 7
A(3, 3) = 61
α(61) = 3
α(n) ≤ 4   for all n ≤ A(4, 4)
α(10^9) = 4
where
α(n): alpha of n, the inverse Ackermann function: the smallest whole number k for which A(k, k) reaches n
A(k, k): the two-argument Ackermann–Péter function with both arguments equal to k; each step up in k makes it explode
A(4, 4): 2 raised to the power (2 raised to the power (2 raised to the power 65536)), minus 3: vastly more than the roughly 10^80 atoms in the observable universe
k: a whole number 0, 1, 2, …
n: the number of elements in the union-find structure
min: the smallest value that satisfies the condition
≥: is at least
≤: is at most
In words: α(n) is the number of times you must step up the Ackermann ladder before it passes n, and for every n you could ever store that is at most 4.
```

The last line is the worked example: a billion elements is more than A(3, 3) = 61 but far less than A(4, 4), so alpha of a billion is 4. Other textbooks use slightly different conventions and get 3 or 5 instead, but always a tiny constant. In practice, treat each operation as constant time; just say "amortised inverse Ackermann" when asked.

This bound, proved by Robert Tarjan in 1975, is also tight: Fredman and Saks showed in 1989 that a matching inverse-Ackermann lower bound holds in the cell-probe model with logarithmic-size words for suitable operation sequences.

"Amortised" matters. An individual `find` can still walk a long path once, but it flattens that path as it goes. Averaged over a whole sequence, the total is bounded:

```formula
T(m) = O(m × α(n))
T_init = O(n)
where
T(m): the total time for m find and union operations after the structure is set up
T_init: the one-off time to create n singleton sets (one element each)
m: the number of operations
n: the number of elements
α(n): the inverse Ackermann function of n, at most 4 in practice
O(f): "grows at most in proportion to f", ignoring constant factors
In words: m operations together cost about m times a tiny constant, plus a one-off cost proportional to n to set things up.
```

For example, 10 million operations on a million elements cost on the order of 10 million × 4 = 40 million basic steps, plus a million to initialise. One unlucky `find` inside that run may be slow; the bound is only on the total.

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

Here V is the number of vertices and E the number of edges. The three phases add up:

```formula
T = O(V) + O(E × log(E)) + O(E × α(V))
T_c = O(E × log(E))
E ≥ V − 1
E × log_2(E) ≈ 10,000 × 13.3 ≈ 133,000
E × α(V) = 10,000 × 4 = 40,000
where
T: the total running time of Kruskal's algorithm
T_c: the total running time when the graph is connected (every vertex reachable from every other) and V ≥ 2
V: the number of vertices (nodes) in the graph
E: the number of edges in the graph
log(E): the logarithm of E; the base only changes a constant factor
log_2(E): the base-2 logarithm of E, about the number of comparison rounds a good sort needs per edge
α(V): the inverse Ackermann function of V, at most 4 in practice
O(f): "grows at most in proportion to f"
≥: is at least
≈: approximately equal to
In words: initialising the DSU, sorting the edges and processing them add up, and on a connected graph sorting the edges is the part that dominates.
```

A connected graph needs at least one edge fewer than it has vertices (the third line), so the sort outgrows both other terms. The last two lines are a worked example with 1,000 vertices and 10,000 edges: about 133,000 comparisons to sort against about 40,000 DSU steps. Disconnected graphs may instead be dominated by initialisation; the code returns a minimum spanning forest. You can stop early once `used` has V − 1 edges.

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

- **Weighted union-find** stores, for each node, a value relative to its parent (an offset, a ratio, a parity bit). `find` accumulates values along the path. This solves "evaluate division" (given some ratios between variables, work out others, as in the block below) and "is this graph bipartite?" online.

```formula
a / b = 2
b / c = 3
a / c = (a / b) × (b / c) = 2 × 3 = 6
where
a, b, c: unknown non-zero quantities that are only described by their ratios to each other
In words: if a is twice b and b is three times c, then a is six times c; weighted union-find stores each ratio on the edge to the parent and multiplies along the path to the root.
```

- **Offline deletion**: union-find cannot split a set. If edges are *removed* over time, a standard trick is to process the operations in reverse, so removals become additions.
- **Hash-map parents**: when elements are strings or sparse coordinates, use a dict instead of a list, creating entries on first sight.

## Pitfalls

- **Comparing parents, not roots.** `parent[a] == parent[b]` is not the same as being connected. Always compare `find(a)` and `find(b)`.
- **Linking non-roots.** `parent[b] = a` instead of `parent[find(b)] = find(a)` loses the rest of b's tree.
- **Forgetting it is undirected.** Union-find has no notion of direction, so it cannot detect cycles in a directed graph or find strongly connected components. Use DFS-based algorithms for those.

## Key takeaways
- Union-Find stores a forest of parent pointers; two elements are connected exactly when they have the same root.
- Union by size or rank caps tree height at log_2(n), where n is the number of elements; path compression flattens paths as `find` walks them.
- Together they give O(α(n)) amortised per operation, where α is the inverse Ackermann function, effectively constant, with a matching lower bound under the stated cell-probe assumptions.
- It powers Kruskal's MST (where sorting dominates on connected graphs), incremental connectivity, undirected cycle detection and accounts merging.
- It cannot split sets or handle direction; reverse the operations or use graph search instead.

## Further reading
- [Disjoint-set data structure — Wikipedia](https://en.wikipedia.org/wiki/Disjoint-set_data_structure)
- [Disjoint Set Union — cp-algorithms](https://cp-algorithms.com/data_structures/disjoint_set_union.html)
- [Kruskal's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Kruskal%27s_algorithm)
- [Ackermann function — Wikipedia](https://en.wikipedia.org/wiki/Ackermann_function)
