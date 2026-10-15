---
id: logp-propositional-classification
title: Classifying and comparing formulas
level: basic
minutes: 3
sourceLesson: logp-propositional
summary: A tautology is true on every assignment; a contradiction is false on every assignment.
---

## Tautologies, contradictions, satisfiable formulas

Tautology, contradiction and contingency form three disjoint classes. Satisfiability is a related property that overlaps them. The two simplest examples, "p or not p" and "p and not p":

```formula
p ∨ ¬p ≡ T
p ∧ ¬p ≡ F
where
p: a proposition, true or false
¬: NOT: ¬p is true exactly when p is false
∨: OR: true when at least one side is true
∧: AND: true only when both sides are true
≡: is logically equivalent to: same truth value in every row
T: the constant "true", a formula that is true in every row
F: the constant "false", a formula that is false in every row
In words: "p or not p" is true whatever p is, and "p and not p" is false whatever p is. Try p = T and p = F: the first gives T both times, the second F both times.
```

- A **tautology** is true in every row. Example: p or not p.
- A **contradiction** is false in every row. Example: p and not p.
- A **contingent formula** is true in some rows and false in others.
- A formula is **satisfiable** if at least one row makes it true: both tautologies and contingent formulas qualify.

These are linked: a formula A is a tautology exactly when its negation not A is unsatisfiable. SAT solvers exploit this to check that something *always* holds: they search for a row where it fails, and "no such row" is a proof.


A single propositional input, considered as a formula on its own, is contingent: the row where the input is true satisfies it and the row where the input is false does not. This also makes it satisfiable. By contrast, a contradiction has no satisfying row at all. These labels answer different questions: “does any assignment work?” is an existence question, while “does every assignment work?” is a universal question. Checking the negation changes the latter into a search for a counterexample.

## Key takeaways
- A tautology is true on every assignment; a contradiction is false on every assignment.
- Satisfiable means at least one assignment works, so tautologies and contingent formulas both qualify.

## Further reading
- [MIT Mathematics for Computer Science](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/mit6_042js15_textbook.pdf)
- [Material conditional — Wikipedia](https://en.wikipedia.org/wiki/Material_conditional)
