---
id: cplx-sat-clause-width
title: "From SAT to 3-SAT and 2-SAT"
level: intermediate
minutes: 4
summary: "Fresh variables split long CNF clauses with only linear growth."
sourceLesson: cplx-np-completeness
---

## From SAT to 3-SAT

Most reductions start from **3-SAT**: CNF formulas where every clause has exactly 3 literals (in some treatments, at most 3). Its rigid shape makes gadgets easier to design.

First convert a general Boolean formula to equisatisfiable CNF with fresh gate variables (the Tseitin construction); distributing OR over AND can cause exponential blow-up. SAT in CNF then reduces to 3-SAT by splitting long clauses with fresh variables. A five-literal clause is replaced by three three-literal clauses:

```formula essential
C_old = (l_1 ∨ l_2 ∨ l_3 ∨ l_4 ∨ l_5)
C_new = (l_1 ∨ l_2 ∨ y_1)
  ∧ (¬y_1 ∨ l_3 ∨ y_2)
  ∧ (¬y_2 ∨ l_4 ∨ l_5)
where
C_old: the original clause, with 5 literals
C_new: the three clauses that replace it
l_1, l_2, l_3, l_4, l_5: the literals of the original clause; a literal is a variable or its negation
y_1, y_2: fresh variables that appear nowhere else in the formula
∨: OR: a clause is true when at least one of its literals is true
∧: AND: all three new clauses must be true
¬: NOT: ¬y_1 is true exactly when y_1 is false
In words: C_new can be satisfied (by choosing y_1 and y_2) exactly when at least one original literal is true, so C_old and C_new are equivalent for satisfiability.
```

If some l_i is true, set the y's to "carry" the chain round it: y's before it true, y's after it false. If all l_i are false, y_1 must be true, which forces y_2 true, which falsifies the last clause.

Each extra original literal needs only a constant amount of extra formula, so splitting has linear growth. Short clauses are padded by repeating a literal, or with extra variables if repeats are forbidden.

The fresh variables are local to this clause. Reusing them across unrelated clauses could introduce constraints that were never in the original formula. The new formula is equisatisfiable with the old one: assignments to original variables may need extending, rather than using the same assignment unchanged.

### The edge of tractability: 2-SAT

With two literals per clause, the problem collapses into P. Each two-literal clause is the same as two implications:

```formula essential
(a ∨ b)  ≡  (¬a → b) ∧ (¬b → a)
where
a, b: literals (a variable or its negation)
∨: OR: true when at least one side is true
¬: NOT: ¬a is true exactly when a is false
→: implies: ¬a → b means "if a is false then b must be true"
∧: AND: both implications hold
≡: "is logically equivalent to": true in exactly the same assignments
In words: "a or b" means "if not a then b, and if not b then a". For the clause (x ∨ y): if x is false, y must be true, and if y is false, x must be true.
```

Draw each implication as an arrow between literals: this is the implication graph. The formula is unsatisfiable exactly when some variable and its own negation lie in the same strongly connected component of this graph (each can reach the other), which takes linear time to check (Aspvall, Plass and Tarjan, 1979). Going from 2 to 3 literals per clause crosses from linear time to NP-complete.

## Key takeaways

- Fresh variables split long CNF clauses with only linear growth.
- The split preserves satisfiability through an extension of the original assignment.
- 2-SAT uses implication graphs and strongly connected components.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
- [Theory of Computation — MIT OpenCourseWare](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/)
