---
id: tree-bst
title: Binary search trees
level: intermediate
minutes: 13
summary: The BST ordering rule, search and insert, the three cases of delete, finding successors, validating a BST correctly, and why sorted input turns a BST into a linked list.
---

Binary search on a sorted array finds a key in O(log n), but inserting a key means shifting everything after it: O(n). A **binary search tree** (BST) stores ordered partitions in linked nodes. A step need not halve the remaining keys; search follows a path, after which insertion or deletion relinks nodes.

When the tree is reasonably balanced, search, insert and delete are all **O(log n)**. When it is not, they degrade to O(n). Most of this lesson is about the operations; the last part is about that failure mode, which lesson 4 fixes.

## The BST property

For **every** node:

- every key in its **left subtree** is **less** than the node's key;
- every key in its **right subtree** is **greater**.

The rule is about whole subtrees, not just immediate children. That distinction is where most BST bugs live (see validation below).

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
    while node and node.key != key:
        if key < node.key:
            node = node.left
        else:
            node = node.right
    return node        # None if absent
```

Searching for 45: 50 (go left), 30 (go right), 40 (go right), 45. Four nodes visited; the Python code can perform both equality and ordering tests at a node. The cost is O(h + 1), where h is the height.

The minimum is the leftmost node and the maximum is the rightmost, also O(h).

## Insert

Search for the key; the place where the search falls off the tree is exactly where the new key belongs. A new key always becomes a **leaf**.

```python
def insert(node, key):
    if node is None:
        return Node(key)
    if key < node.key:
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
        node.key = succ.key
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
> Copying the successor's key into the node is fine for a textbook, but in real code other objects may hold references to nodes (iterators, handles). Production implementations such as the Linux rbtree and C++ `std::map` instead **relink** the successor node into the deleted node's position, so a node never changes key.

Always using the successor (known as **Hibbard deletion**) is asymmetric: right subtrees keep losing their minimum, and after long random sequences of inserts and deletes the tree becomes visibly skewed to the left, and searches can degrade relative to the insertion-only random-tree model. Choosing between successor and predecessor does not establish a logarithmic-height guarantee. A self-balancing policy does.

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
            succ = node    # candidate
            node = node.left
        else:
            node = node.right
    return succ
```

This also works for keys that are not in the tree (successor of 47 is 50) and returns None for the maximum. It is O(h).

## Validating a BST

A classic interview question with a classic wrong answer: check that each node's left child is smaller and its right child is larger.

```
      10
     /  \
    5    15
        /
       6        <- 6 < 10, but it is in
                   10's right subtree
```

Every parent-child pair here looks fine, but 6 sits in the right subtree of 10, so this is **not** a BST. The damage is real: searching for 6 goes left at 10 (6 < 10), then right at 5, and falls off the tree. The key is present but unreachable.

The fix is to pass down the range each node must fall within. This numeric example requires finite keys comparable with float infinities; it rejects NaN and infinite keys, and is not a validator for arbitrary string or custom-object keys:

```python
def is_bst(node, lo=float('-inf'),
           hi=float('inf')):
    if node is None:
        return True
    k = node.key
    if not (lo < k < hi):
        return False
    return (is_bst(node.left, lo, k) and
            is_bst(node.right, k, hi))
```

Going left tightens the upper bound; going right tightens the lower bound. An equivalent approach does an in-order traversal and checks each key is greater than the previous one. Both are O(n).

## Degenerate trees

Search and single-key updates cost O(h + 1); full validation costs O(n). With insertion only, order determines shape; deletions also change it.

| Input order | Shape | Height (n = 1,000) |
|---|---|---|
| Ascending | Right chain | 999 |
| Uniformly random permutation | Random shape | Expected O(log n); no fixed height |
| Median first, recursively | Perfect-ish | 9 |

Inserting sorted keys into a plain BST produces a linked list with extra pointers: every insert walks the whole chain, so building it costs 0 + 1 + ... + (n − 1) = Θ(n²) visited existing nodes. For a million keys that is about 5 × 10¹¹ steps.

Random insertion order is much kinder. For distinct keys inserted in a uniformly random permutation and a uniformly selected stored key, expected depth has leading term 2 ln n ≈ 1.39 log₂ n. Lower-order terms matter for finite sizes. Expected height is also O(log n); this is an expectation, not a bound on every insertion order.

But real data is rarely random. Timestamps, auto-increment IDs and alphabetically sorted imports all arrive in order. For workloads requiring worst-case logarithmic access, use a **self-balancing** tree (AVL, red-black; lesson 4), a B-tree (System Design, databases), a skip list, or a sorted sequence implementation. Python sortedcontainers uses a list of sorted lists; Redis can use a skip list plus dictionary or a compact encoding for sorted sets.

> [!tip] Building a balanced BST from sorted data
> If you have all the keys up front and sorted, pick the **middle** key as the root and recurse on each half. For n > 0 distinct keys, passing index ranges rather than copying slices builds height ⌊log₂ n⌋ in O(n), assuming constant-time node creation.

## Key takeaways
- The BST property applies to whole subtrees: everything left is smaller, everything right is larger. In-order traversal gives sorted keys.
- Search, insert, delete, min, max and successor are all O(h).
- Delete has three cases: leaf (remove), one child (splice), two children (replace with the in-order successor and delete that instead).
- Validate with min/max bounds passed down, not by comparing parents with children.
- Sorted input makes a plain BST a chain of height n − 1, turning O(log n) into O(n). Real systems use balanced trees.

## Further reading
- [Binary search tree — Wikipedia](https://en.wikipedia.org/wiki/Binary_search_tree)
- [Binary Search Trees — Algorithms, 4th ed. (Sedgewick & Wayne)](https://algs4.cs.princeton.edu/32bst/)
- [BST visualisation — VisuAlgo](https://visualgo.net/en/bst)
- [Sorted Containers (Python) docs](https://grantjenks.com/docs/sortedcontainers/)
