---
id: tree-red-black-insertion
title: Red-black insertion and colour repair
level: intermediate
minutes: 2
sourceLesson: tree-balanced
summary: Repair insertion colours with uncle cases and rotations.
---

The preceding unit defined red-black invariants: a black root, no red parent with a red child, and equal black-height on every path to a NIL child. Start with strict BST ordering and distinct comparable keys. Here n counts stored keys. This is the conventional bottom-up repair outline, rather than an executable insertion implementation; left-leaning and other variants have different repair rules.

## Insertion and colour repair

1. Insert as in a BST and colour the new node **red** (this preserves rule 3; rule 2 or the root-colour rule may need repair).
2. If its parent is black, done.
3. If its parent is red, look at the **uncle** (the parent's sibling):
   - **Uncle red:** recolour parent and uncle black and the grandparent red, then repeat the check from the grandparent. No rotation; the problem moves up two levels.
   - **Uncle black:** one or two rotations around the grandparent plus a recolour fix it for good.
4. Colour the root black.

For the conventional bottom-up red-black algorithms, insertion uses at most two rotations and deletion at most three. Recolouring and fix-up traversal can take O(log n) steps in one update of a tree of n keys, because the red-uncle case can repeat up the whole path. These rotation bounds do not apply automatically to every red-black variant.

> [!note] Red-black trees are 2-3-4 trees in disguise
> Glue each black node to its red children and you get a B-tree node with 2, 3 or 4 children. Rule 3 says all leaves of that B-tree are at the same depth. Sedgewick's **left-leaning red-black tree** (2008) restricts red links further and its 2-3 variant maps onto 2-3 trees, which makes the code much shorter.

## Key takeaways
- New nodes start red so existing black counts are unchanged.
- A red uncle allows recolouring and moves the conflict upward.
- A black uncle requires rotations and recolouring; restore the root to black.

## Further reading
- [Red–black tree — Wikipedia](https://en.wikipedia.org/wiki/Red%E2%80%93black_tree)
- [Left-leaning Red-Black Trees — Robert Sedgewick (PDF)](https://sedgewick.io/wp-content/themes/sedgewick/papers/2008LLRB.pdf)
- [Red-black Trees (rbtree) in Linux — kernel docs](https://docs.kernel.org/core-api/rbtree.html)
