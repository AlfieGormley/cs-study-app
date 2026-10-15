---
id: logp-propositional-nand
title: Building every connective from NAND
level: basic
minutes: 3
sourceLesson: logp-propositional
summary: A functionally complete collection expresses every Boolean truth table.
---

## How many connectives do you need?

Not five. Implication and the biconditional can be rewritten with the others, and OR can be rewritten with NOT and AND:

```formula
p → q ≡ ¬p ∨ q
p ↔ q ≡ (p → q) ∧ (q → p)
p ∨ q ≡ ¬(¬p ∧ ¬q)
where
p, q: propositions, each true or false
¬: NOT
∧: AND: true only when both sides are true
∨: OR: true when at least one side is true
→: implies
↔: if and only if
≡: is logically equivalent to
In words: anything written with → and ↔ can be rewritten with NOT, AND and OR, and by De Morgan OR itself can be written with NOT and AND.
```

So the set {not, ∧, or } can express every truth table, and even {not, and } alone suffices. A set like this is **functionally complete**.

Remarkably, a single connective is enough: **NAND** ("not and"), written ↑. Feeding a value into both inputs of a NAND negates it, which is the key to building the rest:

```formula
p ↑ q ≡ ¬(p ∧ q)
¬p ≡ p ↑ p
p ∧ q ≡ (p ↑ q) ↑ (p ↑ q)
p ∨ q ≡ (p ↑ p) ↑ (q ↑ q)
where
p, q: propositions, each true or false
↑: NAND (not and): false only when both sides are true
¬: NOT
∧: AND
∨: OR
≡: is logically equivalent to
In words: NAND is "not both". NAND of a value with itself is its negation; NAND of a NAND gives AND back; NAND of two negations gives OR (by De Morgan).
```

Check the AND line with p equals T and q equals T: p NAND q is F, and F NAND F is T, which matches p and q.

This is why chips can be built from NAND gates alone. NOR is also complete on its own; AND, OR and NOT individually are not.


## Key takeaways
- A functionally complete collection expresses every Boolean truth table.
- NAND alone can express negation, AND and OR; neither AND nor OR alone suffices.

## Further reading
- [MIT Mathematics for Computer Science](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/mit6_042js15_textbook.pdf)
