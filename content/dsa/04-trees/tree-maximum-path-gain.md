---
id: tree-maximum-path-gain
title: Maximum path sums with one-sided gains
level: advanced
minutes: 3
sourceLesson: tree-problems
summary: Clamp a negative extension to zero rather than taking it.
---

Use the binary Node with val, left and right fields introduced earlier. Assume a finite acyclic tree with no shared nodes or concurrent mutation. Throughout this unit n counts nodes and h is the tree height in edges. Recursive examples are limited by Python call depth; arithmetic has unit cost and hash-table operations have expected constant cost. Each example distinguishes working storage from returned output.

## Maximum path sum: post-order with clamping

"Largest sum over any path" (values may be negative). At each node, a path can bend here using the best **downward gain** from each side, but it can only pass **one** side up to the parent, because a path cannot fork. Negative gains are clamped to 0: if extending down a side would lower the sum, just don't extend that way.

So each node does two things:

- **Records a candidate answer**: its own value plus both clamped gains, the best path that bends here.
- **Returns its gain** to its parent: its own value plus the *better* of the two clamped gains, the best path that starts here and goes down one side.

For example, a node of value 2 whose children are leaves of value 1 and 3 records a bend of 2 + 1 + 3 = 6, and offers its parent a one-sided gain of 2 + 3 = 5. If the 1 were −1 instead, the left gain would be clamped to 0 and the bend would be 2 + 0 + 3 = 5.

```python
def max_path_sum(root):
    if root is None:
        raise ValueError("empty tree")
    best = float('-inf')
    def gain(node):
        nonlocal best
        if node is None:
            return 0
        # Ignore extensions that
        # reduce the sum.
        l = max(gain(node.left), 0)
        r = max(gain(node.right), 0)
        best = max(best, node.val + l + r)
        return node.val + max(l, r)
    gain(root)
    return best
```

Initialise `best` to minus infinity (`float('-inf')`, smaller than any number), not 0: in a tree of all-negative values the answer is the largest single node, which is negative. Same shape as diameter: return the one-sided gain, record the two-sided best.

## Key takeaways
- Clamp a negative extension to zero rather than taking it.
- Pass only one downward side to a parent because a path cannot fork.
- Initialise the global best below all values to handle all-negative trees.

## Further reading
- [Tree traversal — Wikipedia](https://en.wikipedia.org/wiki/Tree_traversal)
