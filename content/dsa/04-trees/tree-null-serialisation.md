---
id: tree-null-serialisation
title: Serialising trees with empty-child markers
level: advanced
minutes: 3
sourceLesson: tree-problems
summary: Values alone omit shape; empty-child markers make shape explicit.
---

Use the binary Node with val, left and right fields introduced earlier. Assume a finite acyclic tree with no shared nodes or concurrent mutation. Throughout this unit n counts nodes and h is the tree height in edges. Recursive examples are limited by Python call depth; arithmetic has unit cost and hash-table operations have expected constant cost. Each example distinguishes working storage from returned output.

## Serialise and deserialise

To send a tree over a network or save it to disk you must flatten it so it can be rebuilt **exactly**. A traversal of values alone is not enough: the trees `1 → left 2` and `1 → right 2` both have pre-order `1, 2`. The fix is to record the **empty children** too.

```
        3
       / \
      9   20
         /  \
        15   7

pre-order with '#' for None:
3,9,#,#,20,15,#,#,7,#,#
```

```python
def serialise(root):
    out = []
    def pre(node):
        if node is None:
            # Record shape,
            # not merely
            # values.
            out.append('#')
            return
        out.append(str(node.val))
        pre(node.left)
        pre(node.right)
    pre(root)
    return ','.join(out)

def deserialise(data):
    tokens = iter(data.split(','))
    def build():
        # Consume exactly this
        # subtree's tokens.
        t = next(tokens)
        if t == '#':
            return None
        node = Node(int(t))
        # Consume the left shape before the
        # right.
        node.left = build()
        node.right = build()
        return node
    root = build()
    if next(tokens, None) is not None:
        raise ValueError("trailing tokens")
    return root
```

This teaching format supports integer node values. Truncated input raises StopIteration, invalid integer text raises ValueError, and extra tokens are rejected; untrusted input also requires size and depth limits. Runtime and storage depend on encoded character length, not just node count.

Deserialising consumes the tokens in the same pre-order they were written, so each recursive call knows exactly where its subtree begins and ends. A tree of n nodes produces one value per node plus **one more null marker than nodes**, because a binary tree always has one more empty child slot than nodes (the binary-counting unit). The example string `3,9,#,#,20,15,#,#,7,#,#` has 5 values and 6 markers. A count that does not match is a quick sign of a truncated or corrupted string.

Level-order with nulls (the format LeetCode displays) works too. A JSON or Protocol Buffers schema can encode nested child relationships explicitly; the format alone does not choose a tree representation.

> [!analogy] Real-world analogy: dictating a seating plan
> You read a theatre seating plan down the phone, seat by seat in a fixed order. If you only read out names, the listener cannot tell where the gaps are and seats everyone too far forward. Saying "empty" for each empty seat lets them rebuild the plan exactly.
>
> **How it maps:** names are node values, "empty" is the `#` marker, and the fixed reading order is the pre-order walk. The listener fills seats in the same order the plan was read, as `deserialise` consumes tokens in pre-order.
>
> **Where it stops:** a theatre has a fixed grid, so the listener knows how many seats there are. A tree's shape is not known in advance; the markers are the only record of where each branch ends.

## Key takeaways
- Values alone omit shape; empty-child markers make shape explicit.
- Read tokens in the same recursive order as they were written.
- Validate untrusted input and account for encoded text length.

## Further reading
- [Tree traversal — Wikipedia](https://en.wikipedia.org/wiki/Tree_traversal)
