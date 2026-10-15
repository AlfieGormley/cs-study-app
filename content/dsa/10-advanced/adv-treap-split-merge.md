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

For distinct keys and priorities, there is exactly one tree satisfying both rules. And it is the same tree you would get by inserting the keys in decreasing priority order into a plain BST. Since priorities are random, that is a random insertion order, and a BST built from random insertions has expected depth O(log n), where n is the number of keys:

```formula
H_n = Σ (1 / j)   for 1 ≤ j ≤ n
D = 2(1 + 1 / n)H_n − 4
D ≈ 2 ln(n) − 2.85
D ≈ 2 ln(5000) − 2.85 ≈ 17.0 − 2.85 ≈ 14
2 ln(n) ≈ 1.39 × log_2(n)
where
D: the expected depth of a uniformly selected existing node, in edges from the root, for a random permutation of n distinct keys
H_n: the n-th harmonic number, the sum of reciprocals from 1 through n
j: the summation index, a whole number from 1 to n
Σ: add the indicated terms over the stated summation bounds
≤: is at most
n: the number of keys, 5,000 in the second line
ln(n): the natural logarithm of n, to base e ≈ 2.718
log_2(n): the base-2 logarithm of n; 2 ln(n) equals about 1.39 × log_2(n) because ln(2) ≈ 0.693
≈: approximately equal to
In words: the average depth grows like 2 ln(n), less a small constant of about 2.85, so for large n a randomly built tree is only about 39 % deeper on average than a perfectly balanced one.
```

The average depth is about 14 for 5,000 keys (the leading term 2 ln(n) alone gives 17); the deepest node is somewhat deeper, but still logarithmic in expectation.

So the treap's shape no longer depends on the order keys actually arrived. Inserting 5,000 sorted keys into a plain BST gives a chain of height 4,999 edges; a treap with independent random priorities has expected logarithmic height, though a linear-height outcome remains possible.

### Split and merge

The cleanest treap implementations use two operations:

- `split(t, key)` returns two treaps: keys below `key`, and the rest.
- `merge(a, b)` joins two treaps when every key in a is smaller than every key in b. The root is whichever root has the higher priority.

Assume distinct keys and independent priorities; `insert` below requires a key not already present. `TNode` generates a random priority, with a counter to break rare finite-precision ties. The ideal analysis assumes independent continuous priorities; this finite implementation approximates that model.

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
- [Skip list — Wikipedia](https://en.wikipedia.org/wiki/Skip_list)
- [Treap — Wikipedia](https://en.wikipedia.org/wiki/Treap)
- [Treap (Cartesian tree) — cp-algorithms](https://cp-algorithms.com/data_structures/treap.html)
- [Reservoir sampling — Wikipedia](https://en.wikipedia.org/wiki/Reservoir_sampling)
- [Fisher–Yates shuffle — Wikipedia](https://en.wikipedia.org/wiki/Fisher%E2%80%93Yates_shuffle)
