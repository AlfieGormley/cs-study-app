---
id: cplx-gadget-map
title: "Using a map of reductions"
level: intermediate
minutes: 3
summary: "A reduction transfers hardness from its source to its target."
sourceLesson: cplx-reductions
---

Cook–Levin gives us one NP-complete problem the hard way. Every other NP-completeness proof is a **polynomial-time reduction**: a recipe that turns instances of a known hard problem into instances of the new one, preserving the yes/no answer.

Designing reductions is a craft. The usual approach is to build **gadgets**: small pieces of the target problem that imitate a variable ("choose true or false") or a constraint ("at least one of these must hold").

## The reduction map

```
        SAT
         |   (CNF + clause splitting)
       3-SAT
      /  |   \
     IS  3-COL SUBSET-SUM
    / \          |
  VC  CLIQUE   KNAPSACK
   |
 SET-COVER   (and many more)
```

An arrow from a source problem to a target means a polynomial-time translation preserves both yes and no answers. A fast target solver would therefore solve the source too. The direction transfers hardness forwards and algorithms backwards.

So once A is NP-hard, every problem below it on the map is NP-hard too. For example, 3-SAT reduces to IS (Independent Set), and IS reduces to VC (Vertex Cover), so VC is NP-hard.

## Key takeaways

- A reduction transfers hardness from its source to its target.
- Gadgets represent choices and constraints inside a target problem.
- Arrows in the reduction map preserve the yes/no answer.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
