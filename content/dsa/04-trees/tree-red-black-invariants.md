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

### Why the height is O(log n)

For this proof, count a node's black-height without the node itself: the number of black nodes on a path below it down to NIL, including the NIL (so a NIL has black-height 0). This differs from the inclusive count used in the preceding diagram. Two facts combine:

- No two reds are adjacent, so at least half the nodes on any path below the root are black: the height is at most twice the root's black-height.
- A subtree whose root has black-height b holds a number of real (non-NIL) nodes that grows exponentially with its black-height (the first line below), which you can prove by mathematical induction: it holds for a NIL, and each child's black-height is at least the parent's black-height minus one.

```formula
n_x ≥ 2^{bh(x)} − 1
h ≤ 2 bh(r)
n ≥ 2^{h/2} − 1
h ≤ 2 log_2(n + 1)
h ≤ 2 log_2(10^6 + 1) ≈ 39.9
where
x: any node in the tree
bh(x): the black-height of x: black nodes on any path from just below x down to a NIL leaf, counting the NIL but not x
n_x: the number of real (non-NIL) nodes in the subtree rooted at x
r: the root of the tree
h: the height of the tree, in edges, measured from the root down to the deepest NIL leaf (the height counting only real nodes is one less, so it obeys the same bound)
n: the number of keys (real nodes) in the whole tree
2^{bh(x)}: 2 multiplied by itself bh(x) times
log_2(n + 1): the base-2 logarithm of n + 1: the power you raise 2 to in order to get n + 1
≥: is at least
≤: is at most
≈: approximately equal to
In words: a red-black tree is at most twice as tall as its black-height, and the black-height can only be about log_2(n), so the height is at most 2 × log_2(n + 1).
```

The third line comes from applying the first line at the root and substituting the second; solving it for h gives the fourth. For a million keys the bound is about 40; actual height depends on the implementation and update history.

Java TreeMap uses this red-black structure. Its documented logarithmic get, put and remove guarantees hold for insertion orders such as ascending IDs; ordered arrivals do not turn it into the unbalanced chain studied earlier.

## Key takeaways
- NIL child positions count as black for the path invariant.
- No consecutive red nodes and equal black-height imply logarithmic height.
- Distinguish inclusive diagram counts from the proof’s exclusive black-height convention.

## Further reading
- [Red–black tree — Wikipedia](https://en.wikipedia.org/wiki/Red%E2%80%93black_tree)
- [Balanced Search Trees — Algorithms, 4th ed. (Sedgewick & Wayne)](https://algs4.cs.princeton.edu/33balanced/)
- [TreeMap (Java SE 25) — Oracle](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/TreeMap.html)
