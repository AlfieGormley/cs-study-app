---
id: tree-recursive-orders
title: Recursive traversal orders
level: basic
minutes: 5
sourceLesson: tree-traversals
summary: Pre-order handles parents first; post-order handles children first.
---

A list has one natural order: front to back. A tree does not. To visit every node you must decide, at each node, whether to handle the node itself before, between or after its children, and whether to go **deep** first or **wide** first.

Those choices give the four traversals you will use constantly. Each emits every node once; with constant-cost node processing and suitable stack/queue operations, these implementations take O(n) time, where n is the number of nodes: the work grows in direct proportion to the size of the tree. Assume finite acyclic binary trees without shared subtrees or concurrent mutation. They differ in the order of visits and in how much extra memory they need.

## The running example

```
          F
        /   \
       B     G
      / \     \
     A   D     I
        / \   /
       C   E H
```

| Traversal | Order | Result |
|---|---|---|
| Pre-order | node, left, right | F B A D C E G I H |
| In-order | left, node, right | A B C D E F G H I |
| Post-order | left, right, node | A C E D B H I G F |
| Level-order | level by level | F B G A D I C E H |

This tree happens to be a binary search tree, which is why in-order comes out alphabetical. That is not a coincidence (see below).

## Depth-first: pre, in and post-order

The three depth-first traversals have identical structure; only the position of the "visit" line moves.

```python
def preorder(node, out):
    if node is None:
        return
    # Record this node at this position.
    out.append(node.val)       # visit
    preorder(node.left, out)
    preorder(node.right, out)

def inorder(node, out):
    if node is None:
        return
    inorder(node.left, out)
    # Record this node at this position.
    out.append(node.val)       # visit
    inorder(node.right, out)

def postorder(node, out):
    if node is None:
        return
    postorder(node.left, out)
    postorder(node.right, out)
    # Record this node at this position.
    out.append(node.val)       # visit
```

A trick for doing them by hand: walk round the outline of the tree anticlockwise starting at the root, keeping the tree on your left. Pre-order records a node when you pass its **left** side, in-order when you pass **underneath** it, post-order when you pass its **right** side.

### What each order is for

- **Pre-order** sees a parent before its children. Use it to copy or serialise a tree, including null markers or other shape metadata when reconstruction is required; the root-first order supports top-down rebuilding, and to print indented outlines such as a directory listing.
- **In-order** on a binary search tree yields keys in **sorted order**. Use it to validate a BST, find the k-th smallest key or range-scan.
- **Post-order** sees children before their parent. Use it whenever a node's answer depends on its subtrees: computing **node height** or size, **freeing** memory (delete children before the parent), evaluating an **expression tree** (`3 4 +` is post-order for `3 + 4`), or `rm -r` and `du` on a directory.

> [!tip] Most tree problems are post-order
> "Compute something for every subtree and combine" (height, diameter, balanced check, max path sum) is post-order: recurse into both children, then combine their results at the node. The common-problem units is full of these.

### Space: the hidden cost

Recursion is not free. Each pending call sits on the call stack, and the deepest the recursion goes is one call per level on the longest root-to-leaf path:

```formula
F_max = h + 2
F_max = ⌊log_2(1000000)⌋ + 2 = 21
F_max = (1000000 − 1) + 2 = 1000001
where
F_max: the most call frames (pending recursive calls) on the call stack at once
h: the height of the tree in edges; a path of h edges has h + 1 nodes, each with its own frame, plus the temporary call on an empty child
n: the number of nodes; 1,000,000 in both example lines
log_2(n): the base-2 logarithm of n: the power you raise 2 to in order to get n; log_2(1000000) ≈ 19.93
⌊ ⌋: floor: round down to a whole number
In words: recursive depth-first traversal needs one stack frame per node on the deepest path plus its final empty-child call, so its memory grows with the height, not with the number of nodes.
```

The two example lines are a million-node complete tree (height 19, so 21 frames including an empty-child call) and a million-node chain (height one less than its node count, so 1,000,001 frames including an empty-child call). So depth-first traversal uses O(h + 1) working space, excluding the O(n) output: O(log n) for a balanced tree but **O(n) for a degenerate one**.

CPython commonly starts with a recursion limit of 1,000; query sys.getrecursionlimit() for the actual process. A sufficiently deep chain raises RecursionError, accounting for existing call depth. Raising the limit can create resource risks; an iterative traversal avoids recursive call-depth limits but still needs memory.

## Key takeaways
- Pre-order handles parents first; post-order handles children first.
- In-order yields sorted values only when the tree has BST ordering.
- Recursive working memory grows with height; stored output grows with node count.

## Further reading
- [Tree traversal — Wikipedia](https://en.wikipedia.org/wiki/Tree_traversal)
