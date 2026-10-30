---
id: tree-bst-insertion-shapes
title: Insertion order, degeneration and rebuilding
level: intermediate
minutes: 5
sourceLesson: tree-bst
summary: Sorted insertion creates a chain in an unbalanced BST.
---

Earlier units established a strict BST ordering with distinct, mutually comparable keys: every left-subtree key is smaller and every right-subtree key larger. Use the Node with key, left and right fields introduced in the search unit. Here n counts keys and h measures tree height in edges. Comparisons have constant cost; recursive code remains limited by Python call depth.

## Degenerate trees

Search and single-key updates cost O(h + 1) for a tree of height h; full validation of n nodes costs O(n). With insertion only, order determines shape; deletions also change it.

| Input order | Shape | Height with 1,000 keys |
|---|---|---|
| Ascending | Right chain | 999 |
| Uniformly random permutation | Random shape | Expected O(log n); no fixed height |
| Median first, recursively | Shortest possible | 9 |

Inserting sorted keys into a plain BST produces a linked list with extra pointers. Each new key is larger than everything already stored, so it goes right at every node and walks the whole chain built so far: the first insert visits no existing nodes, the second visits 1, the third 2, and so on.

Adding those up gives about half the square of the number of keys, so the total work grows **quadratically**: ten times as many sorted keys costs about a hundred times as much. 1,000 sorted keys cost about half a million node visits; a million keys cost about 500 billion. Searches afterwards are no better: looking up a late key walks the chain like a linked-list scan.

Random insertion order is much kinder. For distinct keys inserted in a uniformly random permutation, the average depth of a stored key grows only logarithmically: for large trees it is about 1.39 times the depth of the best possible shape.

```formula reference
D ≈ 2 ln(n) ≈ 1.39 log_2(n)
where
D: the expected (average) depth, in edges, of a uniformly chosen key in a BST built from a random insertion order; this is the leading term only
n: the number of distinct keys in the tree
ln(n): the natural logarithm of n, about 0.693 times log_2(n)
log_2(n): the base-2 logarithm of n: how many times you can halve n before reaching 1
≈: approximately equal to
In words: for large trees, a randomly built BST is on average only about 39 % deeper than the best possible shape.
```

For 1,000 random keys the exact expected average depth is about 11, against about 8 in the best (complete) shape, whose height is 9. Expected height is also logarithmic, but this is an average over random orders, not a bound on every insertion order.

But real data is rarely random. Timestamps, auto-increment IDs and alphabetically sorted imports all arrive in order. For workloads requiring worst-case logarithmic access, use a **self-balancing** tree (AVL, red-black; the balanced-tree units), a B-tree (System Design, databases), a skip list, or a sorted sequence implementation. Python sortedcontainers uses a list of sorted lists; Redis can use a skip list plus dictionary or a compact encoding for sorted sets.

> [!tip] Building a balanced BST from sorted data
> If you have all the keys up front and sorted, pick the **middle** key as the root and recurse on each half. For a nonempty sorted set of distinct keys, passing index ranges rather than copying slices builds the shortest possible tree (height 3 for the ten keys above, 9 for 1,000 keys) in O(n) time, assuming constant-time node creation.

## Key takeaways
- Sorted insertion creates a chain in an unbalanced BST.
- Random insertion gives expected logarithmic depth, rather than a worst-case guarantee.
- A sorted batch can be built from midpoint index ranges without copying slices.

## Further reading
- [Binary Search Trees — Algorithms, 4th ed. (Sedgewick & Wayne)](https://algs4.cs.princeton.edu/32bst/)
- [Sorted Containers (Python) docs](https://grantjenks.com/docs/sortedcontainers/)
