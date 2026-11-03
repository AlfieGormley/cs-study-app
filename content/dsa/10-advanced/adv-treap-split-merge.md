---
id: adv-treap-split-merge
title: Treaps, random priorities, split and merge
level: advanced
minutes: 5
summary: A treap keeps BST order on keys and heap order on priorities.
sourceLesson: adv-randomised-structures
---

Here n is the number of keys or stream items, and k is the requested sample size when sampling. Random draws are assumed independent and uniform under the stated model.

## Treaps

A **treap** is a binary search tree where each node also has a random **priority**, and the tree is a **heap** on priorities: every parent's priority beats its children's. (The name is tree + heap.)

```
      (50, .91)
      /       \
 (20, .74)   (70, .80)
    \           /
  (30, .12)  (60, .33)

BST order on keys, max-heap on priorities
```

For distinct keys and priorities, exactly one tree satisfies both rules: the highest-priority key must be the root, and its key separates the left and right subtrees. Applying the same argument recursively fixes the whole tree.

This is also the tree obtained by inserting keys into a plain BST in decreasing priority order. Independent random priorities therefore give the shape of a random insertion order, even when the actual keys arrive sorted. Expected height and operation cost are O(log n) for n keys. A rare linear-height outcome remains possible; this is not a deterministic height bound.

### Split and merge

The cleanest treap implementations use two operations:

- `split(t, key)` returns two treaps: keys below `key`, and the rest.
- `merge(a, b)` joins two treaps when every key in a is smaller than every key in b. The root is whichever root has the higher priority.

Assume distinct keys and independent priorities; `insert` below requires a key not already present. `TNode` generates a random priority, with a counter to break rare ties between representable priorities. The ideal analysis assumes independent continuous priorities; this finite implementation approximates that model.

The example uses `import random`, introduced with the skip-list implementation; run that import when using this excerpt separately.

```python
from itertools import count

_serial = count()

class TNode:
    def __init__(self, key):
        self.key = key
        self.pri = (random.random(),
                    next(_serial))
        self.left = self.right = None

def split(t, key):
    # returns (keys < key, keys >= key)
    if t is None:
        return None, None
    if t.key < key:
        l, r = split(t.right, key)
        # Keep below-key nodes on the left
        # side.
        t.right = l
        return t, r
    l, r = split(t.left, key)
    t.left = r
    return l, t

def merge(a, b):
    # all keys in a < all keys in b
    if a is None or b is None:
        return a or b
    if a.pri > b.pri:
        # The larger priority stays above
        # both.
        a.right = merge(a.right, b)
        return a
    # Attach under the root with the
    # larger treap priority.
    b.left = merge(a, b.left)
    return b

def insert(t, key):
    l, r = split(t, key)
    return merge(merge(l, TNode(key)), r)
```

The recursive implementations can hit Python’s recursion limit on a sufficiently tall outcome; expected balance is not a hard stack bound.

Each runs in expected time proportional to the tree’s depth, which is O(log n) for n keys. Delete is two splits (cutting out the key) and one merge.

Split and merge are what make treaps popular in competitive programming. An **implicit treap** keys nodes by position (subtree sizes) instead of by value, giving a sequence that supports insert at index, delete range, moving a sequence fragment and reversing a range, with expected O(log n) tree work for a sequence of n items when properly augmented; reversal needs lazy tags. Inserting m fresh items costs at least O(m), and deleting nodes can add reclamation work. That is the same job a rope does, which the next lesson covers.

> [!note] Tree vs list
> Skip lists and treaps solve the same problem with the same expected bounds. Skip lists are simpler to make concurrent. Treaps are a real BST, so augmenting nodes (subtree sums, sizes) and split/merge come naturally.

## Key takeaways

- A treap keeps BST order on keys and heap order on priorities.
- Merge requires all left-treap keys to precede every right-treap key.

## Further reading
- [Treaps — Open Data Structures](https://opendatastructures.org/ods-python/7_2_Treap_Randomized_Binary.html)
