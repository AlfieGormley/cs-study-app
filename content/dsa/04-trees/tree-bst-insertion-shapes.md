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
| Median first, recursively | Perfect-ish | 9 |

Inserting sorted keys into a plain BST produces a linked list with extra pointers: every insert walks the whole chain built so far. The first insert visits no existing nodes, the second visits 1, and so on:

```formula
V = 0 + 1 + 2 + … + (n − 1)
V = (n(n − 1)) / 2
V = 1000 × 999 / 2 = 499500
V ≈ 10^6 × 10^6 / 2 = 5 × 10^11
where
V: the total number of existing nodes visited while building the tree
n: the number of keys inserted, in ascending order; 1,000 in the third line, a million (10^6) in the fourth
…: "and so on": the count keeps rising by 1 each insert
10^6: ten to the power 6, one million
≈: approximately equal to (rounded)
In words: the k-th sorted insert walks past all k − 1 earlier keys, and adding those up gives about n²/2, half of n squared.
```

The total has tight quadratic growth:

```formula
V = Θ(n^2)
where
V: existing-node visits across all sorted insertions
n: the number of distinct keys inserted
Θ(f(n)): tight asymptotic growth, bounded above and below by positive constant multiples of f(n) for sufficiently large n
f(n): the comparison growth function, here the square of the key count
In words: doubling a sufficiently large sorted batch multiplies these visits by about four; this is a tight bound, rather than only an upper bound.
```

Ten times as many keys costs about a hundred times as much: 1,000 sorted keys cost about half a million node visits, and a million keys about 5 × 10¹¹.

Random insertion order is much kinder. For distinct keys inserted in a uniformly random permutation, the average depth of a stored key grows only logarithmically:

```formula
D ≈ 2 ln(n)
D ≈ 2 ln(2) log_2(n)
D ≈ 1.39 log_2(n)
D ≈ 2 ln(1000) ≈ 2 × 6.91 ≈ 13.8
where
D: the expected (average) depth, in edges, of a uniformly chosen key in a BST built from a random insertion order; this is the leading term only
n: the number of distinct keys in the tree
ln(n): the natural logarithm of n: the power you raise e ≈ 2.718 to in order to get n; ln(1000) ≈ 6.91
ln(2): the natural logarithm of 2, about 0.693, which converts natural logs into base-2 logs
log_2(n): the base-2 logarithm of n: the power you raise 2 to in order to get n; log_2(1000) ≈ 9.97
e: Euler's number, about 2.718, the base of the natural logarithm
≈: approximately equal to
In words: for large n, a randomly built BST is on average only about 39 % deeper than the best possible shape, because 2 × ln(n) is about 1.39 times log_2(n).
```

For 1,000 random keys that is an average depth of about 14 by the leading term. Lower-order terms matter for finite sizes: the exact expected average is about 11, against an average depth of about 8 in the best (complete) shape, whose height is 9. Expected height is also O(log n); this is an expectation, not a bound on every insertion order.

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
