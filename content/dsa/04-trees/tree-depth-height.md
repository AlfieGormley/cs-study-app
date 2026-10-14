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

Height has a neat recursive definition: the height of a node is one more than the taller of its children's heights, and an empty subtree has height −1 so that a leaf comes out as 0.

```formula
h(x) = 1 + max(h(x_L), h(x_R))
h(∅) = −1
h(E) = 1 + max(−1, −1) = 0
h(F) = 1 + max(h(H), −1) = 1
h(B) = 1 + max(h(E), h(F)) = 2
where
h(x): the height of node x: the number of edges on the longest path from x down to a leaf
x: any node of the tree
x_L: the left child of x (or, in a tree with more children, any one child: take the max over all of them)
x_R: the right child of x
∅: an empty subtree (a missing child, None in Python)
max: the larger of the values listed
E, F, H, B: the nodes with those labels in the tree-structure unit’s A–H diagram; E and H are leaves, so h(H) = 0
In words: a node's height is one more than its tallest child's height, and starting empty subtrees at −1 makes every leaf height 0.
```

That gives B height 2, matching the count by eye. For a finite acyclic binary tree with no shared children, this is the canonical recursive tree function. It visits each of the n nodes once, so it takes O(n) time, and it needs O(h + 1) recursive frames, where h is the tree's height (the exact maximum for a nonempty tree is its edge-counted height plus two: one frame per path node and a final temporary empty-child call). Deep trees can hit the runtime's recursion limit.

The following binary Node stores each child reference explicitly. The sample builds a four-node tree; the height function below accepts this representation and returns two for that sample root. It does not implement general many-child height.

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
