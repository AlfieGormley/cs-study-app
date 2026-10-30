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

The cost is memory and cache behaviour. Every node carries its child pointers and, in languages like Python, an object header as well, so a tree of small values can use several times more memory than the values themselves. For example, on 64-bit CPython 3.14 each object of a plain node class with a value and two child fields takes about 100 bytes, not counting the value it refers to; exact sizes depend on the language, version and class layout. Nodes allocated separately can end up scattered in memory, which can make traversals slower than walking an array, although it does not mean a cache miss on every visit.

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

```formula essential
i_left = 2i + 1
i_right = 2i + 2
i_parent = ⌊(i − 1) / 2⌋
where
i: the index (0-based array position) of a node; i_parent applies only when i > 0, since the root at index 0 has no parent
i_left: the index of that node's left child
i_right: the index of that node's right child
i_parent: the index of that node's parent
⌊ ⌋: floor: round down to a whole number, so ⌊1.5⌋ = 1
In words: the children of slot i sit at 2i + 1 and 2i + 2, and you get back to the parent by subtracting 1, halving and rounding down.
```

So B at index 1 has its left child D at index 3, and F at index 5 has its parent C at index 2. A child index that falls past the end of the array means that child is missing. In Python the same arithmetic is `2*i + 1`, `2*i + 2` and `(i - 1) // 2`, where `//` divides and rounds down.

This is compact and cache-friendly, and it is exactly how binary heaps are implemented (the binary heap units). Because a complete tree has no gaps, every slot from 0 to n − 1 is used and nothing else is needed.

It wastes space badly for sparse, unbalanced trees, since a missing node still needs a slot. Follow a chain that only ever goes right: each step to a right child roughly doubles the index, so a 4-node chain sits at indices 0, 2, 6 and 14 and needs 15 slots to store 4 values. Every node added to the chain roughly doubles the array again, so the implicit layout is a poor fit for any shape that is not close to complete.

> [!analogy] Real-world analogy: numbered plots on a planned estate
> Imagine an estate where plots are numbered by a fixed rule: plot 0 is at the entrance, the two plots that branch off it are 1 and 2, the two off plot 1 are 3 and 4, and so on. To find a neighbour you never need directions; you work the number out.
>
> **How it maps:** a plot number is an array index, the numbering rule is the child and parent arithmetic, and needing no directions is having no pointers. A plot with no house still keeps its number, just as a missing child still reserves an array slot.
>
> **Where it stops:** the arithmetic only stays cheap if the plots are filled in order with no gaps. Real estates, like linked trees, can grow anywhere; an implicit tree cannot add a node in the middle without moving others.

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
