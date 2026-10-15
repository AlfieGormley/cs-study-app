---
id: adv-persistent-path-copying
title: Keeping versions with path copying
level: advanced
minutes: 3
summary: Copy the changed path and share untouched subtrees.
sourceLesson: adv-sparse-tables
---

Here n is the array length, tree size or text length specified in the section. Big-O costs assume fixed-size summaries and constant-time word operations.

## Persistent data structures

Ordinary structures are **ephemeral**: an update destroys the old version. A **persistent structure** keeps old versions usable. A **partially persistent** structure lets you read every version but update only the newest; a **fully persistent** one lets you update them too, forming a tree of versions.

This sounds expensive, but most of each version is shared with the previous one. Shared nodes must remain immutable: changing one in place corrupts every version that still references it.

### Path copying

In a tree, an update only changes nodes on one root-to-leaf path. Copy just those nodes, and point the copies at the unchanged subtrees of the old version:

```python
class T:
    __slots__ = ("key", "left", "right")
    def __init__(self, key, left=None,
                 right=None):
        self.key = key
        self.left = left
        self.right = right

def insert(t, key):
    # returns a new root; t is unchanged
    if t is None:
        return T(key)
    if key < t.key:
        # Copy this path; share the right
        # branch.
        return T(t.key, insert(t.left, key),
                 t.right)
    if key > t.key:
        # Copy this path; share the left
        # branch.
        return T(t.key, t.left,
                 insert(t.right, key))
    return t  # already present
```

Inserting 45 into the tree with keys 20, 30, 40, 50 and 70:

```
v1:     50          v2:     50'
       /  \                /  \
     30    70            30'   70 (shared)
    /  \                /  \
  20    40      (shared)20   40'
                               \
                                45 (new)
```

v2 created four nodes (50', 30', 40' and 45); everything else is shared. Both roots remain valid. In a balanced tree, the copied root-to-leaf route is only as long as the tree is tall:

```formula
p ≈ log_2(n)
p ≈ log_2(10^6) ≈ 20
where
p: the number of nodes copied by one insert (the root-to-leaf path)
n: the number of keys in the balanced tree
log_2(n): the base-2 logarithm of n: the power you raise 2 to in order to get n
≈: approximately equal to
In words: one insert copies about as many nodes as the tree has levels, which grows with the logarithm of the number of keys.
```

So each update costs O(log n) time and memory: about 20 new nodes per insertion into a million-key tree, instead of copying a million. This only holds if the tree stays balanced; a badly unbalanced tree would copy a path as long as the whole chain.

Other techniques:

- **Fat nodes**: each field stores a list of (version, value) pairs. Reads binary-search for the version. Good for partial persistence.
- **Driscoll, Sarnak, Sleator and Tarjan (1989)** showed how to make linked structures with a constant number of fields per node and bounded in-degree persistent with O(1) amortised extra space per primitive field-update step. A whole operation may contain many such steps.

## Key takeaways

- Copy the changed path and share untouched subtrees.
- Logarithmic update overhead requires a balanced tree and immutable shared nodes.

## Further reading
- [Sparse Table — cp-algorithms](https://cp-algorithms.com/data_structures/sparse-table.html)
- [Range minimum query — Wikipedia](https://en.wikipedia.org/wiki/Range_minimum_query)
- [Persistent data structure — Wikipedia](https://en.wikipedia.org/wiki/Persistent_data_structure)
- [Rope (data structure) — Wikipedia](https://en.wikipedia.org/wiki/Rope_(data_structure))
- [Text Buffer Reimplementation — VS Code blog](https://code.visualstudio.com/blogs/2018/03/23/text-buffer-reimplementation)
- [Making Data Structures Persistent](https://www.cs.cmu.edu/~sleator/papers/making-data-structures-persistent.pdf)
