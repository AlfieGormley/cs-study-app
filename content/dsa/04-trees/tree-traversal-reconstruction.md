---
id: tree-traversal-reconstruction
title: Reconstructing a tree from traversal pairs
level: advanced
minutes: 3
sourceLesson: tree-problems
summary: In-order splits the values into left and right subtrees once the root is known.
---

Use the binary Node with val, left and right fields introduced earlier. Assume a finite acyclic tree with no shared nodes or concurrent mutation. Throughout this unit n counts nodes and h is the tree height in edges. Recursive examples are limited by Python call depth; arithmetic has unit cost and hash-table operations have expected constant cost. Each example distinguishes working storage from returned output.

## Constructing a tree from traversals

Given traversals **without** null markers, when can you rebuild the tree? With **distinct** values:

| Given | Unique tree? |
|---|---|
| Pre-order + in-order | Yes |
| Post-order + in-order | Yes |
| Pre-order + post-order | Only if full |
| Pre-order alone | No (but yes for a BST) |

In-order is the key: once you know the root, its position in the in-order sequence tells you exactly which values are in the left and right subtrees. Pre-order tells you the root (its first element), then the left subtree's root, and so on.

```
preorder: 3 | 9 | 20 15 7
inorder:  9 | 3 | 15 20 7
          L  root   R
```

```python
def build_tree(preorder, inorder):
    if len(preorder) != len(inorder):
        raise ValueError("length mismatch")
    pos = {v: i for i, v
           in enumerate(inorder)}
    if len(pos) != len(inorder):
        raise ValueError("duplicate values")
    if set(preorder) != set(inorder):
        raise ValueError("values differ")
    it = iter(preorder)
    def build(lo, hi):     # inorder[lo:hi]
        if lo >= hi:
            return None
        node = Node(next(it))
        mid = pos[node.val]
        if not lo <= mid < hi:
            raise ValueError("bad order")
        # Preorder lists left before right.
        node.left = build(lo, mid)
        node.right = build(mid + 1, hi)
        return node
    return build(0, len(inorder))
```

For distinct hashable values with consistent equality, the dictionary gives expected O(1) index lookup. For n values, the build takes expected O(n) time and O(n) auxiliary dictionary/set space plus the returned nodes; invalid traversal pairs raise an error. The left subtree must be built before the right because that is the order pre-order lists them.

Pre-order and post-order alone are ambiguous whenever a node has a single child: `1 → left 2` and `1 → right 2` both give pre-order `1 2` and post-order `2 1`. And a BST *can* be rebuilt from pre-order alone, because sorting the n values supplies its in-order, at O(n log n) comparison cost, where n counts keys; a bounds-based reconstruction can avoid sorting.

## Key takeaways
- In-order splits the values into left and right subtrees once the root is known.
- Distinct values and a value-to-position map enable linear expected work.
- Pre-order and post-order leave one-child directions ambiguous in general.

## Further reading
- [Tree traversal — Wikipedia](https://en.wikipedia.org/wiki/Tree_traversal)
