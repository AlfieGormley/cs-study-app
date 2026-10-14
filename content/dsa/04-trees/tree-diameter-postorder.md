---
id: tree-diameter-postorder
title: Diameter from one post-order pass
level: advanced
minutes: 3
sourceLesson: tree-problems
summary: A longest path can bend below the root.
---

Use the binary Node with val, left and right fields introduced earlier. Assume a finite acyclic tree with no shared nodes or concurrent mutation. Throughout this unit n counts nodes and h is the tree height in edges. Recursive examples are limited by Python call depth; arithmetic has unit cost and hash-table operations have expected constant cost. Each example distinguishes working storage from returned output.

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
> Computing `height(left) + height(right)` separately at every node recomputes heights from scratch, which is O(n²) on a chain of n nodes (about half the square of the node count in descendant visits). Combining both in one post-order pass keeps it O(n).

## Key takeaways
- A longest path can bend below the root.
- Return height to the parent while recording the best two-sided path.
- Avoid recalculating full subtree heights at every node.

## Further reading
- [Tree traversal — Wikipedia](https://en.wikipedia.org/wiki/Tree_traversal)
