---
id: cplx-sat-independent-instance
title: "Tracing a SAT-to-graph instance"
level: intermediate
minutes: 4
summary: "Count triangle and consistency edges separately."
sourceLesson: cplx-reductions
---

### A worked instance

Here is a formula with three clauses over four Boolean variables:

```formula
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

Counting the graph:

```formula
|V| = 3m = 3 × 3 = 9
|E| = 3m + 5 = 9 + 5 = 14
k = m = 3
where
|V|: the number of vertices
m: the number of clauses, here 3
|E|: the number of edges: 3 triangle edges per clause plus the 5 consistency edges drawn above
k: the independent-set size asked for
In words: 9 vertices, 14 edges, and we ask for an independent set of size 3, one vertex per clause.
```

Set the first and third variables true and the second false (the fourth can be anything). Each clause then has a true literal:

```formula
C1 = x1 ∨ x2 ∨ ¬x3 = T ∨ F ∨ F = T
C2 = ¬x1 ∨ x3 ∨ x4 = F ∨ T ∨ x4 = T
C3 = ¬x2 ∨ ¬x3 ∨ ¬x4 = T ∨ F ∨ ¬x4 = T
where
C1, C2, C3: the three clauses of φ
x1, x2, x3, x4: Boolean variables; here x1 = T, x2 = F, x3 = T, x4 either
T: true
F: false
¬: NOT: flips true and false
∨: OR: true when at least one part is true
In words: with x1 true, x2 false and x3 true, every clause contains a true literal whatever x4 is, so φ is satisfied.
```

Pick one true literal from each clause: x1 from C1, x3 from C2, ¬x2 from C3. These three vertices are in different triangles, and no two are complementary, so they form an independent set of size 3.

## Key takeaways

- Count triangle and consistency edges separately.
- Choose a true literal from each clause to obtain an independent set.
- Picked nonconflicting literals can be extended to an assignment.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
