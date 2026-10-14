---
id: tree-memory-layouts
title: Linked nodes, arrays and parent pointers
level: basic
minutes: 5
sourceLesson: tree-basics
summary: Arrays suit complete trees and calculate child positions without links.
---

Use the rooted-tree vocabulary from the earlier unit. The linked examples below assume a finite acyclic tree without shared child nodes. Count height and depth in edges, not nodes. A path ends at a leaf only when that node has no children. When an example uses n, it means the number of stored nodes.

## Representing trees in memory

### Linked nodes

The usual choice: each node is an object with a value and pointers to its children (and sometimes its parent). It handles any shape. Relinking a known subtree can change only a few pointers, but locating it, maintaining metadata or balancing, and reclaiming removed nodes can require additional work.

The cost is memory and cache behaviour. Object size depends on the interpreter version, build and class layout. Separately allocated nodes can reduce locality, but do not imply a cache miss on every visit.

> [!note] Evidence gap
> The previous universal 56-byte node size and one-cache-miss-per-node claim are omitted because no pinned interpreter measurement or hardware trace was supplied.

### Arrays (implicit trees)

A **complete binary tree** can be stored in a plain array with no pointers at all. Put the nodes in level order (the root, then each level left to right), numbering slots from 0:

```
 index:  0  1  2  3  4  5
 value: [A, B, C, D, E, F]

        A(0)
       /    \
     B(1)    C(2)
    /  \     /
  D(3) E(4) F(5)
```

Arithmetic on the index then replaces the pointers:

```formula
i_left = 2i + 1
i_right = 2i + 2
i_parent = ⌊(i − 1) / 2⌋
i_left = 2 × 1 + 1 = 3
i_parent = ⌊(5 − 1) / 2⌋ = 2
where
i: the index (0-based array position) of a node; i_parent applies only when i > 0, since the root at index 0 has no parent
i_left: the index of that node's left child
i_right: the index of that node's right child
i_parent: the index of that node's parent
⌊ ⌋: floor: round down to a whole number, so ⌊1.5⌋ = 1
In words: the children of slot i sit at 2i + 1 and 2i + 2, and you get back to the parent by subtracting 1, halving and rounding down.
```

So B at index 1 has its left child D at index 3, and F at index 5 has its parent C at index 2. A child index that falls past the end of the array means that child is missing. In Python the same arithmetic is `2*i + 1`, `2*i + 2` and `(i - 1) // 2`, where `//` divides and rounds down.

This is compact and cache-friendly, and it is exactly how binary heaps are implemented (the binary heap units). It wastes space badly for sparse, unbalanced trees, since a missing node still needs a slot. Follow a chain that only ever goes right:

```formula
i_k = 2i_{k−1} + 2
i_k = 2^(k+1) − 2
A = i_h + 1 = 2^(h+1) − 1
i_3 = 2^4 − 2 = 14
A = 14 + 1 = 15
where
k: the depth of a node in the chain: 0 for the root, 1 for its child, and so on
i_k: the array index of the chain node at depth k
i_{k−1}: the array index of the node one level above
i_h: the index of the deepest node in the chain
i_3: the index of the chain node at depth 3 (the fourth node)
h: the height of the chain, in edges
A: the length the array must have (one more than the last index used)
2^(k+1): k + 1 copies of 2 multiplied together
In words: each step right roughly doubles the index, so a right-only chain of height h needs an array of 2^(h+1) − 1 slots although it holds only h + 1 nodes.
```

A chain of 4 nodes (height 3) sits at indices 0, 2, 6 and 14, so it needs 15 slots to store 4 values.

### Trees with many children

For nodes with an unbounded number of children (a file system, the DOM), store a **list of children** per node. An older trick is **left-child, right-sibling**: each node keeps a pointer to its first child and one to its next sibling, which turns any tree into a binary tree.

```python
class TreeNode:
    def __init__(self, name):
        self.name = name
        self.children = []   # any number
```

### Parent pointers

Adding a `parent` field makes it easy to walk upwards (to find an in-order successor, or the path to the root) at the cost of one more pointer per node and more bookkeeping on every change. Red-black trees in the Linux kernel and in common C++ standard-library implementations keep parent pointers for this reason.

## Key takeaways
- Arrays suit complete trees and calculate child positions without links.
- Sparse chains waste exponentially many slots in the implicit layout.
- Linked nodes and child lists accommodate irregular shapes.

## Further reading
- [Tree (data structure) — Wikipedia](https://en.wikipedia.org/wiki/Tree_(data_structure))
- [Binary tree — Wikipedia](https://en.wikipedia.org/wiki/Binary_tree)
