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

Implication can be expressed as NOT-premise OR conclusion. A biconditional combines implications in both directions. De Morgan then rewrites OR using only NOT and AND.

NOT, AND and OR can express every Boolean truth table: describe each accepted row with an AND of its required input values, then join the accepted rows with OR. De Morgan shows that NOT and AND alone suffice too. A set like this is **functionally complete**.

Remarkably, a single connective is enough: **NAND** ("not and"), written ↑. Feeding a value into both inputs of a NAND negates it, which is the key to building the rest:

```formula essential
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
