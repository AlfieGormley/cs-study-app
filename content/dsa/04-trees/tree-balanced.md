---
id: tree-balanced
title: Balanced search trees
level: intermediate
minutes: 15
summary: Rotations, AVL trees and red-black trees, the invariants that guarantee O(log n) height, how they compare, and where they run in practice (Java TreeMap, C++ std::map, the Linux scheduler).
---

A plain BST is only as good as its insertion order. Feed it sorted keys and it becomes a linked list. AVL and red-black trees maintain balancing invariants after updates, using local rotations and metadata changes. Other balancing schemes can rebuild subtrees instead.

The result is a hard guarantee: height O(log n) no matter what order keys arrive in, so search, insert and delete are **O(log n) worst case**. The two classic designs are **AVL trees** (1962) and **red-black trees** (1972 as symmetric B-trees; the red/black formulation dates from 1978). They differ in how strict their invariant is.

## Rotations

A rotation changes the shape of a small part of the tree while **preserving the in-order sequence**, so the BST property still holds.

```
      y                 x
     / \    right      / \
    x   C   ---->     A   y
   / \      <----        / \
  A   B     left        B   C
```

Here A, B and C are whole subtrees. In both shapes the in-order sequence is A, x, B, y, C. A right rotation at y lifts x up one level and pushes y down; subtree **B changes parent** from x to y. A left rotation is the mirror image.

A rotation updates a constant number of links and metadata fields and does no searching, so it is **O(1)**. AVL and red-black trees use rotations plus bookkeeping (heights for AVL, colours for red-black).

```python
def rotate_right(y):
    x = y.left
    y.left = x.right           # move B
    x.right = y
    fix(y)                     # update
    fix(x)                     # heights
    return x                   # new root
```

## AVL trees

Named after Adelson-Velsky and Landis, the AVL tree was the first self-balancing BST.

**Invariant:** at every node, the heights of the left and right subtrees differ by at most 1. The difference `height(left) − height(right)` is the node's **balance factor**, which must be −1, 0 or +1.

### Why that guarantees O(log n)

Ask: what is the fewest nodes an AVL tree of height h can have? The sparsest one has one subtree of height h − 1 and the other of height h − 2, each as sparse as possible:

```
N(h) = N(h-1) + N(h-2) + 1
N(0) = 1, N(1) = 2

h:    0  1  2  3   4   5   6   7
N(h): 1  2  4  7  12  20  33  54
```

That is the Fibonacci recurrence (N(h) = F(h+3) − 1), so N(h) grows like φ^h with φ ≈ 1.618. Inverting it, an AVL tree with n nodes has height at most about **1.44 log₂ n**. For a million keys, the recurrence gives maximum AVL height 27 (28 levels); a complete binary tree has height 19 (20 levels).

### Insert and rebalance

Insert as in a plain BST, then walk back up the path updating heights. At the first node whose balance factor becomes ±2, one of four cases applies, named after the path from that node down to where the new key went.

| Case | Shape | Fix |
|---|---|---|
| LL | left child left-heavy | rotate right |
| RR | right child right-heavy | rotate left |
| LR | left child right-heavy | left at child, then right |
| RL | right child left-heavy | right at child, then left |

The LR case is the one people miss. Insert 30, 10, 20:

```
  30           30           20
  /            /           /  \
10    -->    20    -->   10    30
  \          /
   20      10
 (LR)   rotate left   rotate right
        at 10         at 30
```

A single right rotation at 30 would just move the zig-zag to the other side; you have to straighten it first.

```python
def insert(n, key):
    if n is None:
        return Node(key)
    if key < n.key:
        n.left = insert(n.left, key)
    elif key > n.key:
        n.right = insert(n.right, key)
    else:
        return n
    fix(n)                     # height
    b = bf(n)
    if b > 1:                  # left-heavy
        if bf(n.left) < 0:     # LR case
            n.left = rotate_left(n.left)
        return rotate_right(n)
    if b < -1:                 # right-heavy
        if bf(n.right) > 0:    # RL case
            n.right = rotate_right(n.right)
        return rotate_left(n)
    return n
```

The following helpers complete the example. Keys are distinct comparable values; duplicate insertions leave the tree unchanged.

```python
class Node:
    def __init__(self, key):
        self.key = key
        self.left = self.right = None
        self.height = 0

def ht(n):
    return -1 if n is None else n.height

def fix(n):
    n.height = 1 + max(ht(n.left),
                       ht(n.right))

def bf(n):
    return ht(n.left) - ht(n.right)

def rotate_left(x):
    y = x.right
    x.right = y.left
    y.left = x
    fix(x)
    fix(y)
    return y
```

Inserting 1 to 7 in order into this AVL tree gives the perfect tree with 4 at the root, where a plain BST would give a chain.

After an insert that creates imbalance, one rebalancing step (one single or one double rotation) restores balance, because it returns the subtree to the height it had before the insert, so no ancestor needs fixing. Deletion is worse: a rotation can shrink a subtree's height, unbalancing its parent in turn, so a delete may need **O(log n) rotations** up the path.

## Red-black trees

A red-black tree relaxes the invariant. Instead of near-perfect balance, it only promises that root-to-NIL paths differ in length by at most a factor of two. In exchange, it does less restructuring.

Every node is coloured red or black, and empty (NIL) children count as black leaves. The rules:

1. The root is black.
2. A red node has no red children (no two reds in a row).
3. Every path from a node down to a NIL leaf passes through the **same number of black nodes**: its **black-height**.

```
          13B
        /     \
      8R       17R
     /  \     /   \
   1B   11B 15B   25B
     \           /
      6R       22R
```

Every root-to-NIL path here has 3 black nodes, counting the root and the NIL itself (for example 13, 8, 1, 6, NIL passes 13, 1 and NIL), and no red node has a red child.

### Why the height is O(log n)

For this proof define bh(x) as the number of black nodes on a path below x to NIL, excluding x but including NIL (and bh(NIL) = 0). This differs from the inclusive count used in the preceding diagram.

- Equal black-height and no consecutive reds bound root-to-NIL path length by twice the root black-height.
- A subtree rooted at x has at least 2^bh(x) − 1 non-NIL nodes, by induction.

Putting these together gives height ≤ **2 log₂(n + 1)**. For a million keys this gives a bound of about 40; actual height depends on the implementation and update history.

### Insert, in outline

1. Insert as in a BST and colour the new node **red** (this preserves rule 3; rule 2 or the root-colour rule may need repair).
2. If its parent is black, done.
3. If its parent is red, look at the **uncle** (the parent's sibling):
   - **Uncle red:** recolour parent and uncle black and the grandparent red, then repeat the check from the grandparent. No rotation; the problem moves up two levels.
   - **Uncle black:** one or two rotations around the grandparent plus a recolour fix it for good.
4. Colour the root black.

For the conventional bottom-up red-black algorithms, insertion uses at most two rotations and deletion at most three. Recolouring and fix-up traversal can take O(log n) in one update. These rotation bounds do not apply automatically to every red-black variant.

> [!note] Red-black trees are 2-3-4 trees in disguise
> Glue each black node to its red children and you get a B-tree node with 2, 3 or 4 children. Rule 3 says all leaves of that B-tree are at the same depth. Sedgewick's **left-leaning red-black tree** (2008) restricts red links further and its 2-3 variant maps onto 2-3 trees, which makes the code much shorter.

## AVL versus red-black

| | AVL | Red-black |
|---|---|---|
| Max height | ~1.44 log₂ n | 2 log₂(n+1) |
| Lookup height bound | Tighter | Looser |
| Rotations/insert | ≤ 1 (single or double) | ≤ 2 |
| Rotations/delete | O(log n) | ≤ 3 |
| Extra data | Height or balance factor | 1 colour bit |

Search and single-key updates are O(log n), with constant-cost comparisons; traversing all entries is O(n). Practical tradeoffs:

- AVL offers a tighter worst-case height bound; actual read performance needs measurement.
- **Write-heavy** or general-purpose libraries usually choose red-black: fewer rotations on delete, and a colour bit can be hidden in the low bit of an aligned pointer, as the Linux kernel does.

## Where they are used

- **Java `TreeMap` and `TreeSet`**: red-black trees, giving logarithmic get, put, floorKey and ceilingKey operations; full sorted iteration takes O(n).
- **Java `HashMap`**: since Java 8, when a single bucket grows past 8 colliding entries (in a table of at least 64 buckets), it is converted into a small red-black tree, Comparable keys can use ordering to obtain logarithmic bin searches. Equal-hash keys without usable comparison ordering can still require linear search within a tree bin.
- **C++ `std::map` and `std::set`**: red-black trees in the major standard libraries (libstdc++, libc++, MSVC). The standard only mandates O(log n) operations and iterators that stay valid across inserts, without mandating one specific data structure.
- **Linux kernel**: a generic intrusive rbtree (`lib/rbtree.c`) used widely. The **Completely Fair Scheduler** kept runnable tasks in a red-black tree ordered by `vruntime` (virtual runtime) and ran the leftmost task, caching a pointer to it so picking the next task is O(1). Linux began transitioning fair scheduling toward EEVDF in version 6.6; its implementation uses an augmented red-black tree. `epoll` also stores its watched file descriptors in one.

> [!example] Why CFS wanted a tree, not a heap
> A heap gives the minimum just as fast. But the scheduler also removes arbitrary tasks (one blocks on I/O, one is killed) and re-inserts them with new keys. With an intrusive tree, each task embeds its own tree node, so removing a given task is O(log n) with no search. A binary heap would need an extra position index to find an arbitrary entry, and it cannot cheaply answer "which task comes next after this one?".

### Other balanced structures, briefly

- **B-trees and B+ trees** use the same idea with hundreds of keys per node, matching disk pages. Many relational database indexes use them; hash, bitmap and other index types also exist (covered in System Design: databases).
- **Skip lists** give expected O(log n) with randomised towers of linked lists; Redis sorted sets can use a skip list plus dictionary or a compact encoding.
- **Treaps** and **splay trees** balance with randomness or by moving accessed nodes to the root.
- Python has no built-in balanced tree. `sortedcontainers` uses a list of sorted lists, which offers different locality and update tradeoffs from pointer-based trees.

> [!note] Evidence gap
> Universal AVL-versus-red-black lookup wins and sortedcontainers performance wins are omitted because no matching workload, implementation and reproducible benchmark were supplied.

## Key takeaways
- Rotations restructure a subtree in O(1) while preserving in-order order; AVL and red-black balancing use them.
- AVL keeps every balance factor in {−1, 0, +1}, giving height ≤ ~1.44 log₂ n. Inserts need at most one single or double rotation; deletes may need O(log n).
- Red-black trees forbid red-red edges and require equal black-height on every path, giving height ≤ 2 log₂(n+1). Conventional bottom-up algorithms use at most 2 rotations per insert and 3 per delete; other variants differ.
- AVL suits lookup-heavy workloads; red-black is the common library default.
- Java's TreeMap, C++'s std::map and the Linux scheduler all use red-black trees.

## Further reading
- [AVL tree — Wikipedia](https://en.wikipedia.org/wiki/AVL_tree)
- [Red–black tree — Wikipedia](https://en.wikipedia.org/wiki/Red%E2%80%93black_tree)
- [Balanced Search Trees — Algorithms, 4th ed. (Sedgewick & Wayne)](https://algs4.cs.princeton.edu/33balanced/)
- [Left-leaning Red-Black Trees — Robert Sedgewick (PDF)](https://sedgewick.io/wp-content/themes/sedgewick/papers/2008LLRB.pdf)
- [Red-black Trees (rbtree) in Linux — kernel docs](https://docs.kernel.org/core-api/rbtree.html)
- [CFS Scheduler — Linux kernel docs](https://docs.kernel.org/scheduler/sched-design-CFS.html)
- [AVL tree visualisation — USF](https://www.cs.usfca.edu/~galles/visualization/AVLtree.html)
