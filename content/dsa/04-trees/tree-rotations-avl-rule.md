---
id: tree-rotations-avl-rule
title: Rotations and the AVL balance rule
level: intermediate
minutes: 4
sourceLesson: tree-balanced
summary: A rotation preserves in-order order while changing local parent links.
---

A plain BST is only as good as its insertion order. Feed it sorted keys and it becomes a linked list. AVL and red-black trees maintain balancing invariants after updates, using local rotations and metadata changes. Other balancing schemes can rebuild subtrees instead.

The result is a hard guarantee: for n keys, the height stays O(log n) (growing only with the logarithm of n, a small multiple of about 20 for a million keys) no matter what order keys arrive in, so search, insert and delete are **O(log n) worst case**. The two classic designs are **AVL trees** (1962) and **red-black trees** (1972 as symmetric B-trees; the red/black formulation dates from 1978). They differ in how strict their invariant is.

## Rotations

Here n is the stored key count; a rotation changes only a fixed number of links.


A rotation changes the shape of a small part of the tree while **preserving the in-order sequence**, so the BST property still holds.

```
      y                 x
     / \    right      / \
    x   C   ---->     A   y
   / \      <----        / \
  A   B     left        B   C
```

Here A, B and C are whole subtrees. In both shapes the in-order sequence is A, x, B, y, C. A right rotation at y lifts x up one level and pushes y down; subtree **B changes parent** from x to y. A left rotation is the mirror image.

A rotation updates a constant number of links and metadata fields and does no searching, so it is **O(1)**: a fixed amount of work, however big the tree. AVL and red-black trees use rotations plus bookkeeping (heights for AVL, colours for red-black).

```python
def rotate_right(y):
    x = y.left
    # Transfer the middle subtree
    # before lifting.
    y.left = x.right           # move B
    x.right = y
    # Fix the lowered node before its
    # new parent.
    fix(y)                     # update
    fix(x)                     # heights
    return x                   # new root
```

## AVL trees

Named after Adelson-Velsky and Landis, the AVL tree was the first self-balancing BST.

**Invariant:** at every node, the heights of the left and right subtrees differ by at most 1. The difference is the node's **balance factor**:

```formula
b(x) = h(x_L) − h(x_R)
b(x) ∈ {−1, 0, +1}
b(30) = 1 − (−1) = 2
where
b(x): the balance factor of node x; positive means left-heavy, negative means right-heavy
x: any node in the tree
h(x_L): the height of x's left subtree, in edges; −1 if the subtree is empty
h(x_R): the height of x's right subtree, in edges; −1 if the subtree is empty
∈: "is one of": the value must be in the set that follows
{ }: a set of allowed values
In words: a node's balance factor is its left subtree's height minus its right subtree's height, and an AVL tree requires it to be −1, 0 or +1 at every node.
```

The third line is node 30 in the "insert 30, 10, 20" example in the later AVL insertion unit: its left child 10 has a child of its own and 30 has no right child, so the heights are 1 and −1 and the balance factor is 2, which breaks the invariant. The insertion unit's `bf(n)` computes exactly this.

## Key takeaways
- A rotation preserves in-order order while changing local parent links.
- The middle subtree changes parent during a rotation.
- AVL balance factors compare left and right subtree heights.

## Further reading
- [AVL tree — Wikipedia](https://en.wikipedia.org/wiki/AVL_tree)
- [AVL tree visualisation — USF](https://www.cs.usfca.edu/~galles/visualization/AVLtree.html)
