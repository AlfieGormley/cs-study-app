---
id: tree-problems
title: Common tree problems
level: advanced
minutes: 15
summary: The recurring patterns behind tree interview problems and real code, worked through lowest common ancestor, diameter, path sums, serialisation and rebuilding a tree from its traversals.
---

Tree problems look endlessly varied, but nearly all of them use one of a few patterns. Learn the patterns and most "new" problems become variations.

1. **Post-order combine.** Each call returns a summary of its subtree (height, sum, "found it?"), and the parent combines its children's summaries. Often a second value, the global best, is tracked on the side.
2. **Pre-order with state passed down.** Each call receives information from above (a running sum, a valid range, a depth) and passes an updated version to its children.
3. **Level-order** when the question mentions levels, widths or nearest anything.

This lesson works through the classics. Assume finite acyclic binary trees without shared nodes or concurrent mutation. These recursive examples are limited by Python call depth. Time bounds use unit-cost arithmetic; hashing-based bounds are expected. Throughout, n is the number of nodes and h is the tree's height in edges. Working recursion depth is O(h + 1), but dictionaries, serialized text and returned trees can require additional storage.

## Lowest common ancestor

The **lowest common ancestor** (LCA) of nodes p and q is the deepest node that has both as descendants (a node counts as its own descendant). It underlies "how are these two related?" questions: the nearest shared directory of two files, merge bases of Git commits (a DAG can have several incomparable best common ancestors, unlike a rooted tree), or the distance between two nodes. The path from p to q climbs from p up to their LCA, then goes down to q, so:

```formula
d(p, q) = D(p) + D(q) − 2 × D(a)
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
    return left or right
```

If both sides report a find, this node is where the paths diverge. If only one does, pass its result up. When p is an ancestor of q, the search returns p as soon as it reaches it without looking below, which is correct because p is then the LCA. (This version assumes both nodes are in the tree; if either might be missing, count the finds explicitly.)

### Many queries

For millions of LCA queries on a fixed tree of n nodes, each O(n) walk is too slow. Two standard upgrades:

- **Binary lifting**: precompute, for every node, its ancestors 1, 2, 4, 8, … levels up (see the table recurrence below), in O(n log n) time. Then lift the deeper node to the same depth and jump both up together in powers of two: O(log n) per query.
- **Euler tour + range minimum**: record a node and its depth on entry and again after returning from each child (not just DFS preorder); the LCA is the shallowest node between the first visits of p and q. With a sparse table, queries become O(1) after O(n log n) preprocessing. (Range-query structures such as segment and Fenwick trees are covered in the advanced module.)

The binary-lifting table is built from itself: two half-size jumps make one full-size jump.

```formula
A_0(v) = P(v)
A_k(v) = A_{k−1}(A_{k−1}(v))
K = ⌈log_2(n)⌉
K = ⌈log_2(100000)⌉ = ⌈16.6⌉ = 17
where
v: any node
P(v): the parent of v
A_0(v): the ancestor 2^0 = 1 level above v, which is simply its parent
k: the table level, from 0 up to K − 1
A_k(v): the ancestor of v that is 2^k levels above it (k copies of 2 multiplied together: 1, 2, 4, 8, …)
A_{k−1}(v): the ancestor 2^(k−1) levels above v, from the previous level of the table
K: the number of table levels needed so that a jump can cover any depth
n: the number of nodes
log_2(n): the base-2 logarithm of n: the power you raise 2 to in order to get n
⌈ ⌉: ceiling: round up to a whole number
In words: the ancestor 2^k levels up is the ancestor 2^(k−1) levels above the ancestor 2^(k−1) levels up, so each level of the table is built from the one before.
```

For 100,000 nodes that is 17 levels, 1.7 million table entries, and any climb of up to 100,000 levels takes at most 17 jumps (one per 1-bit in its binary form).

## Diameter

The **diameter** is the number of edges on the longest path between any two nodes. The trap: that path need **not** pass through the root.

```
          1
         /
        2
       / \
      3   6
     /     \
    4       7
   /         \
  5           8
```

The longest path here is 5–4–3–2–6–7–8: 6 edges, bending at node 2. The root is not on it.

Every path has a single highest node where it bends. At that node it goes down one edge into each subtree and then as deep as that subtree allows:

```formula
B(x) = (h(x_L) + 1) + (h(x_R) + 1)
B(2) = (2 + 1) + (2 + 1) = 6
h(∅) = −1
B(5) = (−1 + 1) + (−1 + 1) = 0
where
x: the node where the path bends (its highest node)
B(x): the length, in edges, of the longest path that bends at x
h(x_L): the height of x's left subtree, in edges
h(x_R): the height of x's right subtree, in edges
h(∅): the height of an empty subtree, taken as −1
∅: an empty subtree (None in Python)
In words: the longest path bending at a node uses one edge into each child plus each child's height, and the diameter is the largest such value over all nodes.
```

At node 2 above, both subtrees have height 2, giving the 6-edge path; at a leaf such as 5 the empty sides give 0. So compute heights in post-order and track the best bend seen:

```python
def diameter(root):
    best = 0
    def height(node):
        nonlocal best
        if node is None:
            return -1
        hl = height(node.left)
        hr = height(node.right)
        # path bending at this node
        best = max(best, hl + hr + 2)
        return 1 + max(hl, hr)
    height(root)
    return best
```

In the code, `hl + hr + 2` is the formula above, and returning −1 for None makes a leaf contribute 0 edges, as it should. This is the archetype of "return one thing, track another": the function *returns* the height (useful to the parent) but *records* the diameter (useful only globally).

> [!warning] The O(n²) version
> Computing `height(left) + height(right)` separately at every node recomputes heights from scratch, which is O(n²) on a chain of n nodes (about n²/2 node visits, n times n halved). Combining both in one post-order pass keeps it O(n).

## Path sums

Three questions with similar names and different techniques.

### Root-to-leaf sum: pass state down

"Is there a root-to-leaf path summing to target?" Subtract as you descend; check at the leaves.

```python
def has_path_sum(node, target):
    if node is None:
        return False
    r = target - node.val
    if not node.left and not node.right:
        return r == 0
    return (has_path_sum(node.left, r) or
            has_path_sum(node.right, r))
```

The leaf check matters: without it, a node with one child could "succeed" at its empty side, counting a path that does not end at a leaf.

### Any downward path: prefix sums

"How many downward paths (starting anywhere, ending anywhere below) sum to target?" Checking every start node is O(n²) on a chain of n nodes. Instead, borrow the **prefix-sum** trick from arrays. Keep the running total from the root down to each node; a downward segment's sum is then a difference of two running totals:

```formula
S = R(v) − R(u)
R(v) − R(u) = T
R(u) = R(v) − T
R(u) = 18 − 8 = 10
where
v: the node where the segment ends (the current node)
u: an ancestor of v; the segment runs from just below u down to v
R(v): the running sum: the total of all values from the root down to v, inclusive
R(u): the running sum from the root down to u
S: the sum of the values on the segment below u down to v
T: the target sum
In words: a downward segment ending here sums to the target exactly when some ancestor's running sum equals the current running sum minus the target.
```

For example, on the path 10 → 5 → 3 with target 8, the running sums are 10, 15 and 18. At node 3, 18 − 8 = 10 is the running sum at the root, so the segment 5 → 3 sums to 8. In the code, `run` is R(v) and `seen` counts the running sums on the current path.

```python
from collections import defaultdict

def count_paths(root, target):
    seen = defaultdict(int)
    seen[0] = 1            # empty prefix
    def dfs(node, run):
        if node is None:
            return 0
        run += node.val
        n = seen.get(run - target, 0)
        seen[run] += 1
        n += dfs(node.left, run)
        n += dfs(node.right, run)
        seen[run] -= 1     # backtrack
        if seen[run] == 0:
            del seen[run]
        return n
    return dfs(root, 0)
```

The **backtrack** line is essential: the map must only contain prefixes on the *current* path, so a node's prefix is removed when the recursion leaves it. Without it, sums from a sibling branch leak in. Removing zero-count entries keeps O(h + 1) distinct active prefixes for a tree of height h; expected time is O(n) for n nodes with constant-cost integer arithmetic and hashing.

### Maximum path sum: post-order with clamping

"Largest sum over any path" (values may be negative). At each node, a path can bend here using the best **downward gain** from each side, but it can only pass **one** side up to the parent, because a path cannot fork. Negative gains are clamped to 0 (just don't extend that way).

```formula
g(x) = v(x) + max(G_L, G_R)
G_L = max(g(x_L), 0)
G_R = max(g(x_R), 0)
B(x) = v(x) + G_L + G_R
B(x) = 2 + 1 + 3 = 6, g(x) = 2 + 3 = 5
where
x: a node; x_L and x_R are its left and right children
x_L: the left child of x
x_R: the right child of x
v(x): the value stored at x (may be negative)
g(x): the gain of x: the largest sum of a path that starts at x and goes down one side only
G_L: the gain from the left side, clamped so it is never below 0 (0 means "don't extend left")
G_R: the gain from the right side, clamped the same way
B(x): the best sum of a path that bends at x, using both sides
max: the larger of the values listed
In words: a node passes up its own value plus the better of its two clamped gains, and records its value plus both clamped gains as a candidate answer.
```

The example line is a node of value 2 whose children are leaves of value 1 and 3: the bend sums to 6, and the node offers its parent a one-sided gain of 5.

```python
def max_path_sum(root):
    if root is None:
        raise ValueError("empty tree")
    best = float('-inf')
    def gain(node):
        nonlocal best
        if node is None:
            return 0
        l = max(gain(node.left), 0)
        r = max(gain(node.right), 0)
        best = max(best, node.val + l + r)
        return node.val + max(l, r)
    gain(root)
    return best
```

Initialise `best` to minus infinity (`float('-inf')`, smaller than any number), not 0: in a tree of all-negative values the answer is the largest single node, which is negative. Same shape as diameter: return the one-sided gain, record the two-sided best.

## Serialise and deserialise

To send a tree over a network or save it to disk you must flatten it so it can be rebuilt **exactly**. A traversal of values alone is not enough: the trees `1 → left 2` and `1 → right 2` both have pre-order `1, 2`. The fix is to record the **empty children** too.

```
        3
       / \
      9   20
         /  \
        15   7

pre-order with '#' for None:
3,9,#,#,20,15,#,#,7,#,#
```

```python
def serialise(root):
    out = []
    def pre(node):
        if node is None:
            out.append('#')
            return
        out.append(str(node.val))
        pre(node.left)
        pre(node.right)
    pre(root)
    return ','.join(out)

def deserialise(data):
    tokens = iter(data.split(','))
    def build():
        t = next(tokens)
        if t == '#':
            return None
        node = Node(int(t))
        node.left = build()
        node.right = build()
        return node
    root = build()
    if next(tokens, None) is not None:
        raise ValueError("trailing tokens")
    return root
```

This teaching format supports integer node values. Truncated input raises StopIteration, invalid integer text raises ValueError, and extra tokens are rejected; untrusted input also requires size and depth limits. Runtime and storage depend on encoded character length, not just node count.

Deserialising consumes the tokens in the same pre-order they were written, so each recursive call knows exactly where its subtree begins and ends. A tree of n nodes produces n values plus **n + 1** null markers (lesson 1):

```formula
T = n + (n + 1) = 2 × n + 1
T = 5 + 6 = 11
where
T: the number of tokens in the serialised string
n: the number of nodes, each written as one value; 5 in the example above
In words: every node writes its value, and a binary tree of n nodes has n + 1 empty child slots, each written as one #.
```

The example string `3,9,#,#,20,15,#,#,7,#,#` has 5 values and 6 markers: 11 tokens. Level-order with nulls (the format LeetCode displays) works too. A JSON or Protocol Buffers schema can encode nested child relationships explicitly; the format alone does not choose a tree representation.

## Constructing a tree from traversals

Given traversals **without** null markers, when can you rebuild the tree? With **distinct** values:

| Given | Unique tree? |
|---|---|
| Pre-order + in-order | Yes |
| Post-order + in-order | Yes |
| Pre-order + post-order | Only if full |
| Pre-order alone | No (but yes for a BST) |

In-order is the key: once you know the root, its position in the in-order sequence tells you exactly which values are in the left and right subtrees. Pre-order tells you the root (its first element), then the left subtree's root, and so on.

```
preorder: 3 | 9 | 20 15 7
inorder:  9 | 3 | 15 20 7
          L  root   R
```

```python
def build_tree(preorder, inorder):
    if len(preorder) != len(inorder):
        raise ValueError("length mismatch")
    pos = {v: i for i, v
           in enumerate(inorder)}
    if len(pos) != len(inorder):
        raise ValueError("duplicate values")
    if set(preorder) != set(inorder):
        raise ValueError("values differ")
    it = iter(preorder)
    def build(lo, hi):     # inorder[lo:hi]
        if lo >= hi:
            return None
        node = Node(next(it))
        mid = pos[node.val]
        if not lo <= mid < hi:
            raise ValueError("bad order")
        node.left = build(lo, mid)
        node.right = build(mid + 1, hi)
        return node
    return build(0, len(inorder))
```

For distinct hashable values with consistent equality, the dictionary gives expected O(1) index lookup. For n values, the build takes expected O(n) time and O(n) auxiliary dictionary/set space plus the returned nodes; invalid traversal pairs raise an error. The left subtree must be built before the right because that is the order pre-order lists them.

Pre-order and post-order alone are ambiguous whenever a node has a single child: `1 → left 2` and `1 → right 2` both give pre-order `1 2` and post-order `2 1`. And a BST *can* be rebuilt from pre-order alone, because sorting the n values supplies its in-order, at O(n log n) comparison cost; a bounds-based reconstruction can avoid sorting.

## Key takeaways
- Most tree problems are post-order combine (return a subtree summary) or pre-order with state passed down; diameter and max path sum return one value while recording another.
- LCA in a BST follows the split point in O(h) for height h; in a general tree, the node where both sides report a find is the LCA. Binary lifting answers many queries in O(log n) each, for n nodes.
- The diameter need not pass through the root; compute it from heights in one O(n) pass over n nodes.
- Downward path sums use the prefix-sum hash map with backtracking for O(n).
- Serialise with null markers; rebuild from pre-order (or post-order) plus in-order, with a value-to-index map for O(n).

## Further reading
- [Lowest common ancestor — Wikipedia](https://en.wikipedia.org/wiki/Lowest_common_ancestor)
- [Lowest Common Ancestor (Euler tour) — cp-algorithms](https://cp-algorithms.com/graph/lca.html)
- [LCA with binary lifting — cp-algorithms](https://cp-algorithms.com/graph/lca_binary_lifting.html)
- [Tree traversal — Wikipedia](https://en.wikipedia.org/wiki/Tree_traversal)
- [Euler tour technique — Wikipedia](https://en.wikipedia.org/wiki/Euler_tour_technique)
