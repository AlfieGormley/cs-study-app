---
id: tree-shape-definitions
title: Full, complete, perfect and balanced
level: basic
minutes: 4
sourceLesson: tree-basics
summary: Full describes child counts; complete describes filled positions.
---

Use the rooted-tree vocabulary from the earlier unit. The linked examples below assume a finite acyclic tree without shared child nodes. Count height and depth in edges, not nodes. A path ends at a leaf only when that node has no children. When an example uses n, it means the number of stored nodes.

## Shapes: full, complete, perfect, balanced

These four words get confused constantly, and interviewers love them.

```
 Full        Complete    Perfect
   o            o           o
  / \          / \        /   \
 o   o        o   o      o     o
    / \      / \  /     / \   / \
   o   o    o  o o     o   o o   o
```

- **Full tree** (or *proper*): every node has **0 or 2 children**, never exactly one. A full binary tree always has one more leaf than internal node (see the formula below).
- **Complete tree**: every level is completely filled **except possibly the last**, and the last level is filled **from left to right** with no gaps. This is the shape a binary heap always has. (Some authors use "complete" for what this module calls perfect, so check the definition a source uses.)
- **Perfect tree**: every internal node has two children and **all leaves are at the same depth**. Every level is full, so it holds the maximum number of nodes for its height: 1, 3, 7, 15, 31... nodes for heights 0 to 4.
- **Height-balanced tree**: for every node, the heights of its left and right subtrees differ by **at most 1**. More loosely, people say a tree is balanced when its height is O(log n), where n counts nodes.

A full tree always has **exactly one more leaf than internal nodes**. Count its edges two ways: each internal node owns exactly two child edges, and any tree has one edge fewer than nodes. Those two counts only agree when the leaves outnumber the internal nodes by one:

```formula reference
L_f = i + 1
where
i: the number of internal nodes (nodes with children); each has exactly 2 children in a full tree
L_f: the number of leaves in the full binary tree
In words: every full binary tree has one more leaf than it has internal nodes, so its total node count is always odd.
```

The "Full" tree in the picture has two internal nodes and 3 leaves. A knockout tournament is the same shape: 16 players (leaves) need exactly 15 matches (internal nodes), however the draw is arranged.

The balance rule is a check you make at **every** node, not just the root. Using this module's edge-counted heights, an empty subtree has height −1. So a node whose left child has a child of its own (left height 1) but whose right side is empty (height −1) is out of balance by 2, and the tree is not height-balanced even if every other node is fine.

Every perfect tree is both full and complete, but the other combinations are independent. In the picture, the "Full" tree is full but **not complete**: its last level is filled on the right with a gap on the left. The "Complete" tree is complete but **not full**: the right child of the root has only one child.

> [!analogy] Real-world analogy: seating an audience row by row
> An usher fills a theatre from the front row, left to right, and starts a new row only when the current one is full. At any moment every row is full except the one being filled, and that row has no gaps on its left.
>
> **How it maps:** rows are levels and seats are node positions. The usher's rule produces exactly a complete tree. A completely sold-out theatre with every row full corresponds to a perfect tree.
>
> **Where it stops:** in a tree, each level has twice as many seats as the one above, and every seat must sit under an occupied seat in the row before. The analogy also says nothing about "full", which is a rule about each node's child count, not about filling order.

> [!tip] Why shape matters
> Ordered searches and single-key updates in a balanced BST cost time proportional to the height; traversing all n nodes takes O(n). A complete tree with a million nodes has height 19; other balancing rules permit larger logarithmic heights. A degenerate one, where each node has a single child, has height 999,999 and is just a slow linked list.

## Key takeaways
- Full describes child counts; complete describes filled positions.
- Perfect requires every level to be full.
- Height balance must hold at every node, not just the root.

## Further reading
- [Binary tree — Wikipedia](https://en.wikipedia.org/wiki/Binary_tree)
