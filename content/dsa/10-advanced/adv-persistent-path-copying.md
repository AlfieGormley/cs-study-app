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

v2 creates four nodes: the copies of 50, 30 and 40, plus the new leaf 45. Both roots remain valid, and every subtree away from the changed path is shared.

In a balanced tree the path is logarithmic, giving O(log n) extra time and memory for an update to n keys. The teaching BST above does not balance itself: sorted insertions can create a chain and require linear copying. A production balanced persistent tree must also copy any nodes changed by rebalancing.

> [!analogy] Real-world analogy: Revised binders
> To revise one page, keep the old binder and create a new contents path pointing to the replacement, reusing unchanged sections.
>
> **How it maps:** Each saved root identifies a version; copied ancestors point towards the changed page, and untouched subtrees remain shared.
>
> **Where it stops:** Shared pages must be immutable. Keeping old binders also keeps their referenced pages alive, so history still consumes memory.

Other techniques:

- **Fat nodes**: each field stores a list of (version, value) pairs. Reads binary-search for the version. Good for partial persistence.
- **Driscoll, Sarnak, Sleator and Tarjan (1989)** showed how to make linked structures with a constant number of fields per node and bounded in-degree persistent with O(1) amortised extra space per primitive field-update step. A whole operation may contain many such steps.

## Key takeaways

- Copy the changed path and share untouched subtrees.
- Logarithmic update overhead requires a balanced tree and immutable shared nodes.

## Further reading
- [Making Data Structures Persistent — Driscoll, Sarnak, Sleator and Tarjan](https://www.cs.cmu.edu/~sleator/papers/making-data-structures-persistent.pdf)
- [Clojure persistent data structures](https://clojure.org/reference/data_structures)
