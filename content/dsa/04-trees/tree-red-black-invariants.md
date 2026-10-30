---
id: tree-red-black-invariants
title: Red-black paths and height
level: intermediate
minutes: 4
sourceLesson: tree-balanced
summary: NIL child positions count as black for the path invariant.
---

Start with the distinct-key BST ordering from the previous units. A rotation must keep the same sorted in-order sequence while changing local links. Here n counts stored keys and h measures real-node height in edges; empty subtrees have height minus one unless a NIL-path convention is explicitly given. Height bounds assume constant-cost key comparisons, rather than measuring application latency.

## Red-black trees

A red-black tree relaxes the invariant. Instead of near-perfect balance, it only promises that root-to-NIL paths differ in length by at most a factor of two. In exchange, it does less restructuring.

Every node is coloured red or black, and empty (NIL) children count as black leaves. The rules:

1. The root is black.
2. A red node has no red children (no two reds in a row).
3. Every path from a node down to a NIL leaf passes through the **same number of black nodes**: its **black-height**.

```
          13B
        /     \
      8R       17R
     /  \     /   \
   1B   11B 15B   25B
     \           /
      6R       22R
```

Every root-to-NIL path here has 3 black nodes, counting the root and the NIL itself (for example 13, 8, 1, 6, NIL passes 13, 1 and NIL), and no red node has a red child.

> [!analogy] Real-world analogy: checkpoints on routes out of a city
> Every route from a city's centre to its edge must pass the same number of official checkpoints. Between checkpoints a route may have at most one optional rest stop, never two in a row. However the roads are laid out, no route to the edge can have more than about twice as many stops as the route with the fewest.
>
> **How it maps:** routes are root-to-NIL paths, checkpoints are black nodes, and the equal checkpoint count is the black-height rule. Rest stops are red nodes, and "never two in a row" is the no-red-red rule. Together they cap how many more nodes one path can have than another.
>
> **Where it stops:** roads do not change. A red-black tree must recolour and rotate after every insert or delete to keep both rules true, and the rules bound only the *ratio* of path lengths; the logarithmic height comes from also counting how many nodes the checkpoints force into the tree.

### Why the height is O(log n)

Two facts combine:

- **Paths are within a factor of two.** No two reds are adjacent, so at least half the nodes on any root-to-NIL path are black. Every path has the same number of black nodes, so the longest root-to-NIL path is at most twice as long as the shortest.
- **Black nodes force lots of nodes.** Ignoring the red nodes, every path down from the root meets the same number of black nodes, so the black nodes alone behave like a perfectly balanced tree. If every path from a node down to NIL meets b black nodes (counting the NIL but not the node itself), that node's subtree must contain at least 2 to the power b, minus 1, real nodes; this can be proved by induction.

Put together, the black levels can only be about log₂ n deep, and the full height at most twice that:

```formula reference
h ≤ 2 log_2(n + 1)
where
h: the height of the tree, in edges
n: the number of keys (real, non-NIL nodes) in the tree
log_2(n + 1): the base-2 logarithm of n + 1: how many times you can halve n + 1 before reaching 1
≤: is at most
In words: a red-black tree is never more than about twice as tall as the shortest possible binary tree with the same number of keys.
```

For a million keys the bound is a height of about 40 edges, against 19 for a complete tree and at most 27 for an AVL tree. That looser bound is the price of red-black trees' cheaper repairs. Actual height depends on the implementation and update history.

Java TreeMap uses this red-black structure. Its documented logarithmic get, put and remove guarantees hold for insertion orders such as ascending IDs; ordered arrivals do not turn it into the unbalanced chain studied earlier.

## Key takeaways
- NIL child positions count as black for the path invariant.
- No consecutive red nodes and equal black-height imply logarithmic height.
- Red-black height is bounded by about twice the best possible; AVL is stricter but may rotate more on deletes.

## Further reading
- [Red–black tree — Wikipedia](https://en.wikipedia.org/wiki/Red%E2%80%93black_tree)
- [Balanced Search Trees — Algorithms, 4th ed. (Sedgewick & Wayne)](https://algs4.cs.princeton.edu/33balanced/)
- [TreeMap (Java SE 25) — Oracle](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/TreeMap.html)
