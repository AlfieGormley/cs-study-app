---
id: tree-bst-deletion-cases
title: Deleting leaves and internal BST nodes
level: intermediate
minutes: 3
sourceLesson: tree-bst
summary: Remove a leaf, splice a single child, or substitute a two-child node.
---

Earlier units established a strict BST ordering with distinct, mutually comparable keys: every left-subtree key is smaller and every right-subtree key larger. Use the Node with key, left and right fields introduced in the search unit. Here n counts keys and h measures tree height in edges. Comparisons have constant cost; recursive code remains limited by Python call depth.

## Delete: the three cases

Deletion is the operation people get wrong, because removing a node can leave a hole that must be filled without breaking the ordering. Find the node, then:

1. **No children (a leaf).** Just remove it. Deleting 20 sets 30's left pointer to None.
2. **One child.** Splice the child into the node's place. Deleting 60 makes 65 the left child of 70. Everything in 60's subtree was already between 50 and 70, so order is preserved.
3. **Two children.** You cannot splice two subtrees into one pointer. Instead, replace the node's key with its **in-order successor** (the smallest key in its right subtree), then delete the successor from the right subtree. The successor has no left child, so that second delete is always case 1 or 2.

```python
def delete(node, key):
    if node is None:
        return None
    if key < node.key:
        node.left = delete(node.left, key)
    elif key > node.key:
        # Reconnect the repaired right
        # subtree.
        node.right = delete(node.right, key)
    else:
        # cases 1 and 2: 0 or 1 child
        if node.left is None:
            return node.right
        if node.right is None:
            return node.left
        # case 3: two children
        succ = node.right
        while succ.left:
            succ = succ.left
        # Copy the next sorted key, then
        # remove it.
        node.key = succ.key
        # Reconnect the repaired right
        # subtree.
        node.right = delete(node.right,
                            succ.key)
    return node
```

Deleting 30 (two children) from the example: its successor is 35, the leftmost node in its right subtree. Copy 35 into 30's node, then delete the old 35 leaf.

```
 before            after
     30                35
    /  \              /  \
  20    40          20    40
       /  \                 \
     35    45                45
```

Why does the successor work? It is larger than everything in the left subtree (it came from the right) and smaller than everything else in the right subtree (it was the minimum there). The **in-order predecessor** (maximum of the left subtree) works equally well.

> [!warning] Copying keys is not always allowed
> Copying the successor's key into the node is fine for a textbook, but in real code other objects may hold references to nodes (iterators, handles). Production implementations such as the Linux rbtree and common C++ standard-library `std::map` implementations instead **relink** the successor node into the deleted node's position, so a node never changes key.

Always using the successor (known as **Hibbard deletion**) is asymmetric: right subtrees keep losing their minimum, and after long random sequences of inserts and deletes the tree becomes visibly skewed to the left, and searches can degrade relative to the insertion-only random-tree model. Choosing between successor and predecessor does not establish a logarithmic-height guarantee. A self-balancing policy does.

## Key takeaways
- Remove a leaf, splice a single child, or substitute a two-child node.
- The successor is the smallest key in the right subtree.
- Reconnect each returned subtree root after a recursive deletion.

## Further reading
- [Binary search tree — Wikipedia](https://en.wikipedia.org/wiki/Binary_search_tree)
- [Binary Search Trees — Algorithms, 4th ed. (Sedgewick & Wayne)](https://algs4.cs.princeton.edu/32bst/)
