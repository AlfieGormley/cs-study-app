---
id: tree-traversals
title: Tree traversals
level: basic
minutes: 12
summary: Pre-order, in-order, post-order and level-order traversal, recursive and iterative versions, what each is good for, and Morris traversal for O(1) extra space.
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
    out.append(node.val)       # visit
    preorder(node.left, out)
    preorder(node.right, out)

def inorder(node, out):
    if node is None:
        return
    inorder(node.left, out)
    out.append(node.val)       # visit
    inorder(node.right, out)

def postorder(node, out):
    if node is None:
        return
    postorder(node.left, out)
    postorder(node.right, out)
    out.append(node.val)       # visit
```

A trick for doing them by hand: walk round the outline of the tree anticlockwise starting at the root, keeping the tree on your left. Pre-order records a node when you pass its **left** side, in-order when you pass **underneath** it, post-order when you pass its **right** side.

### What each order is for

- **Pre-order** sees a parent before its children. Use it to copy or serialise a tree, including null markers or other shape metadata when reconstruction is required; the root-first order supports top-down rebuilding, and to print indented outlines such as a directory listing.
- **In-order** on a binary search tree yields keys in **sorted order**. Use it to validate a BST, find the k-th smallest key or range-scan.
- **Post-order** sees children before their parent. Use it whenever a node's answer depends on its subtrees: computing **height** or size, **freeing** memory (delete children before the parent), evaluating an **expression tree** (`3 4 +` is post-order for `3 + 4`), or `rm -r` and `du` on a directory.

> [!tip] Most tree problems are post-order
> "Compute something for every subtree and combine" (height, diameter, balanced check, max path sum) is post-order: recurse into both children, then combine their results at the node. Lesson 7 is full of these.

### Space: the hidden cost

Recursion is not free. Each pending call sits on the call stack, and the deepest the recursion goes is one call per level on the longest root-to-leaf path:

```formula
F_max = h + 1
F_max = ⌊log_2(1000000)⌋ + 1 = 20
F_max = (1000000 − 1) + 1 = 1000000
where
F_max: the most call frames (pending recursive calls) on the call stack at once
h: the height of the tree in edges; a path of h edges has h + 1 nodes, each with its own frame
n: the number of nodes; 1,000,000 in both example lines
log_2(n): the base-2 logarithm of n: the power you raise 2 to in order to get n; log_2(1000000) ≈ 19.93
⌊ ⌋: floor: round down to a whole number
In words: recursive depth-first traversal needs one stack frame per node on the deepest path, so its memory grows with the height, not with the number of nodes.
```

The two example lines are a million-node complete tree (height 19, so 20 frames) and a million-node chain (height n − 1, so a million frames). So depth-first traversal uses O(h + 1) working space, excluding the O(n) output: O(log n) for a balanced tree but **O(n) for a degenerate one**.

CPython commonly starts with a recursion limit of 1,000; query sys.getrecursionlimit() for the actual process. A sufficiently deep chain raises RecursionError, accounting for existing call depth. Raising the limit can create resource risks; an iterative traversal avoids recursive call-depth limits but still needs memory.

## Iterative depth-first traversals

Replace the call stack with an explicit list used as a stack.

### Pre-order

Pop a node, visit it, then push its children. Push the **right child first** so that the left is popped first.

```python
def preorder_iter(root):
    out = []
    stack = [root] if root else []
    while stack:
        node = stack.pop()
        out.append(node.val)
        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)
    return out
```

### In-order

Slide down to the leftmost node, stacking each ancestor on the way. Pop, visit, then repeat the slide from the popped node's right child.

```python
def inorder_iter(root):
    out, stack = [], []
    node = root
    while node or stack:
        while node:            # go left
            stack.append(node)
            node = node.left
        node = stack.pop()     # visit
        out.append(node.val)
        node = node.right      # then right
    return out
```

This pattern is worth memorising: it is also how you build a **BST iterator** that yields the next key on demand. Over a full traversal of n nodes each advance costs O(1) amortised (constant on average, because each node is pushed and popped once in total), and the stack needs O(h + 1) memory for a tree of height h. Initialisation or an individual next call can cost O(h + 1).

### Post-order

Post-order is the awkward one, because a node can only be visited after both children are done. The neat trick: do a pre-order that goes **node, right, left**, then reverse the output. Reversed, that is left, right, node.

```python
def postorder_iter(root):
    out = []
    stack = [root] if root else []
    while stack:
        node = stack.pop()
        out.append(node.val)
        if node.left:
            stack.append(node.left)
        if node.right:
            stack.append(node.right)
    return out[::-1]
```

This uses O(n) memory for the output it reverses, for n nodes. If you need to *act* on nodes in post-order as you go (to free them, say), use the single-stack version that remembers the last node visited, so it can tell whether it is returning from the left or the right subtree.

## Breadth-first: level-order

Level-order visits nodes by depth: the root, then all depth-1 nodes left to right, and so on. It uses a **queue** instead of a stack: first in, first out, so nodes are processed in the order they were discovered.

```python
from collections import deque

def level_order(root):
    if root is None:
        return []
    levels, q = [], deque([root])
    while q:
        level = []
        for _ in range(len(q)):
            node = q.popleft()
            level.append(node.val)
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        levels.append(level)
    return levels

# [['F'], ['B', 'G'],
#  ['A', 'D', 'I'], ['C', 'E', 'H']]
```

Taking `len(q)` at the start of each round processes exactly one level per round. That is the hook for a whole family of problems: right-side view (last of each level), zigzag order, average per level, minimum depth.

> [!warning] Use a deque, not a list
> `list.pop(0)` shifts every remaining element, so it is O(n) in the n items still in the list, and can make BFS quadratic (work growing with n², n times n) on wide trees. `deque.popleft()` is O(1), a fixed cost.

### Space for BFS

The queue can mix the unprocessed part of one level with discovered nodes of the next; its size grows with the tree's **width** (the most nodes on any one level), written O(width). A perfect tree is widest at its last level, which holds just over half of all its nodes:

```formula
W = 2^h = (n + 1) / 2
n = 2^(h+1) − 1
W = (15 + 1) / 2 = 8
where
W: the number of nodes on the last (widest) level of a perfect binary tree
h: the height of the tree in edges; the last level is at depth h
n: the total number of nodes in the perfect tree
2^h: h copies of 2 multiplied together
In words: in a perfect binary tree the bottom level holds (n + 1)/2 nodes, just over half the tree, and BFS's queue fills with all of them.
```

A perfect tree of 15 nodes has 8 leaves; one of 1,048,575 nodes has 524,288. So BFS uses O(n) memory on bushy trees, while DFS needs only O(log n) there. On a degenerate chain it is the other way round: the queue never holds more than one node, but recursive DFS needs O(n) frames. Iterative pre-order can keep only one pending node on a chain.

For n nodes:

| Shape | Recursive DFS stack | BFS queue |
|---|---|---|
| Balanced | O(log n) | O(n) |
| Chain | O(n) | O(1) |

BFS has one big advantage: it reaches shallow nodes first. To find the **minimum depth** of a tree, or the nearest node satisfying a condition, BFS can stop as soon as it finds one, while DFS might explore a huge deep subtree first.

## Advanced aside: Morris traversal

Can you do an in-order traversal with **O(1) extra space**, no stack and no recursion? Yes, if you are allowed to modify the tree temporarily.

Morris traversal (Joseph M. Morris, 1979) uses the empty right pointers of nodes as temporary **threads** back to their in-order successor:

1. If the current node has no left child, visit it and go right.
2. Otherwise, find its in-order predecessor (the rightmost node of its left subtree).
   - If the predecessor's right pointer is empty, point it at the current node (a thread) and go left.
   - If it already points at the current node, we have come back up via the thread: remove it, visit the current node and go right.

```python
def morris_inorder(root):
    out, cur = [], root
    while cur:
        if cur.left is None:
            out.append(cur.val)
            cur = cur.right
            continue
        pred = cur.left
        while (pred.right and
               pred.right is not cur):
            pred = pred.right
        if pred.right is None:
            pred.right = cur   # thread
            cur = cur.left
        else:
            pred.right = None  # unthread
            out.append(cur.val)
            cur = cur.right
    return out
```

Each edge is walked a constant number of times, so it is still **O(n) time** for n nodes. The catch is that the tree is temporarily rewired: it is unsafe if another thread is reading the tree concurrently, and if you stop early (say, on finding a key) you must still finish the walk or the threads stay in place. The O(1) bound excludes the output list: the shown function stores O(n) output. Exceptions or early exits also require cleanup of outstanding threads.

## Key takeaways
- Pre-order (node first) suits copying and serialising; in-order gives sorted keys from a BST; post-order (node last) suits anything that combines subtree results.
- All traversals are O(n) time for n nodes. Recursive DFS needs O(h + 1) frames for height h; BFS needs a queue as large as the widest level. The shown functions also materialise O(n) output.
- Iterative versions avoid the process recursion limit on deep trees; push the right child before the left for pre-order.
- Level-order uses a deque and `len(q)` per round to process one level at a time.
- Morris traversal achieves O(1) working space excluding output by temporarily threading predecessor pointers.

## Further reading
- [Tree traversal — Wikipedia](https://en.wikipedia.org/wiki/Tree_traversal)
- [Threaded binary tree (Morris traversal) — Wikipedia](https://en.wikipedia.org/wiki/Threaded_binary_tree)
- [Breadth-first search — Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)
- [collections.deque — Python docs](https://docs.python.org/3/library/collections.html)
