---
id: tree-morris-threads
title: Morris traversal and temporary threads
level: basic
minutes: 3
sourceLesson: tree-traversals
summary: Temporary predecessor links replace an explicit traversal stack.
---

Use the binary Node representation introduced earlier: each node has a value and optional left and right children. Assume finite acyclic trees without shared nodes or concurrent mutation. Here n counts nodes and h is the root height in edges. Constant-cost processing at each visited node is assumed; returned output is separate from working memory.

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
            # Save a route
            # back to this
            # ancestor.
            pred.right = cur   # thread
            cur = cur.left
        else:
            # Restore the
            # original empty
            # link.
            pred.right = None  # unthread
            out.append(cur.val)
            cur = cur.right
    return out
```

Each edge is walked a constant number of times, so it is still **O(n) time** for n nodes. The catch is that the tree is temporarily rewired: it is unsafe if another thread is reading the tree concurrently, and if you stop early (say, on finding a key) you must still finish the walk or the threads stay in place. The O(1) bound excludes the output list: the shown function stores O(n) output. Exceptions or early exits also require cleanup of outstanding threads.

## Key takeaways
- Temporary predecessor links replace an explicit traversal stack.
- Remove each thread on the second encounter.
- Constant working space excludes output and requires safe cleanup.

## Further reading
- [Threaded binary tree (Morris traversal) — Wikipedia](https://en.wikipedia.org/wiki/Threaded_binary_tree)
