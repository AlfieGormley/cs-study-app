---
id: tree-bst-search-insert
title: BST ordering, search and insertion
level: intermediate
minutes: 5
sourceLesson: tree-bst
summary: Ordering constrains entire subtrees, not only immediate children.
---

Binary search on a sorted array of n keys finds a key in O(log n) steps (it halves the range each time, so about 20 steps for a million keys), but inserting a key means shifting everything after it: O(n), work in proportion to n. A **binary search tree** (BST) stores ordered partitions in linked nodes. A step need not halve the remaining keys; search follows a path, after which insertion or deletion relinks nodes.

When the tree is reasonably balanced, search, insert and delete are all **O(log n)**. When it is not, they degrade to O(n). Most of this lesson is about the operations; the later insertion-shape unit explains that failure mode, which the balanced-tree units address.

## The BST property

For **every** node:

- every key in its **left subtree** is **less** than the node's key;
- every key in its **right subtree** is **greater**.

The rule is about whole subtrees, not just immediate children. That distinction is where most BST bugs live (see the later successor-and-validation unit).

```
            50
          /    \
        30      70
       /  \    /  \
     20   40  60   80
         /  \   \
        35  45   65
```

An in-order traversal of this tree gives 20 30 35 40 45 50 60 65 70 80: a BST *is* a sorted sequence, stored as a tree.

Duplicates need a policy. The common choices are to reject them (sets and maps), keep a count in the node, or consistently send equal keys to one side. The code below ignores duplicates and assumes mutually comparable keys with a consistent total order, constant-cost comparisons and no concurrent mutation. Recursive functions are limited by Python call depth. Maps generally update an existing key rather than reject its new value.

## Search

Start at the root. If the key is smaller, go left; if larger, go right; stop when you find it or fall off the tree.

```python
class Node:
    def __init__(self, key):
        self.key = key
        self.left = self.right = None

def search(node, key):
    # Follow only the side containing
    # the key.
    while node and node.key != key:
        if key < node.key:
            node = node.left
        else:
            node = node.right
    return node        # None if absent
```

Searching for 45: 50 (go left), 30 (go right), 40 (go right), 45. Four nodes visited; the Python code can perform both equality and ordering tests at a node.

A search visits one node per level it passes through: one more node than the key's depth, and never more than the tree's height plus one. A miss walks a full path down to an empty child. So the cost depends on the tree's **height**, not directly on how many keys it holds: O(h + 1), where h is the height in edges. The minimum is the leftmost node and the maximum is the rightmost, found the same way.

> [!analogy] Real-world analogy: a higher-or-lower guessing game
> A friend thinks of a number and you guess; after each guess they say "higher" or "lower", and you never need to consider the other side again. You find the number in a handful of guesses if each guess is near the middle of what is left.
>
> **How it maps:** each node's key is a guess, "lower" sends you to the left subtree and "higher" to the right, and the number of guesses is the number of nodes on the search path.
>
> **Where it stops:** in the game you choose a fresh middle guess each time. A BST's guesses are fixed by where earlier keys were inserted, so a badly shaped tree keeps guessing near one end and can need as many guesses as there are keys.

## Insert

Search for the key; the place where the search falls off the tree is exactly where the new key belongs. A new key always becomes a **leaf**.

```python
def insert(node, key):
    if node is None:
        return Node(key)
    if key < node.key:
        # Reconnect the returned
        # subtree root.
        node.left = insert(node.left, key)
    elif key > node.key:
        node.right = insert(node.right, key)
    return node        # duplicates ignored

root = None
for k in [50, 30, 70, 20, 40,
          60, 80, 35, 45, 65]:
    root = insert(root, k)
```

The recursive style "return the (possibly new) subtree root and reassign it" is worth adopting. It avoids special-casing the empty tree and is the same shape you need for delete and for balanced trees.

> [!note] Insertion order determines shape
> The same set of keys can produce very different trees. The order above gives the height-3 tree in the diagram. Inserting the same ten keys in ascending order gives a chain of height 9.

## Key takeaways
- Ordering constrains entire subtrees, not only immediate children.
- Search follows a single root-to-key path.
- Insertion returns a possibly new subtree root and ignores duplicate keys here.

## Further reading
- [Binary search tree — Wikipedia](https://en.wikipedia.org/wiki/Binary_search_tree)
- [Binary Search Trees — Algorithms, 4th ed. (Sedgewick & Wayne)](https://algs4.cs.princeton.edu/32bst/)
