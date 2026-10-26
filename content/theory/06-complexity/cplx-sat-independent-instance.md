---
id: cplx-sat-independent-instance
title: "Tracing a SAT-to-graph instance"
level: intermediate
minutes: 4
summary: "Choose compatible literal occurrences to translate between an assignment and an independent set."
sourceLesson: cplx-reductions
---

### A worked instance

Here is a formula with three clauses over four Boolean variables:

```formula essential
φ = (x1 ∨ x2 ∨ ¬x3)
  ∧ (¬x1 ∨ x3 ∨ x4)
  ∧ (¬x2 ∨ ¬x3 ∨ ¬x4)
where
φ: phi, the whole 3-CNF formula; it is true when every bracketed clause is true
x1, x2, x3, x4: Boolean variables, each set to true or false
¬: NOT: ¬x3 is true exactly when x3 is false
∨: OR: a clause is true when at least one of its 3 literals is true
∧: AND: joins the clauses; φ is true only when all of them are true
In words: three clauses, C1, C2 and C3 in order; φ is satisfiable if some true/false setting of x1 to x4 makes at least one literal true in every clause.
```

```
 C1:   x1 ---- x2       C2:  ¬x1 ---- x3
         \    /                \     /
          ¬x3                    x4

 C3:  ¬x2 ---- ¬x3
         \     /
          ¬x4

 consistency edges (5):
  C1.x1  -- C2.¬x1    C1.x2  -- C3.¬x2
  C1.¬x3 -- C2.x3     C2.x3  -- C3.¬x3
  C2.x4  -- C3.¬x4
```

The graph has nine vertices, one per occurrence, and target size three. Triangle edges enforce one choice per clause; the five listed consistency edges prevent contradictory choices.

Set the first and third variables true and the second false (the fourth can be anything). The first clause is satisfied by the first variable, the second by the third variable, and the last by the negation of the second variable.

Pick one true literal from each clause: x1 from C1, x3 from C2, ¬x2 from C3. These three vertices are in different triangles, and no two are complementary, so they form an independent set of size 3.

## Key takeaways

- Triangle edges enforce clause choices; consistency edges forbid contradictory choices.
- Choose a true literal from each clause to obtain an independent set.
- Picked nonconflicting literals can be extended to an assignment.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
