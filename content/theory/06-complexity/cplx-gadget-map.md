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

An arrow from A down to B means A reduces to B, written with the symbol ≤_p:

```formula
A ≤_p B
x ∈ A  iff  f(x) ∈ B
where
A: the problem we already know is hard (higher up the map), e.g. 3-SAT
B: the problem we want to show is hard (lower down the map), e.g. IS
≤_p: "polynomial-time reduces to": a polynomial-time translation maps every instance of A to an instance of B with the same yes/no answer, so B is at least as hard as A
x: any instance (input) of problem A
f: the reduction: an algorithm that turns an instance of A into an instance of B, running in polynomial time (at most about n^k steps for an input of n bits and some fixed k)
f(x): the instance of B that f builds from x
∈: "is a yes-instance of": x ∈ A means x is an input whose answer for problem A is yes
In words: A reduces to B when a fast translation turns every A-question into a B-question with exactly the same answer. Then a fast algorithm for B would give one for A, so B is at least as hard as A.
```

So once A is NP-hard, every problem below it on the map is NP-hard too. For example, 3-SAT reduces to IS (Independent Set), and IS reduces to VC (Vertex Cover), so VC is NP-hard.

## Key takeaways

- A reduction transfers hardness from its source to its target.
- Gadgets represent choices and constraints inside a target problem.
- Arrows in the reduction map preserve the yes/no answer.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
