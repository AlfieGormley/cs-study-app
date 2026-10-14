---
id: graph-spanning-cuts
title: Minimum spanning trees and safe cut edges
level: intermediate
minutes: 4
sourceLesson: graph-mst
summary: An MST minimises the sum of chosen edge weights.
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

For example, putting A and C on one side cuts the example graph; the crossing edges are A–B 4, B–C 2, C–D 8 and C–E 10, and the lightest is B–C.

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

Every spanning tree uses the same number of edges. Therefore adding one constant to every edge shifts every tree total equally and preserves the MST ranking. A globally heaviest edge can still be necessary if it is the only link joining two regions.

## Key takeaways
- An MST minimises the sum of chosen edge weights.
- The cut exchange argument justifies greedy edge choices.
- Distinct weights ensure uniqueness; ties need not.

## Further reading
- [Primary reference for this unit](https://algs4.cs.princeton.edu/43mst/)
- [Minimum spanning tree — Wikipedia](https://en.wikipedia.org/wiki/Minimum_spanning_tree)
- [Kruskal's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Kruskal%27s_algorithm)
