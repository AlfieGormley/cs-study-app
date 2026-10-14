---
id: tree-maximum-path-gain
title: Maximum path sums with one-sided gains
level: advanced
minutes: 3
sourceLesson: tree-problems
summary: Clamp a negative extension to zero rather than taking it.
---

Use the binary Node with val, left and right fields introduced earlier. Assume a finite acyclic tree with no shared nodes or concurrent mutation. Throughout this unit n counts nodes and h is the tree height in edges. Recursive examples are limited by Python call depth; arithmetic has unit cost and hash-table operations have expected constant cost. Each example distinguishes working storage from returned output.

### Maximum path sum: post-order with clamping

"Largest sum over any path" (values may be negative). At each node, a path can bend here using the best **downward gain** from each side, but it can only pass **one** side up to the parent, because a path cannot fork. Negative gains are clamped to 0 (just don't extend that way).

```formula
g(x) = v(x) + max(G_L, G_R)
G_L = max(g(x_L), 0)
G_R = max(g(x_R), 0)
g(∅) = 0
B(x) = v(x) + G_L + G_R
B(x) = 2 + 1 + 3 = 6
g(x) = 2 + 3 = 5
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
∅: an empty child; its gain is zero, allowing the path to stop at its parent
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
