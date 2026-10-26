---
id: logp-sat-encoding
title: Encoding graph colouring with clauses
level: advanced
minutes: 3
sourceLesson: logp-sat
summary: Exactly one colour needs both at-least-one and at-most-one constraints.
---

## Encoding a real problem

The skill that makes SAT useful is **problem encoding**: turning a problem into clauses. Take graph 3-colouring: can you colour each vertex red, green or blue so no edge joins two vertices of the same colour?

Use a variable v_c meaning "vertex v has colour c". Three kinds of clause do the job. Each vertex gets at least one colour (line 1), at most one colour (lines 2 to 4), and the two ends of every edge differ (line 5):

```formula essential
(v_R ∨ v_G ∨ v_B)
(¬v_R ∨ ¬v_G)
(¬v_R ∨ ¬v_B)
(¬v_G ∨ ¬v_B)
(¬u_c ∨ ¬v_c)
where
v_c: the variable "vertex v has colour c"; written once for each vertex v
v_R, v_G, v_B: "v is red", "v is green", "v is blue"
u, v: the two ends of an edge; the last clause is written once for every edge and every colour c
u_c: the variable "vertex u has colour c"
c: one of the three colours R, G, B
∨: OR
¬: NOT
In words: every vertex is red, green or blue; no vertex has two colours; and for every edge and every colour, the two ends are not both that colour.
```

A satisfying assignment *is* a colouring; "unsatisfiable" is a proof that none exists. A triangle is satisfiable; K4 (four mutually connected vertices) is not.

The same style encodes standard 9 times 9 Sudoku (one Boolean variable per proposed digit in each cell), timetabling, register allocation and bounded model checking ("can the circuit reach a bad state within k steps?"). The pairwise "at most one" clauses are quadratic in the number of options; for large domains, encodings with auxiliary variables keep it smaller.


For Sudoku, a Boolean variable represents one proposed digit in one cell. It does not mean the cell stores a Boolean: the collection of nine propositions represents its possible digits. An encoding must require exactly one digit per cell, then require each digit exactly once in every row, column and box, and assert the given clues. Omitting a family of constraints changes the problem the solver answers. A satisfying assignment is useful only after decoding it and checking it against the intended puzzle rules.

## Key takeaways
- Exactly one colour needs both at-least-one and at-most-one constraints.
- Each edge needs a constraint for every colour; auxiliary encodings can reduce large at-most-one constructions.

## Further reading
- [CMU lecture: SAT solvers and DPLL](https://www.cs.cmu.edu/~15414/f18/2018/lectures/13-dpll.pdf)
- [Conflict-driven clause learning — Wikipedia](https://en.wikipedia.org/wiki/Conflict-driven_clause_learning)
- [Z3 theorem prover — GitHub](https://github.com/Z3Prover/z3)
