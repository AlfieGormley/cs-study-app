---
id: logp-propositional-connectives
title: Propositions, connectives and truth tables
level: basic
minutes: 5
sourceLesson: logp-propositional
summary: Connectives combine true-or-false propositions; inclusive OR includes the case where both inputs hold.
---


Every `if` statement you have written is a small piece of logic. Propositional logic is the precise version of that: a way of combining true/false statements and working out, mechanically, when the combination is true.

It is the foundation for everything else in this module. Proofs are built from it, predicate logic extends it, and the SAT problem in the last lesson asks one question about it that turns out to be enormously hard and enormously useful.

## Propositions

In the classical two-valued logic used here, a proposition is a statement that is either true or false, never both.

- "7 is prime" is a proposition (true).
- "2 plus 2 equals 5" is a proposition (false).
- "x is greater than 3" is **not** a proposition on its own: its truth depends on what the unknown x is. (Predicate logic, next lesson, handles this.)
- "Close the door" is not a proposition: it is neither true nor false.

We name propositions with letters: p, q, r. These are **propositional variables**, the logical equivalent of Boolean variables in code. When we write down the truth values themselves, T means true and F means false.


## The connectives

Five connectives build bigger formulas from smaller ones. Each has its own symbol, and these symbols appear in every lesson of this module, so it is worth learning them now.

```formula
¬p
p ∧ q
p ∨ q
p → q
p ↔ q
where
p, q: propositions (propositional variables), each either true or false
¬: NOT (negation). ¬p is true exactly when p is false
∧: AND (conjunction). p ∧ q is true only when both p and q are true
∨: OR (disjunction). p ∨ q is true when at least one of p, q is true, including when both are
→: IMPLIES (implication, the conditional). p → q reads "if p then q", and is false only when p is true and q is false
↔: IF AND ONLY IF (the biconditional). p ↔ q is true when p and q have the same truth value, both true or both false
In words: "not p", "p and q", "p or q", "if p then q" and "p if and only if q": the five ways to build a bigger statement out of p and q.
```

The table gives each one's name and the nearest Python.

| Symbol | Name | Read as | Python |
|---|---|---|---|
| not p | negation | not p | `not p` |
| p and q | conjunction | p and q | `p and q` |
| p or q | disjunction | p or q | `p or q` |
| p implies q | implication | if p then q | `(not p) or q` |
| p if and only if q | biconditional | p if and only if q | `p == q` |

The Python column assumes Boolean operands. Python and/or return operands and short-circuit; arbitrary objects can have custom truth tests and equality. The logical connectives have their meaning fixed by a **truth table**, which lists every combination of inputs, one per row. Each variable doubles the number of combinations, because every existing row splits into a "true" version and a "false" version:

```formula
N_rows = 2^n
N_rows = 2^2 = 4   for n = 2
N_rows = 2^3 = 8   for n = 3
where
N_rows: the number of rows in the truth table, one per combination of input values
n: the number of propositional variables in the formula
2^n: n copies of 2 multiplied together (2 to the power n)
In words: a truth table over n variables has 2 to the power n rows, so two variables need 4 rows and three need 8.
```

Here is the truth table for all five connectives over p and q. T is true and F is false; each column is one connective.

```
p q | ¬p  p∧q  p∨q  p→q  p↔q
----+-------------------------
T T |  F   T    T    T    T
T F |  F   F    T    F    F
F T |  T   F    T    T    F
F F |  T   F    F    T    T
```

Two things trip people up.

- **∨ is inclusive.** p or q is true when both are true. "Exclusive or" (exactly one) is a separate connective, written ⊕. In Python on booleans it is `p != q`.
- **→ is false in exactly one row**: when p is true and q is false.

Exclusive or is "not (p if and only if q)", because it is true exactly when p and q differ:

```formula
p ⊕ q ≡ ¬(p ↔ q)
where
p, q: propositions, each true or false
⊕: XOR (exclusive or): true when exactly one of p, q is true
↔: if and only if: true when p and q have the same truth value
¬: NOT: flips true to false and false to true
≡: is logically equivalent to: the two sides have the same truth value in every row of the truth table
In words: "exactly one of p and q" means the same as "it is not the case that p and q agree". With p true and q false, both sides are true.
```


## Key takeaways
- Connectives combine true-or-false propositions; inclusive OR includes the case where both inputs hold.
- Every independent Boolean input doubles the number of rows of the truth table.

## Further reading
- [MIT Mathematics for Computer Science](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/mit6_042js15_textbook.pdf)
- [Propositional calculus — Wikipedia](https://en.wikipedia.org/wiki/Propositional_calculus)
