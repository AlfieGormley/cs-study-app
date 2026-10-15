---
id: adv-rope-weighted-indexing
title: Indexing text with weighted ropes
level: advanced
minutes: 2
summary: Rope leaves hold chunks; internal weights count left-subtree characters.
sourceLesson: adv-sparse-tables
---

Here n is the array length, tree size or text length specified in the section. Big-O costs assume fixed-size summaries and constant-time word operations.

## Ropes

Inserting into a single flat text buffer can copy or shift a large part of a 100 MB document. The amount depends on the representation and edit position. A **rope** (Boehm, Atkinson and Plass, 1995) stores the text as a binary tree whose leaves hold short string chunks. Each internal node stores a **rope weight**: the total length of its left subtree.

```
            (9)
          /     \
       (6)       (2)
      /   \     /   \
 "Hello_" "my_" "na" "me_is_Simon"

text: Hello_my_name_is_Simon
```

### Indexing

To find character i, compare it with the weight: go left if smaller, otherwise subtract the weight and go right.

```python
class Leaf:
    def __init__(self, s):
        self.s = s
        self.length = len(s)

class Concat:
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.weight = left.length
        self.length = (left.length
                       + right.length)

def char_at(node, i):
    if not 0 <= i < node.length:
        raise IndexError(i)
    while isinstance(node, Concat):
        if i < node.weight:
            node = node.left
        else:
            # Skip all characters in the
            # left branch.
            i -= node.weight
            node = node.right
    return node.s[i]
```

Tracing `char_at(root, 10)` on the rope above:

```formula
i = 10,   w_root = 9
i ≥ w_root,   so i = 10 − 9 = 1
i = 1 < w_right = 2
c = "na"[1] = "a"
where
i: the index of the wanted character, counting from 0 within the current subtree
w_root: the root's weight: the length of its left subtree, 6 + 3 = 9 characters
w_right: the weight of the root's right child: the length of "na", 2 characters
c: the character found
≥: is at least
<: is less than
In words: at the root the index is not below the weight, so go right and subtract the 9 skipped characters; at the next node 1 is below the weight 2, so go left to the leaf "na", whose character 1 is "a".
```

Character 10 of `Hello_my_name_is_Simon` is indeed `a`. The cost is one step per level, so a balanced rope finds any character in O(log n) steps for n characters.

## Key takeaways

- Rope leaves hold chunks; internal weights count left-subtree characters.
- A right descent subtracts the skipped left-subtree length from the index.

## Further reading
- [Sparse Table — cp-algorithms](https://cp-algorithms.com/data_structures/sparse-table.html)
- [Range minimum query — Wikipedia](https://en.wikipedia.org/wiki/Range_minimum_query)
- [Persistent data structure — Wikipedia](https://en.wikipedia.org/wiki/Persistent_data_structure)
- [Rope (data structure) — Wikipedia](https://en.wikipedia.org/wiki/Rope_(data_structure))
- [Text Buffer Reimplementation — VS Code blog](https://code.visualstudio.com/blogs/2018/03/23/text-buffer-reimplementation)
