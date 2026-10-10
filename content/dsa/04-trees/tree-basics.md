---
id: tree-basics
title: Tree basics
level: basic
minutes: 10
summary: What a tree is, the vocabulary (root, leaf, height, depth), binary trees, how they are stored in memory, and the difference between full, complete, perfect and balanced.
---

Arrays and linked lists are **linear**: every element has at most one successor. A **tree** lets an element have several successors, which is exactly the shape of a lot of real data: a file system, the HTML DOM, an organisation chart, a parsed expression, a JSON document.

Trees also matter for speed. In this module, n is the number of items (keys or nodes) stored, and O(…) is Big O notation: it describes how the work grows as n grows. O(n) means the work grows in proportion to n; O(log n) means it grows with the base-2 logarithm of n, roughly the number of times you can halve n before reaching 1 (about 20 for a million). O(1) means a fixed amount of work however large n is.

A sorted array lets you search in O(log n) but inserts cost O(n), because every later item must shift along. A balanced binary search tree gives O(log n) search and insertion under constant-cost key comparisons: its height is logarithmic, and those operations follow a root-to-leaf path. An arbitrary well-shaped tree does not provide ordered search.

## What makes something a tree

A tree is a set of **nodes** joined by **edges**, with one special node, the **root**, such that:

- every node except the root has exactly one **parent**;
- following parents from any node always leads back to the root;
- there are no cycles.

Equivalently (in graph terms) a tree is a connected undirected graph with no cycles, with a root chosen for the rooted representation.

Because every node except the root has exactly one edge up to its parent, you can count the edges of any tree without looking at its shape:

```formula
E = n − 1
E = 8 − 1 = 7
where
n: the number of nodes in the tree, a whole number of at least 1; here the 8 nodes A to H drawn below
E: the number of edges (parent–child links) in the tree
In words: a nonempty tree always has exactly one edge fewer than it has nodes, because the root is the only node with no edge to a parent.
```

So the tree below, with 8 nodes, has **n − 1 = 7 edges**, and a tree of a million nodes has 999,999, whatever its shape. The rule needs a single connected tree; a collection of separate trees (a forest) has fewer edges.

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

Height has a neat recursive definition: the height of a node is one more than the taller of its children's heights, and an empty subtree has height −1 so that a leaf comes out as 0.

```formula
h(x) = 1 + max(h(x_L), h(x_R))
h(∅) = −1
h(E) = 1 + max(−1, −1) = 0
h(F) = 1 + max(h(H), −1) = 1
h(B) = 1 + max(h(E), h(F)) = 2
where
h(x): the height of node x: the number of edges on the longest path from x down to a leaf
x: any node of the tree
x_L: the left child of x (or, in a tree with more children, any one child: take the max over all of them)
x_R: the right child of x
∅: an empty subtree (a missing child, None in Python)
max: the larger of the values listed
E, F, H, B: the nodes with those labels in the tree drawn above; E and H are leaves, so h(H) = 0
In words: a node's height is one more than its tallest child's height, and starting empty subtrees at −1 makes every leaf height 0.
```

That gives B height 2, matching the count by eye. For a finite acyclic binary tree with no shared children, this is the canonical recursive tree function. It visits each of the n nodes once, so it takes O(n) time, and it needs O(h + 1) recursive frames, where h is the tree's height (the +1 is the root's own frame, so even a one-node tree with h = 0 needs one). Deep trees can hit the runtime's recursion limit.

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

Two useful counting facts.

First, every node has two child slots, and every edge fills one of them, so the rest must be empty (None):

```formula
S = 2 × n − (n − 1) = n + 1
S = 2 × 4 − 3 = 5
where
S: the number of empty (None) child slots in a nonempty binary tree
n: the number of nodes; here 4, as in the four-node tree in the code above
In words: n nodes have 2n child slots between them, n − 1 of those hold edges, so n + 1 are empty.
```

In the four-node tree above, node 4 has two empty slots, node 3 has two and node 2 has one: 5 in total. This is why serialising a tree with a marker for every empty child writes n + 1 markers (lesson 7).

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

So height 3 fits at most 15 nodes, and a million nodes need height at least 19. That lower bound is why "O(log n)" keeps appearing: a well-shaped tree reaches any node in about log₂ n steps. Nothing stops a badly shaped tree being much taller: n nodes in a single chain have height n − 1.

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

- **Full** (or *proper*): every node has **0 or 2 children**, never exactly one. A full binary tree always has one more leaf than internal node (see the formula below).
- **Complete**: every level is completely filled **except possibly the last**, and the last level is filled **from left to right** with no gaps. This is the shape a binary heap always has.
- **Perfect**: every internal node has two children and **all leaves are at the same depth**. Every level is full, so it holds exactly the maximum node count from the formula above: 1, 3, 7, 15, 31... nodes for heights 0 to 4.
- **Balanced** (height-balanced): for every node, the heights of its left and right subtrees differ by **at most 1**. More loosely, people say a tree is balanced when its height is O(log n), for n nodes.

Two of these definitions are easier to apply as formulas. For a full tree, counting edges two ways gives the leaf count:

```formula
E = 2 × i
E = n − 1
n = 2 × i + 1
L_f = n − i = i + 1
L_f = 3 + 1 = 4
where
i: the number of internal nodes (nodes with children); each has exactly 2 children in a full tree
E: the number of edges; each internal node contributes 2
n: the total number of nodes
L_f: the number of leaves in the full binary tree
In words: in a full binary tree, each internal node owns two edges and a tree has n − 1 edges, so there is always exactly one more leaf than internal node.
```

The "Full" tree in the picture has i = 2 internal nodes and 3 leaves. A full tree with 3 internal nodes has 4 leaves and 7 nodes; every full tree has an odd number of nodes.

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

## Representing trees in memory

### Linked nodes

The usual choice: each node is an object with a value and pointers to its children (and sometimes its parent). It handles any shape. Relinking a known subtree can change only a few pointers, but locating it, maintaining metadata or balancing, and reclaiming removed nodes can require additional work.

The cost is memory and cache behaviour. Object size depends on the interpreter version, build and class layout. Separately allocated nodes can reduce locality, but do not imply a cache miss on every visit.

> [!note] Evidence gap
> The previous universal 56-byte node size and one-cache-miss-per-node claim are omitted because no pinned interpreter measurement or hardware trace was supplied.

### Arrays (implicit trees)

A **complete** binary tree can be stored in a plain array with no pointers at all. Put the nodes in level order (the root, then each level left to right), numbering slots from 0:

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
i_left = 2 × i + 1
i_right = 2 × i + 2
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

This is compact and cache-friendly, and it is exactly how binary heaps are implemented (lesson 5). It wastes space badly for sparse, unbalanced trees, since a missing node still needs a slot. Follow a chain that only ever goes right:

```formula
i_k = 2 × i_{k−1} + 2
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
- A binary tree of n nodes can be no shorter than the number of times n can be halved, rounded down (19 edges for a million nodes). BST search follows a path; a full traversal still takes O(n).
- Linked nodes handle any shape; arrays with children at `2*i + 1` and `2*i + 2` suit complete trees such as heaps.

## Further reading
- [Tree (data structure) — Wikipedia](https://en.wikipedia.org/wiki/Tree_(data_structure))
- [Binary tree — Wikipedia](https://en.wikipedia.org/wiki/Binary_tree)
- [Binary expression tree — Wikipedia](https://en.wikipedia.org/wiki/Binary_expression_tree)
