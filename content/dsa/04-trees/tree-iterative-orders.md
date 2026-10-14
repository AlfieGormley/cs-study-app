---
id: tree-iterative-orders
title: Explicit stacks for depth-first traversal
level: basic
minutes: 3
sourceLesson: tree-traversals
summary: A LIFO stack reverses the order in which children are pushed.
---

Use the binary Node representation introduced earlier: each node has a value and optional left and right children. Assume finite acyclic trees without shared nodes or concurrent mutation. Here n counts nodes and h is the root height in edges. Constant-cost processing at each visited node is assumed; returned output is separate from working memory.

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
        # LIFO: right waits for left.
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
        # LIFO visits right before left.
        if node.right:
            stack.append(node.right)
    # Reverse node-right-left into
    # postorder.
    return out[::-1]
```

This uses O(n) memory for the output it reverses, for n nodes. If you need to *act* on nodes in post-order as you go (to free them, say), use the single-stack version that remembers the last node visited, so it can tell whether it is returning from the left or the right subtree.

## Key takeaways
- A LIFO stack reverses the order in which children are pushed.
- In-order keeps pending ancestors until their left side is finished.
- Reversing a right-first pre-order gives post-order output, with output storage.

## Further reading
- [Tree traversal — Wikipedia](https://en.wikipedia.org/wiki/Tree_traversal)
