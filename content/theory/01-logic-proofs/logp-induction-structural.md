---
id: logp-induction-structural
title: Structural induction over trees and expressions
level: intermediate
minutes: 3
sourceLesson: logp-induction
summary: Structural induction follows each constructor of a recursive definition.
---

## Structural induction

Lists, trees, expressions and programs are defined by **recursion**: base objects, plus rules that build bigger objects from smaller ones. **Structural induction** proves a property for every such object.

1. **Base**: prove it for each base object.
2. **Step**: for each construction rule, assume it for the parts and prove it for the whole.

### Example: leaves in a full binary tree

A **full binary tree** is either a single leaf, or a root with exactly two children, each of which is a full binary tree.

Claim: in every full binary tree, the number of leaves is one more than the number of internal nodes:

```formula
L = I + 1
where
L: the number of leaves (nodes with no children)
I: the number of internal nodes (nodes with two children)
In words: a full binary tree always has exactly one more leaf than it has internal nodes. A root with two leaf children has L = 2 and I = 1.
```

**Base**: a single leaf has L equals 1 and I equals 0. ✓

**Step**: a bigger tree T is a root joined to two smaller full binary trees T₁ and T₂. By the IH, each subtree satisfies the claim. Count T's leaves and internal nodes (the root is one extra internal node):

```formula
L_1 = I_1 + 1,   L_2 = I_2 + 1
L = L_1 + L_2
I = I_1 + I_2 + 1
L = (I_1 + 1) + (I_2 + 1)
  = (I_1 + I_2 + 1) + 1 = I + 1
where
L, I: the leaves and internal nodes of the whole tree T
L_1, I_1: the leaves and internal nodes of the left subtree T_1
L_2, I_2: the leaves and internal nodes of the right subtree T_2
T_1, T_2: the two subtrees hanging from the root
In words: the whole tree's leaves are the subtrees' leaves, and its internal nodes are the subtrees' internal nodes plus the root. Substituting the hypothesis gives L = I + 1 again. ∎
```

Consequence: a full binary tree with n leaves has n minus 1 internal nodes, so twice n minus one nodes in total. A single-elimination tournament with 64 teams, one elimination per match and no extra placement or replay matches, has 63 matches; a Huffman tree over 256 symbols has 255 internal nodes.

The induction follows the tree constructors rather than incrementing a numerical size parameter. You could induct on height or on the number of nodes, but structural induction follows the definition directly, which is usually simpler. It is also how compilers and type checkers are proved correct: by induction over the abstract syntax tree, one rule per kind of node.


## Key takeaways
- Structural induction follows each constructor of a recursive definition.
- A full binary tree has one more leaf than internal node; its total node count follows by adding both counts.

## Further reading
- [MIT Mathematics for Computer Science](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/mit6_042js15_textbook.pdf)
- [Well-founded relation — Wikipedia](https://en.wikipedia.org/wiki/Well-founded_relation)
