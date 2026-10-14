---
id: tree-bst-successor-validation
title: Successors and global BST validation
level: intermediate
minutes: 3
sourceLesson: tree-bst
summary: A successor is the next key in sorted order, not necessarily a child.
---

Earlier units established a strict BST ordering with distinct, mutually comparable keys: every left-subtree key is smaller and every right-subtree key larger. Use the Node with key, left and right fields introduced in the search unit. Here n counts keys and h measures tree height in edges. Comparisons have constant cost; recursive code remains limited by Python call depth.

## In-order successor

"What is the next key after k?" comes up in ordered maps (`TreeMap.higherKey`), range scans and iterators. Two cases:

1. If the node has a **right subtree**, the successor is the **leftmost node** of that subtree. Successor of 30 is 35.
2. Otherwise, it is the nearest **ancestor whose left subtree contains the node**. Successor of 45 is 50: walking up, 45 is in 40's right, 40 is in 30's right, but 30 is in 50's left.

Without parent pointers you can find it top-down from the root: every time you go left, the current node is a candidate.

```python
def successor(root, key):
    succ, node = None, root
    while node:
        if key < node.key:
            # A left turn finds a greater
            # key.
            succ = node    # candidate
            node = node.left
        else:
            node = node.right
    return succ
```

This also works for keys that are not in the tree (successor of 47 is 50) and returns None for the maximum. It is O(h), where h is the tree's height: one step per level.

## Validating a BST

A classic interview question with a classic wrong answer: check that each node's left child is smaller and its right child is larger.

```
      10
     /  \
    5    15
        /
       6        <- 6 is below 10, yet is in
                   10's right subtree
```

Every parent-child pair here looks fine, but 6 sits in the right subtree of 10, so this is **not** a BST. The damage is real: searching for 6 goes left at 10 because 6 is smaller, then right at 5, and falls off the tree. The key is present but unreachable.

The fix is to pass down the range each node must fall within. This numeric example requires finite keys comparable with float infinities; it rejects NaN and infinite keys, and is not a validator for arbitrary string or custom-object keys:

```python
def is_bst(node, lo=float('-inf'),
           hi=float('inf')):
    if node is None:
        return True
    k = node.key
    # Ancestor bounds constrain the entire
    # path.
    if not (lo < k < hi):
        return False
    return (is_bst(node.left, lo, k) and
            is_bst(node.right, k, hi))
```

Going left tightens the upper bound; going right tightens the lower bound. An equivalent approach does an in-order traversal and checks each key is greater than the previous one. Both are O(n) for n nodes, since every node must be checked.

## Key takeaways
- A successor is the next key in sorted order, not necessarily a child.
- Ancestor bounds expose violations that local comparisons miss.
- Strict bounds match the distinct-key policy used here.

## Further reading
- [Binary search tree — Wikipedia](https://en.wikipedia.org/wiki/Binary_search_tree)
- [Binary Search Trees — Algorithms, 4th ed. (Sedgewick & Wayne)](https://algs4.cs.princeton.edu/32bst/)
