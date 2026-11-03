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

For character ten, the root's left subtree contains nine characters, so go right with index one. The right child's left chunk, `na`, has two characters, so go left and read its character one: `a`.

The weights translate a whole-document position into a position relative to the current subtree. Each right descent subtracts exactly the skipped left-subtree length. With balanced, bounded-size chunks, navigation takes O(log n) for n characters; the unbalanced example class itself does not enforce that guarantee.

## Key takeaways

- Rope leaves hold chunks; internal weights count left-subtree characters.
- A right descent subtracts the skipped left-subtree length from the index.

## Further reading
- [SGI rope implementation overview](https://stlab.adobe.com/stldoc_ropeimpl.html)
- [VS Code text-buffer implementation](https://code.visualstudio.com/blogs/2018/03/23/text-buffer-reimplementation)
