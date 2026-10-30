---
id: graph-spanning-cuts
title: Minimum spanning trees and safe cut edges
level: intermediate
minutes: 4
sourceLesson: graph-mst
summary: An MST minimises the sum of chosen edge weights.
---

You need to connect 6 offices with fibre. Assume each possible link has a positive installation cost. Every office must be reachable from every other, and you want to spend as little as possible. You will never buy a link that closes a loop, because a loop always contains a link you could drop while keeping everything connected.

So the answer is a **tree** that spans every vertex: a **minimum spanning tree (MST)**. A spanning tree of a connected undirected graph connects every vertex with no cycle, so it always has one edge fewer than it has vertices: 5 links for 6 offices. The MST is the spanning tree whose edge weights add up to the least.

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

A **cut** splits the vertices into two non-empty groups. An edge **crosses** the cut if it has one end on each side. For example, putting A and C on one side cuts the example graph; the crossing edges are A–B 4, B–C 2, C–D 8 and C–E 10, and the lightest is B–C.

> [!note] Cut property
> For any cut, the lightest edge crossing it belongs to some MST. If it is strictly the lightest, it belongs to every MST.

> [!analogy] Real-world analogy: bridging a river between two halves of a town
> A town is split by a river, and the council will fund links so that everyone can reach everyone. Whatever else the cheapest overall plan contains, it can always use the cheapest of the possible bridges across that river: any plan that crosses the river some other way could exchange that crossing for the cheapest bridge without costing more.
>
> **How it maps:** the two banks are the two sides of a cut, the candidate bridges are the crossing edges, and "the cheapest bridge is always safe to build" is the cut property. Kruskal and Prim keep drawing new "rivers" and building the cheapest bridge across each.
>
> **Where it stops:** a real council might want two bridges for resilience. An MST deliberately has no redundancy, exactly one route between any two vertices, so it is the cheapest connected network, not a robust one.

Proof sketch: take an MST that does not contain the lightest crossing edge. Adding that edge creates a cycle, and the cycle must cross the cut a second time at some other edge. Exchanging that other edge for the lightest one never makes the tree heavier:

```formula reference
W(T′) = W(T) + w(e) − w(f) ≤ W(T)
where
T: an MST that does not contain e
e: the lightest edge crossing the cut
f: another edge of the new cycle that crosses the cut
w(e), w(f): their weights, with w(e) ≤ w(f)
T′: T with f removed and e added
W(T), W(T′): the total weights of the two trees
≤: is at most
In words: swapping the other crossing edge on the cycle for the lightest crossing edge never makes the tree heavier, and the result is still a spanning tree, so some minimum spanning tree contains the lightest crossing edge.
```

The companion **cycle property** says the heaviest edge on any cycle is never needed (if it is strictly heaviest). Both Kruskal and Prim are just ways of repeatedly applying the cut property.

A consequence: **if all edge weights are distinct, the MST is unique.**

Every spanning tree uses the same number of edges. Therefore adding one constant to every edge shifts every tree total equally and preserves the MST ranking. A globally heaviest edge can still be necessary if it is the only link joining two regions.

## Key takeaways
- An MST minimises the sum of chosen edge weights.
- The cut exchange argument justifies greedy edge choices.
- Distinct weights ensure uniqueness; ties need not.

## Further reading
- [Sedgewick and Wayne, Algorithms 4th ed.: 4.3 Minimum spanning trees](https://algs4.cs.princeton.edu/43mst/)
- [Minimum spanning tree — Wikipedia](https://en.wikipedia.org/wiki/Minimum_spanning_tree)
- [Kruskal's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Kruskal%27s_algorithm)
