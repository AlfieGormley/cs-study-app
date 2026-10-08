---
id: tree-balanced
title: Balanced search trees
level: intermediate
minutes: 15
summary: Rotations, AVL trees and red-black trees, the invariants that guarantee logarithmic height, how they compare, and where they run in practice (Java TreeMap, C++ std::map, the Linux scheduler).
---

A plain BST is only as good as its insertion order. Feed it sorted keys and it becomes a linked list. AVL and red-black trees maintain balancing invariants after updates, using local rotations and metadata changes. Other balancing schemes can rebuild subtrees instead.

The result is a hard guarantee: for n keys, the height stays O(log n) (growing only with the logarithm of n, a small multiple of about 20 for a million keys) no matter what order keys arrive in, so search, insert and delete are **O(log n) worst case**. The two classic designs are **AVL trees** (1962) and **red-black trees** (1972 as symmetric B-trees; the red/black formulation dates from 1978). They differ in how strict their invariant is.

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

A rotation updates a constant number of links and metadata fields and does no searching, so it is **O(1)**: a fixed amount of work, however big the tree. AVL and red-black trees use rotations plus bookkeeping (heights for AVL, colours for red-black).

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

The third line is node 30 in the "insert 30, 10, 20" example below: its left child 10 has a child of its own and 30 has no right child, so the heights are 1 and −1 and the balance factor is 2, which breaks the invariant. The code's `bf(n)` computes exactly this.

### Why that guarantees O(log n)

Ask: what is the fewest nodes an AVL tree of height h can have? The sparsest one has one subtree of height h − 1 and the other of height h − 2 (the most lopsided the invariant allows), each as sparse as possible, plus the root:

```formula
N(h) = N(h − 1) + N(h − 2) + 1
N(0) = 1
N(1) = 2
N(2) = 2 + 1 + 1 = 4
N(3) = 4 + 2 + 1 = 7
N(4) = 7 + 4 + 1 = 12
N(5) = 12 + 7 + 1 = 20
N(6) = 20 + 12 + 1 = 33
N(7) = 33 + 20 + 1 = 54
where
h: the height of the AVL tree, in edges
N(h): the smallest number of nodes an AVL tree of height h can have
In words: the sparsest AVL tree of height h is a root with a sparsest subtree of height h − 1 on one side and of height h − 2 on the other.
```

Those counts are each one less than a Fibonacci number, so they grow exponentially with h, and turning that round gives the height limit:

```formula
N(h) = F(h + 3) − 1
N(h) ≈ φ^(h+3) / √5
h_max ≈ 1.44 × log_2(n)
h_max ≈ 1.44 × log_2(10^6) ≈ 28.7
N(0) = F(3) − 1 = 2 − 1 = 1
N(5) = F(8) − 1 = 21 − 1 = 20
where
N(h): the smallest number of nodes an AVL tree of height h can have (from the recurrence above)
h: the height of the tree, in edges
F(k): the k-th Fibonacci number, with F(1) = F(2) = 1 and each later one the sum of the two before (1, 1, 2, 3, 5, 8, …)
k: a position in the Fibonacci sequence
φ: phi, the golden ratio (1 + √5) / 2 ≈ 1.618, the factor by which Fibonacci numbers grow each step
φ^(h+3): φ multiplied by itself h + 3 times; dividing by √5 (about 2.236) gives roughly 1.89 × 1.618^h
h_max: the greatest height an AVL tree with n nodes can have
n: the number of nodes (keys) in the tree
log_2(n): the base-2 logarithm of n: the power you raise 2 to in order to get n; log_2(10^6) ≈ 19.93
√5: the square root of 5, about 2.236
≈: approximately equal to
In words: because the fewest nodes for height h grows like 1.618^h, an AVL tree can never be more than about 1.44 times taller than the shortest possible binary tree.
```

The last two lines check the Fibonacci form against the counts above. The 1.44 × log₂ n formula is an approximation for large n. For a million keys, the exact recurrence gives maximum AVL height 27 (28 levels): N(27) = 832,039 nodes fit within a million but N(28) = 1,346,268 do not. A complete binary tree has height 19 (20 levels).

### Insert and rebalance

Insert as in a plain BST, then walk back up the path updating heights. At the first node whose balance factor becomes +2 or −2, one of four cases applies, named after the path from that node down to where the new key went.

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

After an insert that creates imbalance, one rebalancing step (one single or one double rotation) restores balance, because it returns the subtree to the height it had before the insert, so no ancestor needs fixing. Deletion is worse: a rotation can shrink a subtree's height, unbalancing its parent in turn, so a delete in a tree of n keys may need **O(log n) rotations**, up to one per level of the path.

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

For this proof, count a node's black-height without the node itself: the number of black nodes on a path below it down to NIL, including the NIL (so a NIL has black-height 0). This differs from the inclusive count used in the preceding diagram. Two facts combine:

- No two reds are adjacent, so at least half the nodes on any path below the root are black: the height is at most twice the root's black-height.
- A subtree whose root has black-height b holds a number of real (non-NIL) nodes that grows exponentially with its black-height (the first line below), which you can prove by mathematical induction: it holds for a NIL, and each child's black-height is at most one less.

```formula
n_x ≥ 2^{bh(x)} − 1
h ≤ 2 × bh(r)
n ≥ 2^{h/2} − 1
h ≤ 2 × log_2(n + 1)
h ≤ 2 × log_2(10^6 + 1) ≈ 39.9
where
x: any node in the tree
bh(x): the black-height of x: black nodes on any path from just below x down to a NIL leaf, counting the NIL but not x
n_x: the number of real (non-NIL) nodes in the subtree rooted at x
r: the root of the tree
h: the height of the tree, in edges, measured from the root down to the deepest NIL leaf (the height counting only real nodes is one less, so it obeys the same bound)
n: the number of keys (real nodes) in the whole tree
2^{bh(x)}: 2 multiplied by itself bh(x) times
log_2(n + 1): the base-2 logarithm of n + 1: the power you raise 2 to in order to get n + 1
≥: is at least
≤: is at most
≈: approximately equal to
In words: a red-black tree is at most twice as tall as its black-height, and the black-height can only be about log_2(n), so the height is at most 2 × log_2(n + 1).
```

The third line comes from applying the first line at the root and substituting the second; solving it for h gives the fourth. For a million keys the bound is about 40; actual height depends on the implementation and update history.

### Insert, in outline

1. Insert as in a BST and colour the new node **red** (this preserves rule 3; rule 2 or the root-colour rule may need repair).
2. If its parent is black, done.
3. If its parent is red, look at the **uncle** (the parent's sibling):
   - **Uncle red:** recolour parent and uncle black and the grandparent red, then repeat the check from the grandparent. No rotation; the problem moves up two levels.
   - **Uncle black:** one or two rotations around the grandparent plus a recolour fix it for good.
4. Colour the root black.

For the conventional bottom-up red-black algorithms, insertion uses at most two rotations and deletion at most three. Recolouring and fix-up traversal can take O(log n) steps in one update of a tree of n keys, because the red-uncle case can repeat up the whole path. These rotation bounds do not apply automatically to every red-black variant.

> [!note] Red-black trees are 2-3-4 trees in disguise
> Glue each black node to its red children and you get a B-tree node with 2, 3 or 4 children. Rule 3 says all leaves of that B-tree are at the same depth. Sedgewick's **left-leaning red-black tree** (2008) restricts red links further and its 2-3 variant maps onto 2-3 trees, which makes the code much shorter.

## AVL versus red-black

Side by side, the two height bounds for n keys are:

```formula
h_AVL ≈ 1.44 × log_2(n)
h_RB ≤ 2 × log_2(n + 1)
h_AVL ≈ 1.44 × 19.93 ≈ 28.7
h_RB ≤ 2 × 19.93 ≈ 39.9
where
h_AVL: the greatest possible height of an AVL tree, in edges (an approximation for large n)
h_RB: the greatest possible height of a red-black tree, in edges
n: the number of keys stored; the last two lines use n = 10^6, for which log_2(n) ≈ 19.93
log_2(n): the base-2 logarithm of n: the power you raise 2 to in order to get n
≈: approximately equal to
≤: is at most
In words: the red-black worst-case height bound is about 40 % higher than the AVL one for the same number of keys; both are logarithmic in n.
```

(The exact AVL worst case for a million keys is 27, from the recurrence above.)

| | AVL | Red-black |
|---|---|---|
| Max height | ~1.44 log₂ n | 2 log₂(n+1) |
| Lookup height bound | Tighter | Looser |
| Rotations/insert | ≤ 1 (single or double) | ≤ 2 |
| Rotations/delete | O(log n) | ≤ 3 |
| Extra data | Height or balance factor | 1 colour bit |

Search and single-key updates are O(log n) for n keys, with constant-cost comparisons; traversing all entries is O(n). Practical tradeoffs:

- AVL offers a tighter worst-case height bound; actual read performance needs measurement.
- **Write-heavy** or general-purpose libraries usually choose red-black: fewer rotations on delete, and a colour bit can be hidden in the low bit of an aligned pointer, as the Linux kernel does.

## Where they are used

- **Java `TreeMap` and `TreeSet`**: red-black trees, giving logarithmic get, put, floorKey and ceilingKey operations; full sorted iteration over n entries takes O(n).
- **Java `HashMap`**: since Java 8, when a single bucket grows past 8 colliding entries (in a table of at least 64 buckets), it is converted into a small red-black tree, Comparable keys can use ordering to obtain logarithmic bin searches. Equal-hash keys without usable comparison ordering can still require linear search within a tree bin.
- **C++ `std::map` and `std::set`**: red-black trees in the major standard libraries (libstdc++, libc++, MSVC). The standard only mandates O(log n) operations (for n elements) and iterators that stay valid across inserts, without mandating one specific data structure.
- **Linux kernel**: a generic intrusive rbtree (`lib/rbtree.c`) used widely. The **Completely Fair Scheduler** kept runnable tasks in a red-black tree ordered by `vruntime` (virtual runtime) and ran the leftmost task, caching a pointer to it so picking the next task is O(1). Linux began transitioning fair scheduling toward EEVDF in version 6.6; its implementation uses an augmented red-black tree. `epoll` also stores its watched file descriptors in one.

> [!example] Why CFS wanted a tree, not a heap
> A heap gives the minimum just as fast. But the scheduler also removes arbitrary tasks (one blocks on I/O, one is killed) and re-inserts them with new keys. With an intrusive tree, each task embeds its own tree node, so removing a given task from n runnable tasks is O(log n) with no search. A binary heap would need an extra position index to find an arbitrary entry, and it cannot cheaply answer "which task comes next after this one?".

### Other balanced structures, briefly

- **B-trees and B+ trees** use the same idea with hundreds of keys per node, matching disk pages. Many relational database indexes use them; hash, bitmap and other index types also exist (covered in System Design: databases).
- **Skip lists** give expected O(log n) search over n keys with randomised towers of linked lists; Redis sorted sets can use a skip list plus dictionary or a compact encoding.
- **Treaps** and **splay trees** balance with randomness or by moving accessed nodes to the root.
- Python has no built-in balanced tree. `sortedcontainers` uses a list of sorted lists, which offers different locality and update tradeoffs from pointer-based trees.

> [!note] Evidence gap
> Universal AVL-versus-red-black lookup wins and sortedcontainers performance wins are omitted because no matching workload, implementation and reproducible benchmark were supplied.

## Key takeaways
- Rotations restructure a subtree in O(1) while preserving in-order order; AVL and red-black balancing use them.
- AVL keeps every balance factor at −1, 0 or +1, so for n keys its height is at most about 1.44 times the base-2 logarithm of n (27 for a million keys). Inserts need at most one single or double rotation; deletes may need O(log n).
- Red-black trees forbid red-red edges and require equal black-height on every path, so their height is at most twice the base-2 logarithm of n + 1 (about 40 for a million keys). Conventional bottom-up algorithms use at most 2 rotations per insert and 3 per delete; other variants differ.
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
