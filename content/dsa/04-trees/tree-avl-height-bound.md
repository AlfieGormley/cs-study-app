---
id: tree-avl-height-bound
title: Minimum AVL nodes and the height bound
level: intermediate
minutes: 4
sourceLesson: tree-balanced
summary: The sparsest allowed children differ in height by one.
---

Start with the distinct-key BST ordering from the previous units. A rotation must keep the same sorted in-order sequence while changing local links. Here n counts stored keys and h measures real-node height in edges; empty subtrees have height minus one unless a NIL-path convention is explicitly given. Height bounds assume constant-cost key comparisons, rather than measuring application latency.

### Why that guarantees O(log n)

Here n counts stored keys and h is tree height in edges. The empty-tree base case is used only as a recurrence boundary.


Ask: what is the fewest nodes an AVL tree of height h can have? The sparsest one has one subtree one edge shorter and the other two edges shorter (the most lopsided the invariant allows), each as sparse as possible, plus the root:

```formula
N(h) = N(h − 1) + N(h − 2) + 1
N(−1) = 0
N(0) = 1
N(1) = 2
N(2) = 2 + 1 + 1 = 4
N(3) = 4 + 2 + 1 = 7
N(4) = 7 + 4 + 1 = 12
N(5) = 12 + 7 + 1 = 20
N(6) = 20 + 12 + 1 = 33
N(7) = 33 + 20 + 1 = 54
where
h: the height of the AVL tree, in edges
N(h): the smallest number of nodes an AVL tree of height h can have
In words: the sparsest AVL tree of height h is a root with a sparsest subtree of height h − 1 on one side and of height h − 2 on the other.
```

Those counts are each one less than a Fibonacci number, so they grow exponentially with h, and turning that round gives the height limit:

```formula
N(h) = F(h + 3) − 1
N(h) ≈ φ^(h+3) / √(5)
h_max ≈ 1.44 log_2(n)
h_max ≈ 1.44 log_2(10^6) ≈ 28.7
N(0) = F(3) − 1 = 2 − 1 = 1
N(5) = F(8) − 1 = 21 − 1 = 20
where
N(h): the smallest number of nodes an AVL tree of height h can have (from the recurrence above)
h: the height of the tree, in edges
F(k): the k-th Fibonacci number, with F(1) = F(2) = 1 and each later one the sum of the two before (1, 1, 2, 3, 5, 8, …)
k: a position in the Fibonacci sequence
φ: phi, the golden ratio (1 + √(5)) / 2 ≈ 1.618, the factor by which Fibonacci numbers grow each step
φ^(h+3): h + 3 copies of φ multiplied together; dividing by √(5) (about 2.236) gives roughly 1.89 × 1.618^h
h_max: the greatest height an AVL tree with n nodes can have
n: the number of nodes (keys) in the tree
log_2(n): the base-2 logarithm of n: the power you raise 2 to in order to get n; log_2(10^6) ≈ 19.93
√(5): the square root of 5, about 2.236
≈: approximately equal to
In words: because the fewest nodes for height h grows like 1.618^h, an AVL tree has a leading worst-case height coefficient about 1.44 times that of the shortest possible binary tree.
```

The last two lines check the Fibonacci form against the counts above. The logarithmic coefficient is a leading approximation for large node counts; exact finite heights require the recurrence. For a million keys:


```formula
N(27) = 832039 ≤ n
N(28) = 1346268 > n
h_max = 27
h_complete = ⌊log_2(n)⌋ = 19
where
N(h): minimum AVL node count at edge-counted height h
h: tree height in edges; empty trees have height minus one
n: the number of stored keys, here 1,000,000
h_max: largest allowed AVL height at this node count, in edges
h_complete: height of a complete binary tree at this node count, in edges
log_2(x): base-2 logarithm of positive x
⌊ ⌋: floor, rounding down to the next integer
≤: less than or equal to
In words: Height twenty-seven fits the available keys, but height twenty-eight requires too many. A complete shape uses only nineteen edges.
```

## Key takeaways
- The sparsest allowed children differ in height by one.
- Minimum node counts obey a Fibonacci-related recurrence.
- Use exact counts when deciding a finite maximum height.

## Further reading
- [AVL tree — Wikipedia](https://en.wikipedia.org/wiki/AVL_tree)
- [AVL tree visualisation — USF](https://www.cs.usfca.edu/~galles/visualization/AVLtree.html)
