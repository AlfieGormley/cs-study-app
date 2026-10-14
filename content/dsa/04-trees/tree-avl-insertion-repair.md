---
id: tree-avl-insertion-repair
title: AVL insertion and single or double repair
level: intermediate
minutes: 4
sourceLesson: tree-balanced
summary: Repair LL and RR cases with a single rotation.
---

Start with the distinct-key BST ordering from the previous units. A rotation must keep the same sorted in-order sequence while changing local links. Here n counts stored keys and h measures real-node height in edges; empty subtrees have height minus one unless a NIL-path convention is explicitly given. Height bounds assume constant-cost key comparisons, rather than measuring application latency.

### Insert and rebalance

Insert as in a plain BST, then walk back up the path updating heights. At the first node whose balance factor becomes +2 or −2, one of four cases applies, named after the path from that node down to where the new key went.

| Case | Shape | Fix |
|---|---|---|
| LL | left child left-heavy | rotate right |
| RR | right child right-heavy | rotate left |
| LR | left child right-heavy | left at child, then right |
| RL | right child left-heavy | right at child, then left |

The LR case is the one people miss. Insert 30, 10, 20:

```
  30           30           20
  /            /           /  \
10    -->    20    -->   10    30
  \          /
   20      10
 (LR)   rotate left   rotate right
        at 10         at 30
```

A single right rotation at 30 would just move the zig-zag to the other side; you have to straighten it first.

The insertion function below uses rotate_right from the rotation unit; the Node, height helpers and rotate_left needed to run it are provided just after it. Together those definitions form the complete distinct-key insertion example.

```python
def insert(n, key):
    if n is None:
        return Node(key)
    if key < n.key:
        n.left = insert(n.left, key)
    elif key > n.key:
        n.right = insert(n.right, key)
    else:
        return n
    # Child updates change the cached
    # height.
    fix(n)                     # height
    b = bf(n)
    if b > 1:                  # left-heavy
        if bf(n.left) < 0:     # LR case
            n.left = rotate_left(n.left)
        return rotate_right(n)
    if b < -1:                 # right-heavy
        if bf(n.right) > 0:    # RL case
            n.right = rotate_right(n.right)
        return rotate_left(n)
    return n
```

The following helpers complete the example. Keys are distinct comparable values; duplicate insertions leave the tree unchanged.

```python
class Node:
    def __init__(self, key):
        self.key = key
        self.left = self.right = None
        self.height = 0

def ht(n):
    return -1 if n is None else n.height

def fix(n):
    n.height = 1 + max(ht(n.left),
                       ht(n.right))

def bf(n):
    return ht(n.left) - ht(n.right)

def rotate_left(x):
    y = x.right
    # Transfer the middle subtree
    # symmetrically.
    x.right = y.left
    y.left = x
    fix(x)
    fix(y)
    return y
```

Inserting 1 to 7 in order into this AVL tree gives the perfect tree with 4 at the root, where a plain BST would give a chain.

After an insert that creates imbalance, one rebalancing step (one single or one double rotation) restores balance, because it returns the subtree to the height it had before the insert, so no ancestor needs fixing. Deletion is worse: a rotation can shrink a subtree's height, unbalancing its parent in turn, so a delete in a tree of n keys may need **O(log n) rotations**, up to one per level of the path.

## Key takeaways
- Repair LL and RR cases with a single rotation.
- Straighten a zig-zag before the second rotation in LR and RL cases.
- Insert and delete differ in whether height changes propagate.

## Further reading
- [AVL tree — Wikipedia](https://en.wikipedia.org/wiki/AVL_tree)
- [AVL tree visualisation — USF](https://www.cs.usfca.edu/~galles/visualization/AVLtree.html)
