---
id: tree-basics
title: Tree basics
level: basic
minutes: 10
summary: What a tree is, the vocabulary (root, leaf, height, depth), binary trees, how they are stored in memory, and the difference between full, complete, perfect and balanced.
---

Arrays and linked lists are **linear**: every element has at most one successor. A **tree** lets an element have several successors, which is exactly the shape of a lot of real data: a file system, the HTML DOM, an organisation chart, a parsed expression, a JSON document.

Trees also matter for speed. A sorted array lets you search in O(log n) but inserts cost O(n). A balanced binary search tree gives O(log n) search and insertion under constant-cost key comparisons: its height is logarithmic, and those operations follow a root-to-leaf path. An arbitrary well-shaped tree does not provide ordered search.

## What makes something a tree

A tree is a set of **nodes** joined by **edges**, with one special node, the **root**, such that:

- every node except the root has exactly one **parent**;
- following parents from any node always leads back to the root;
- there are no cycles.

Equivalently (in graph terms) a tree is a connected undirected graph with no cycles, with a root chosen for the rooted representation. A nonempty tree with n nodes always has exactly **n − 1 edges**: one edge per node, except the root.

```
            A          <- root (depth 0)
          / | \
         B  C  D       <- depth 1
        / \     \
       E   F     G     <- depth 2
           |
           H           <- depth 3
```

## Vocabulary

| Term | Meaning (in the tree above) |
|---|---|
| Child / parent | B is a child of A; A is B's parent |
| Siblings | B, C and D share a parent |
| Leaf | A node with no children: E, H, C, G |
| Internal node | Has at least one child: A, B, F, D |
| Subtree | A node plus all its descendants |
| Ancestor | A, B and F are ancestors of H |
| Degree | Number of children (A has 3) |

### Depth versus height

These two are easy to mix up because they both count edges, but they look in opposite directions.

- The **depth** of a node is the number of edges from the **root down to it**. The root has depth 0; H has depth 3.
- The **height** of a node is the number of edges on the **longest path down to a leaf**. Leaves have height 0; B has height 2; A has height 3.
- The **height of the tree** is the height of its root, which equals the maximum depth of any node.

> [!warning] Conventions vary
> Some books count nodes rather than edges, so a single node has height 1 instead of 0. This module counts **edges**: a one-node tree has height 0 and an empty tree has height −1. Always check which convention a problem uses before you answer "what is the height?".

For a finite acyclic binary tree with no shared children, computing height is the canonical recursive tree function (O(n) time, O(h + 1) recursive frames, subject to the runtime recursion limit): the height of a node is one more than the taller of its children.

```python
def height(node):
    if node is None:
        return -1          # empty tree
    return 1 + max(height(node.left),
                   height(node.right))
```

## Binary trees

A **binary tree** is a tree where every node has at most two children, called **left** and **right**. The order matters: a node with only a left child is a different tree from one with only a right child.

Binary trees are the workhorse of this module. Binary search trees, AVL trees, red-black trees and binary heaps have binary shape. Heaps can also have higher arity, and expression trees can have unary or many-operand nodes.

```python
class Node:
    def __init__(self, val, left=None,
                 right=None):
        self.val = val
        self.left = left
        self.right = right

#      1
#     / \
#    2   3
#   /
#  4
root = Node(1, Node(2, Node(4)), Node(3))
```

Two useful counting facts:

- A nonempty binary tree with n nodes has **n + 1 empty (None) child slots**: there are 2n slots and n − 1 of them are used by edges.
- A binary tree of height h has at most **2^(h+1) − 1 nodes** (level d holds at most 2^d). Turned round, a nonempty binary tree with n nodes has height at least **⌊log₂ n⌋**. That lower bound is why "O(log n)" keeps appearing.

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

- **Full** (or *proper*): every node has **0 or 2 children**, never exactly one. A full binary tree with i internal nodes has exactly i + 1 leaves.
- **Complete**: every level is completely filled **except possibly the last**, and the last level is filled **from left to right** with no gaps. This is the shape a binary heap always has.
- **Perfect**: every internal node has two children and **all leaves are at the same depth**. A perfect tree of height h has exactly 2^(h+1) − 1 nodes: 1, 3, 7, 15, 31...
- **Balanced** (height-balanced): for every node, the heights of its left and right subtrees differ by **at most 1**. More loosely, people say a tree is balanced when its height is O(log n).

Every perfect tree is both full and complete, but the other combinations are independent. In the picture, the "Full" tree is full but **not complete**: its last level is filled on the right with a gap on the left. The "Complete" tree is complete but **not full**: the right child of the root has only one child.

> [!tip] Why shape matters
> Ordered searches and single-key updates in a balanced BST cost O(height); traversing all nodes takes O(n). A complete tree with a million nodes has height 19; other balancing rules permit larger logarithmic heights. A degenerate one, where each node has a single child, has height 999,999 and is just a slow linked list.

## Representing trees in memory

### Linked nodes

The usual choice: each node is an object with a value and pointers to its children (and sometimes its parent). It handles any shape. Relinking a known subtree can change only a few pointers, but locating it, maintaining metadata or balancing, and reclaiming removed nodes can require additional work.

The cost is memory and cache behaviour. Object size depends on the interpreter version, build and class layout. Separately allocated nodes can reduce locality, but do not imply a cache miss on every visit.

> [!note] Evidence gap
> The previous universal 56-byte node size and one-cache-miss-per-node claim are omitted because no pinned interpreter measurement or hardware trace was supplied.

### Arrays (implicit trees)

A **complete** binary tree can be stored in a plain array with no pointers at all. Put the nodes in level order; then, with 0-based indices:

```
 index:  0  1  2  3  4  5
 value: [A, B, C, D, E, F]

        A(0)
       /    \
     B(1)    C(2)
    /  \     /
  D(3) E(4) F(5)

 left(i)   = 2*i + 1
 right(i)  = 2*i + 2
 parent(i) = (i - 1) // 2  # i > 0
```

This is compact and cache-friendly, and it is exactly how binary heaps are implemented (lesson 5). It wastes space badly for sparse, unbalanced trees, since a missing node still needs a slot: a degenerate right-leaning chain of height h needs an array of 2^(h+1) − 1 slots.

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

## Where trees appear

- **File systems**: a directory hierarchy is often modelled as a tree; empty directories are also leaves, and hard links or followed symbolic links need extra care.
- **Compilers**: source code is parsed into an *abstract syntax tree*; `(2 + 3) * 4` becomes a `*` node with children `+` and `4`.
- **Databases**: many indexes use B-trees, a many-children generalisation of search trees (covered in the System Design databases module).
- **Ordered maps**: Java's TreeMap uses a red-black tree; common std::map implementations do too, but the C++ interface does not require that representation (lesson 4).
- **Schedulers and priority queues**: heaps (lesson 5).
- **Autocomplete and routing tables**: tries (lesson 6).

## Key takeaways
- A tree is a connected, acyclic structure with a root; a nonempty tree with n nodes has n − 1 edges.
- Depth counts edges down from the root; height counts edges down to the deepest leaf. Check whether a problem counts edges or nodes.
- Full: 0 or 2 children. Complete: levels filled left to right. Perfect: every level full. Balanced: subtree heights differ by at most 1 everywhere.
- A nonempty binary tree has height at least ⌊log₂ n⌋. BST search follows a path; a full traversal still takes O(n).
- Linked nodes handle any shape; arrays with `2i+1` / `2i+2` suit complete trees such as heaps.

## Further reading
- [Tree (data structure) — Wikipedia](https://en.wikipedia.org/wiki/Tree_(data_structure))
- [Binary tree — Wikipedia](https://en.wikipedia.org/wiki/Binary_tree)
- [Binary expression tree — Wikipedia](https://en.wikipedia.org/wiki/Binary_expression_tree)
