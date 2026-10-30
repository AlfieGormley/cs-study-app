---
id: tree-depth-height
title: Depth, height and recursive counting
level: basic
minutes: 4
sourceLesson: tree-basics
summary: Depth looks upwards to the root; height looks down to the deepest leaf.
---

Use the rooted-tree vocabulary from the earlier unit. The linked examples below assume a finite acyclic tree without shared child nodes. Count height and depth in edges, not nodes. A path ends at a leaf only when that node has no children. When an example uses n, it means the number of stored nodes.

## Vocabulary

| Term | Meaning (in the tree-structure unit’s A–H example) |
|---|---|
| Child / parent | B is a child of A; A is B's parent |
| Siblings | B, C and D share a parent |
| Leaf | A node with no children: E, H, C, G |
| Internal node | Has at least one child: A, B, F, D |
| Subtree | A node plus all its descendants |
| Ancestor | A, B and F are ancestors of H |
| Degree | Number of children (A has 3) |

### Depth versus height

These two are easy to mix up because they both count edges, but they look in opposite directions.

- The **node depth** of a node is the number of edges from the **root down to it**. The root has depth 0; H has depth 3.
- The **node height** of a node is the number of edges on the **longest path down to a leaf**. Leaves have height 0; B has height 2; A has height 3.
- The **height of the tree** is the height of its root, which equals the maximum depth of any node.

> [!warning] Conventions vary
> Some books count nodes rather than edges, so a single node has height 1 instead of 0. This module counts **edges**: a one-node tree has height 0 and an empty tree has height −1. Always check which convention a problem uses before you answer "what is the height?".

> [!analogy] Real-world analogy: generations in a family tree
> Pick one family's founding ancestor. Your generation number is how many generations you sit below that ancestor. Separately, ask how many generations of descendants you have below you: none if you have no children, three if you have a great-grandchild.
>
> **How it maps:** the founding ancestor is the root. Your generation number is your depth, counted from the top down to you. The number of generations below you, along your longest line of descendants, is your height. A childless person is a leaf, with height 0.
>
> **Where it stops:** real people have two parents, so a full ancestry chart is not a tree at all; this picture follows only one line of descent. Families also often number the founder as "generation 1", which is the node-counting convention this module avoids.

### Computing height recursively

Height has a neat recursive definition: the height of a node is one more than the taller of its children's heights, and an empty subtree has height −1 so that a leaf comes out as 0. In the A–H tree, E is a leaf (height 0), F's only child H is a leaf, so F has height 1, and B is one more than the taller of E and F: height 2, matching the count by eye.

The recursion has to know both children's heights before it can answer for their parent, so it naturally works bottom-up. It visits each of the n nodes once, so it takes O(n) time. Its call stack holds one frame for each node on the longest root-to-leaf path, plus one for the final call on an empty child. A balanced tree keeps that shallow, but a degenerate chain of thousands of nodes can hit the runtime's recursion limit (CPython's default limit is 1,000 frames).

The following binary Node stores each child reference explicitly. The sample builds a four-node tree; the height function below accepts this representation and returns 2 for that sample root. For a node with any number of children, take the maximum over all of them instead of just two.

```python
class Node:
    def __init__(self, val, left=None,
                 right=None):
        self.val = val
        # Keep left/right
        # positions distinct.
        self.left = left
        self.right = right

#      1
#     / \
#    2   3
#   /
#  4
root = Node(1, Node(2, Node(4)), Node(3))
```

```python
def height(node):
    if node is None:
        return -1          # empty tree
    # Combine both child heights.
    return 1 + max(height(node.left),
                   height(node.right))
```

## Key takeaways
- Depth looks upwards to the root; height looks down to the deepest leaf.
- This module counts edges: leaves have height zero and empty trees height minus one.
- Recursive height combines children before their parent.

## Further reading
- [Tree (data structure) — Wikipedia](https://en.wikipedia.org/wiki/Tree_(data_structure))
- [Binary tree — Wikipedia](https://en.wikipedia.org/wiki/Binary_tree)
