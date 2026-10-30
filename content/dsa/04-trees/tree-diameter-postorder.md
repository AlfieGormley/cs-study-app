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

> [!analogy] Real-world analogy: the longest walk on a branching trail
> A park's trails branch out from a car park and never loop. The longest walk between any two trail ends usually bends at some junction deep in the park, running out to the far end of one branch and the far end of another. It need not pass the car park at all.
>
> **How it maps:** junctions and trail ends are nodes, trail sections are edges and the car park is the root. The longest walk is the diameter, and the junction where it turns is the path's highest node.
>
> **Where it stops:** real trails can join up into loops, giving several routes between two points. In a tree there is exactly one path between any two nodes, which is why measuring one bend per node is enough.

Every path has a single highest node where it bends. At that node it goes down one edge into each subtree and then as deep as that subtree allows. So the best path bending at a node is the two subtree heights added together, plus the two edges into them. At node 2 above, both subtrees have height 2, giving the 6-edge path; at a leaf such as 5, both sides are empty (height −1), giving 0. The diameter is the largest of these values over all nodes, so compute heights in post-order and track the best bend seen:

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

In the code, `hl + hr + 2` is the path bending at the current node, and returning −1 for None makes a leaf contribute 0 edges, as it should. This is the archetype of "return one thing, track another": the function *returns* the height (useful to the parent) but *records* the diameter (useful only globally).

> [!warning] The O(n²) version
> Computing `height(left) + height(right)` separately at every node recomputes heights from scratch, which is O(n²) on a chain of n nodes (about half the square of the node count in descendant visits). Combining both in one post-order pass keeps it O(n).

## Key takeaways
- A longest path can bend below the root.
- Return height to the parent while recording the best two-sided path.
- Avoid recalculating full subtree heights at every node.

## Further reading
- [Tree traversal — Wikipedia](https://en.wikipedia.org/wiki/Tree_traversal)
