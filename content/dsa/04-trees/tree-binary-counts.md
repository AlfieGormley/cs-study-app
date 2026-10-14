---
id: tree-binary-counts
title: Binary nodes and counting bounds
level: basic
minutes: 4
sourceLesson: tree-basics
summary: Left and right child positions are distinct, even with only one child.
---

Use the rooted-tree vocabulary from the earlier unit. The linked examples below assume a finite acyclic tree without shared child nodes. Count height and depth in edges, not nodes. A path ends at a leaf only when that node has no children. When an example uses n, it means the number of stored nodes.

## Binary trees

A **binary tree** is a tree where every node has at most two children, called **left** and **right**. The order matters: a node with only a left child is a different tree from one with only a right child.

Binary trees are the workhorse of this module. Binary search trees, AVL trees, red-black trees and binary heaps have binary shape. Other priority queue structures, such as d-ary heaps, allow higher arity, and expression trees can have unary or many-operand nodes.

Use the Node representation from the depth-and-height unit; the four-node example there also illustrates these child-slot counts.


Two useful counting facts.

First, every node has two child slots, and every edge fills one of them, so the rest must be empty (None):

```formula
S = 2n − (n − 1) = n + 1
S = 2 × 4 − 3 = 5
where
S: the number of empty (None) child slots in a nonempty binary tree
n: the number of nodes; here 4, as in the four-node Node sample from the depth-and-height unit
In words: n nodes have 2n child slots between them, n − 1 of those hold edges, so n + 1 are empty.
```

In that earlier four-node tree, node 4 has two empty slots, node 3 has two and node 2 has one: 5 in total. This is why serialising a tree with a marker for every empty child writes one more marker than nodes (the common-problem units).

Second, each level can hold at most twice as many nodes as the level above it, which caps how many nodes fit under a given height, and so how short a tree of n nodes can be:

```formula
N_max = 1 + 2 + 4 + … + 2^h
N_max = 2^(h+1) − 1
h ≥ ⌊log_2(n)⌋
N_max = 2^(3+1) − 1 = 15
h ≥ ⌊log_2(1000000)⌋ = ⌊19.93⌋ = 19
where
h: the height of the tree, in edges; level d (depth d) holds at most 2^d nodes, so levels 0 to h can hold 1, 2, 4, … nodes
N_max: the largest number of nodes a binary tree of height h can hold
n: the number of nodes actually in the tree (at least 1)
2^h: h copies of 2 multiplied together, so 2^3 = 2 × 2 × 2 = 8
…: "and so on": the doubling terms continue up to the last one shown
log_2(n): the base-2 logarithm of n: the power you must raise 2 to in order to get n, so log_2(8) = 3 and log_2(1000000) ≈ 19.93
⌊ ⌋: floor: round down to the whole number below, so ⌊19.93⌋ = 19
≥: is at least
In words: a binary tree of height h holds at most 2^(h+1) − 1 nodes, so a tree of n nodes must be at least ⌊log_2(n)⌋ edges tall.
```

So height 3 fits at most 15 nodes, and a million nodes need height at least 19. That lower bound is why "O(log n)" keeps appearing: a well-shaped tree reaches any node in about log₂ n steps. Nothing stops a badly shaped tree being much taller: n nodes in a single chain have height one less than its node count.

## Key takeaways
- Left and right child positions are distinct, even with only one child.
- Count empty slots by subtracting occupied edges from child positions.
- Doubling each level gives the shortest possible height for a node count.

## Further reading
- [Binary tree — Wikipedia](https://en.wikipedia.org/wiki/Binary_tree)
