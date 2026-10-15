---
id: logp-sat-cnf
title: CNF, DIMACS and Tseitin gate definitions
level: advanced
minutes: 5
sourceLesson: logp-sat
summary: CNF is an AND of OR clauses; a satisfying assignment makes every clause true.
---


Earlier propositional logic raised a question that sounds trivial: given a propositional formula, is there *any* assignment of true and false to its variables that makes it true? That is the **Boolean satisfiability problem**, or **SAT**.

How many assignments are there to try?

```formula
N_assign = 2^n
N_assign = 2^100 ≈ 1.27 × 10^30
where
N_assign: the number of ways to give every variable the value true or false
n: the number of propositional variables in the formula
2^n: n copies of 2 multiplied together, because each variable doubles the count
≈: approximately equal to
10^30: a 1 followed by 30 zeros
In words: each extra variable doubles the number of assignments, so (second line) a formula with just 100 variables already has about 10^30 of them, far too many to try one by one.
```

SAT was the first problem proved **NP-complete**, which means nobody knows an algorithm that is fast on every input, and finding one would settle P vs NP. Modern SAT solvers can solve large structured industrial formulas, but instance size alone does not predict runtime. They verify chip designs, resolve package dependencies and power program-verification tools.

This lesson is about both halves of that story: why SAT is hard in theory, and why it is so often easy in practice.

## Conjunctive normal form

Solvers take their input in a standard shape, **conjunctive normal form (CNF)**:

- A **literal** is a variable or its negation: x, or "not x".
- A **clause** is an OR of literals.
- A **CNF formula** is an AND of clauses.

Here is a running example, with four clauses over three variables:

```formula
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

Every formula has an equivalent CNF, found using the laws from the first lesson: eliminate → (implies) and ↔ (if and only if), push ¬ inwards with De Morgan, then distribute ∨ over ∧. But distribution can explode. Take this formula, an OR of n pairs:

```formula
(a_1 ∧ b_1) ∨ (a_2 ∧ b_2)
  ∨ ... ∨ (a_n ∧ b_n)
N_clauses = 2^n
where
a_1, b_1, a_2, b_2, ..., a_n, b_n: propositional variables, two per pair
n: the number of pairs
∧: AND
∨: OR
N_clauses: the number of clauses in the equivalent CNF made by distribution
2^n: n copies of 2 multiplied together
In words: distributing turns this into one clause for every way of picking a or b from each pair, so 2^n clauses; 30 pairs already give over a billion.
```

The formula has 2n literals, but its distributed CNF has 2 to the power n clauses.

The fix is the **Tseitin transformation**: introduce a fresh variable for each subformula and add clauses that define it. For an AND gate, the fresh variable x must equal a and b:

```formula
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
