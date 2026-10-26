---
id: logp-sat-cnf
title: CNF, DIMACS and Tseitin gate definitions
level: advanced
minutes: 5
sourceLesson: logp-sat
summary: CNF is an AND of OR clauses; a satisfying assignment makes every clause true.
---


Earlier propositional logic raised a question that sounds trivial: given a propositional formula, is there *any* assignment of true and false to its variables that makes it true? That is the **Boolean satisfiability problem**, or **SAT**.

Why use a solver rather than blindly try everything?

Each additional Boolean variable doubles the number of assignments. Exhaustive search quickly becomes impractical; a solver tries to avoid exploring assignments individually.

SAT was the first problem proved **NP-complete**: every NP decision problem can be translated into it in polynomial time. No polynomial-time algorithm for general SAT is known; finding one would settle P vs NP. Polynomial time is a growth guarantee, not a promise of practical speed. Modern SAT solvers can solve large structured industrial formulas, but instance size alone does not predict runtime. They verify chip designs, resolve package dependencies and power program-verification tools.

This lesson explains the input representation that lets a solver work with those constraints.

## Conjunctive normal form

Solvers take their input in a standard shape, **conjunctive normal form (CNF)**:

- A **literal** is a variable or its negation: x, or "not x".
- A **clause** is an OR of literals.
- A **CNF formula** is an AND of clauses.

Here is a running example, with four clauses over three variables:

```formula essential
(x ∨ y) ∧ (¬x ∨ z) ∧ (¬y ∨ ¬z) ∧ (¬z)
where
x, y, z: propositional variables, each true or false
¬: NOT: ¬x is true exactly when x is false; x and ¬x are both literals
∨: OR: a clause like (x ∨ y) is true when at least one of its literals is true
∧: AND: the whole formula is true only when every clause is true
In words: "x or y", and "not x or z", and "not y or not z", and "not z", all at once. The last clause has a single literal, which makes it a **unit clause**.
```

To satisfy a CNF formula, every clause must contain at least one true literal. A clause is a constraint: "at least one of these must hold". This is a natural shape for real requirements, which is half the reason CNF is the standard.

Solvers read it in the **DIMACS** format, with each variable written as a number and negation as a minus sign. The formula above, with x, y, z as 1, 2, 3:

```
p cnf 3 4
1 2 0
-1 3 0
-2 -3 0
-3 0
```

The header says 3 variables and 4 clauses; each clause ends in 0.

### Converting to CNF

Every formula has an equivalent CNF, found using the laws from the first lesson: eliminate → (implies) and ↔ (if and only if), push ¬ inwards with De Morgan, then distribute ∨ over ∧. But distribution can explode. Consider an OR of independent two-input AND groups:

Distributing an OR of independent AND pairs requires a clause for every choice of one member from each pair. The clause count doubles with each added pair, even though the original expression grows by only one pair.

The important distinction is input size: an equivalent representation may be exponentially larger.

The fix is the **Tseitin transformation**: introduce a fresh variable for each subformula and add clauses that define it. For an AND gate, the fresh variable x must equal a and b:

```formula essential
x ↔ (a ∧ b)
(¬x ∨ a) ∧ (¬x ∨ b) ∧ (x ∨ ¬a ∨ ¬b)
where
x: the fresh variable standing for the subformula a ∧ b
a, b: the inputs to the gate (variables or other gates' fresh variables)
↔: if and only if: both sides have the same truth value
∧: AND
∨: OR
¬: NOT
→: implies (used in the explanation below)
In words: the second line is the first written as three clauses. The first two clauses say "if x then a" and "if x then b"; the third says "if a and b then x".
```

The first two clauses say x implies a and x implies b; the third says (a and b) implies x. Add these constraints for every bounded-fan-in gate and a unit clause asserting the root/output variable true. The resulting CNF is linear in formula size. Gate definitions alone do not assert the original formula. It is generally not logically equivalent over the enlarged set of variables, but it is equisatisfiable: satisfiable exactly when the original is. That is all a solver needs.


## Key takeaways
- CNF is an AND of OR clauses; a satisfying assignment makes every clause true.
- Tseitin gate definitions plus an asserted output give a linear-size equisatisfiable encoding for bounded-fan-in formulas.

## Further reading
- [CMU lecture: SAT solvers and DPLL](https://www.cs.cmu.edu/~15414/f18/2018/lectures/13-dpll.pdf)
- [Boolean satisfiability problem — Wikipedia](https://en.wikipedia.org/wiki/Boolean_satisfiability_problem)
- [MiniSat](http://minisat.se/)
