---
id: fp-tree-paths
title: Persistent trees and path copying
level: advanced
minutes: 4
sourceLesson: fp-persistent-data
summary: Path copying rebuilds the root-to-change path and shares other branches.
---

Path copying rebuilds the root-to-change path and shares other branches. This unit develops that mechanism using the earlier units as prerequisites.

## Trees: path copying

That rule gives the key technique for trees. To change a leaf of a tree, copy **only the nodes on the path from the root to it**. Every subtree off that path is reused by pointer.

Inserting 65 into a binary search tree:

```
version 1:
        50
       /  \
     30    70
    /  \   / \
   20  40 60  80

version 2 (after inserting 65):
        50'
       /  \
    (30)   70'
           / \
         60'  (80)
           \
            65
```

Nodes marked `'` are new copies, and 65 is the new leaf. `(30)` (with its whole subtree) and `(80)` are the very same objects as in version 1, reached by pointer. Here's the whole thing in Python:

```python
# Rebuild only ancestors of a changed key.
from typing import NamedTuple

class Node(NamedTuple):
    key: int
    left: "Node | None"
    right: "Node | None"

def insert(t, k):
    if t is None:
        return Node(k, None, None)
    if k < t.key:
        return t._replace(
            left=insert(t.left, k))
    if k > t.key:
        return t._replace(
            right=insert(t.right, k))
    return t
```

`_replace` builds a new node with one field changed. The new version shares the whole left subtree:

```python
# Unchanged branches retain identity.
v2 = insert(v1, 65)
v2.left is v1.left        # True
v2.right.right is v1.right.right  # True
```

For a **balanced tree** of n keys, a balance invariant bounds path length logarithmically; it need not put every leaf at nearly the same depth. A nearly complete tree gives the following approximate count; a merely balanced tree can have a different constant factor:

```formula
h ≈ log_2(n)
h ≈ log_2(1000000) ≈ 19.9 ≈ 20
where
h: the height of the tree: the number of nodes on a path from the root to a leaf, and so the number of nodes an insert copies
n: the number of keys in the tree
log_2(n): the base-2 logarithm of n: how many times you can halve n before reaching 1 (2^20 = 1,048,576)
≈: approximately equal to
In words: each level of a balanced binary tree doubles how many keys it can hold, so a million keys needs only about 20 levels.
```

With a million keys that's about 20 new nodes per insert, instead of a million. Both versions remain fully usable, and the extra memory is O(log n) per update: it grows with the logarithm of n, not with n itself. The figure only holds while the tree stays balanced; a tree built by inserting sorted keys without rebalancing degenerates into a list with height n.

This is how Haskell's `Data.Map` and `Data.Set` (size-balanced binary trees), OCaml's `Map`, and Scala's `TreeMap` work. Rebalancing (rotations in a red-black or AVL tree) only touches nodes near the path, so it stays O(log n).

> [!example] Git does this too
> A Git commit points to a tree object for the root directory, which points to trees and blobs for its contents. Change one file and Git writes a new blob, new trees for each directory on the path up to the root, and a new commit. Every unchanged directory is shared with the previous commit by hash. That's path copying on your file system.

## Key takeaways
- Path copying rebuilds the root-to-change path and shares other branches.
- Logarithmic bounds require a balanced tree.

## Further reading
- [Okasaki: Purely Functional Data Structures](https://www.cs.cmu.edu/~rwh/students/okasaki.pdf)
- [Haskell Containers](https://hackage.haskell.org/package/containers/docs/Data-Map-Lazy.html)
- [Scala Collections](https://docs.scala-lang.org/overviews/collections-2.13/concrete-immutable-collection-classes.html)
- [Git](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects)
