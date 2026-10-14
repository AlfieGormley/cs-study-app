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
- **Complete tree**: every level is completely filled **except possibly the last**, and the last level is filled **from left to right** with no gaps. This is the shape a binary heap always has.
- **Perfect tree**: every internal node has two children and **all leaves are at the same depth**. Every level is full, so it holds exactly the maximum node count from the formula above: 1, 3, 7, 15, 31... nodes for heights 0 to 4.
- **Height-balanced tree**: for every node, the heights of its left and right subtrees differ by **at most 1**. More loosely, people say a tree is balanced when its height is O(log n), where n counts nodes.

Two of these definitions are easier to apply as formulas. For a full tree, counting edges two ways gives the leaf count:

```formula
E = 2i
E = n − 1
n = 2i + 1
L_f = n − i = i + 1
L_f = 3 + 1 = 4
where
i: the number of internal nodes (nodes with children); each has exactly 2 children in a full tree
E: the number of edges; each internal node contributes 2
n: the total number of nodes
L_f: the number of leaves in the full binary tree
In words: in a full binary tree, each internal node owns two edges and a tree has n − 1 edges, so there is always exactly one more leaf than internal node.
```

The "Full" tree in the picture has two internal nodes and 3 leaves. A full tree with 3 internal nodes has 4 leaves and 7 nodes; every full tree has an odd number of nodes.

The balance rule is a check you make at every node:

```formula
|h(x_L) − h(x_R)| ≤ 1
|1 − (−1)| = 2
where
x: any node of the tree
h(x_L): the height of x's left subtree, in edges; −1 if it is empty
h(x_R): the height of x's right subtree, in edges; −1 if it is empty
| |: absolute value: the size of the difference ignoring its sign, so |−2| = 2
≤: is at most
In words: at every node, the left and right subtrees may differ in height by at most one edge.
```

The second line is a node whose left child has a child of its own but whose right side is empty: heights 1 and −1 differ by 2, so that node is unbalanced.

Every perfect tree is both full and complete, but the other combinations are independent. In the picture, the "Full" tree is full but **not complete**: its last level is filled on the right with a gap on the left. The "Complete" tree is complete but **not full**: the right child of the root has only one child.

> [!tip] Why shape matters
> Ordered searches and single-key updates in a balanced BST cost time proportional to the height; traversing all n nodes takes O(n). A complete tree with a million nodes has height 19; other balancing rules permit larger logarithmic heights. A degenerate one, where each node has a single child, has height 999,999 and is just a slow linked list.

## Key takeaways
- Full describes child counts; complete describes filled positions.
- Perfect requires every level to be full.
- Height balance must hold at every node, not just the root.

## Further reading
- [Binary tree — Wikipedia](https://en.wikipedia.org/wiki/Binary_tree)
