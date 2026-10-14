---
id: tree-lca-single-query
title: Lowest common ancestors in ordered and general trees
level: advanced
minutes: 4
sourceLesson: tree-problems
summary: A BST query follows the side containing both keys until they split.
---

Tree problems look endlessly varied, but nearly all of them use one of a few patterns. Learn the patterns and most "new" problems become variations.

1. **Post-order combine.** Each call returns a summary of its subtree (height, sum, "found it?"), and the parent combines its children's summaries. Often a second value, the global best, is tracked on the side.
2. **Pre-order with state passed down.** Each call receives information from above (a running sum, a valid range, a depth) and passes an updated version to its children.
3. **Level-order** when the question mentions levels, widths or nearest anything.

This lesson works through the classics. Assume finite acyclic binary trees without shared nodes or concurrent mutation. These recursive examples are limited by Python call depth. Time bounds use unit-cost arithmetic; hashing-based bounds are expected. Throughout, n is the number of nodes and h is the tree's height in edges. Working recursion depth is O(h + 1), but dictionaries, serialized text and returned trees can require additional storage.

## Lowest common ancestor

The **lowest common ancestor** (LCA) of nodes p and q is the deepest node that has both as descendants (a node counts as its own descendant). It underlies "how are these two related?" questions: the nearest shared directory of two files, merge bases of Git commits (a DAG can have several incomparable best common ancestors, unlike a rooted tree), or the distance between two nodes. The path from p to q climbs from p up to their LCA, then goes down to q, so:

```formula
d(p, q) = D(p) + D(q) − 2D(a)
d(3, 5) = 3 + 3 − 2 × 2 = 2
where
p, q: the two nodes being compared
a: their lowest common ancestor
D(x): the depth of node x: its number of edges below the root
d(p, q): the distance between p and q: the number of edges on the path joining them
In words: climb from p up to the common ancestor, then down to q; each leg is a difference in depths, and together they give depth(p) + depth(q) minus twice the ancestor's depth.
```

The example line uses nodes 3 and 5 in the BST drawn below: both have depth 3 and their LCA, 4, has depth 2, so they are 2 edges apart (3–4–5).

### In a BST: follow the split

```
          6
        /   \
       2     8
      / \   / \
     0   4 7   9
        / \
       3   5
```

If p and q are both smaller than the current node, the LCA is on the left; both larger, on the right. Otherwise they **split** here (or one of them *is* this node), so this node is the LCA.

```python
def lca_bst(root, p, q):
    node = root
    while node:
        if p < node.val and q < node.val:
            node = node.left
        elif p > node.val and q > node.val:
            node = node.right
        else:
            return node    # split point
```

Assume unique ordered keys and that both queried keys exist in this tree. The function does not verify membership.

`lca_bst(root, 3, 5)` is 4, `lca_bst(root, 2, 8)` is 6 and `lca_bst(root, 0, 5)` is 2. This is O(h) time for a tree of height h, with O(1) space (a fixed amount, just the current node).

### In any binary tree: post-order

Without ordering, ask each subtree "did you find p or q?":

```python
def lca(node, p, q):
    # p and q are node objects
    if (node is None or node is p or
            node is q):
        return node
    left = lca(node.left, p, q)
    right = lca(node.right, p, q)
    if left and right:
        return node        # p, q split
    # Carry a find upward if only one
    # side found.
    return left or right
```

If both sides report a find, this node is where the paths diverge. If only one does, pass its result up. When p is an ancestor of q, the search returns p as soon as it reaches it without looking below, which is correct because p is then the LCA. (This version assumes both nodes are in the tree; if either might be missing, count the finds explicitly.)

## Key takeaways
- A BST query follows the side containing both keys until they split.
- A general tree combines findings from its two children.
- The simple algorithms assume both requested nodes belong to the tree.

## Further reading
- [Lowest common ancestor — Wikipedia](https://en.wikipedia.org/wiki/Lowest_common_ancestor)
