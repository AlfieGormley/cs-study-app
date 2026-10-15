---
id: logp-propositional-equivalences
title: Simplifying conditions with logical laws
level: basic
minutes: 4
sourceLesson: logp-propositional
summary: De Morgan changes AND to OR or OR to AND while negating both parts.
---

## Logical equivalence

Two formulas are **logically equivalent** if they have the same truth value in every row:

```formula
A ≡ B
where
A, B: any two formulas built from propositions and connectives
≡: is logically equivalent to: A and B have the same truth value in every row of their truth table
In words: A and B always agree. Equivalently, the formula "A if and only if B" is a tautology.
```

These are the laws you use daily to simplify conditions. Each line can be checked with a four- or eight-row truth table.

```formula
¬¬p ≡ p
¬(p ∧ q) ≡ ¬p ∨ ¬q
¬(p ∨ q) ≡ ¬p ∧ ¬q
p → q ≡ ¬p ∨ q
p → q ≡ ¬q → ¬p
p ∧ (q ∨ r) ≡ (p ∧ q) ∨ (p ∧ r)
p ∨ (q ∧ r) ≡ (p ∨ q) ∧ (p ∨ r)
p ∨ (p ∧ q) ≡ p
p ↔ q ≡ (p → q) ∧ (q → p)
where
p, q, r: propositions, each true or false
¬: NOT: flips true and false; ¬¬p is NOT applied twice
∧: AND: true only when both sides are true
∨: OR (inclusive): true when at least one side is true
→: implies: false only when the left side is true and the right side false
↔: if and only if: true when both sides have the same truth value
≡: is logically equivalent to: same truth value in every row
In words: line by line, these are double negation, De Morgan's two laws, the implication law, the contrapositive, distribution of AND over OR and of OR over AND, absorption, and the biconditional law.
```

**De Morgan's laws** are the ones you will use most: to negate an AND, negate each part and switch to OR (and vice versa).

Commutativity (order doesn't matter), associativity (grouping doesn't matter) and the identity laws complete the toolkit:

```formula
p ∧ T ≡ p
p ∨ T ≡ T
p ∨ F ≡ p
p ∧ F ≡ F
where
p: a proposition, true or false
T: the constant true
F: the constant false
∧: AND: true only when both sides are true
∨: OR: true when at least one side is true
≡: is logically equivalent to
In words: AND with true and OR with false change nothing; OR with true is always true and AND with false is always false.
```

> [!example] Simplifying a guard
> A code review finds `if not (user.banned or not user.verified):`. Write b for `user.banned` and v for `user.verified`, then apply De Morgan and double negation, as shown below.

```formula
¬(b ∨ ¬v) ≡ ¬b ∧ ¬¬v
          ≡ ¬b ∧ v
where
b: the proposition "the user is banned"
v: the proposition "the user is verified"
¬: NOT; ¬¬v is NOT applied twice, which gives v back
∨: OR: true when at least one side is true
∧: AND: true only when both sides are true
≡: is logically equivalent to
In words: "not (banned or unverified)" is the same as "not banned and verified". The first step is De Morgan, the second is double negation.
```

So it is `if not user.banned and user.verified:`, which reads far better.

You can also prove an equivalence algebraically, one law per step. Here is a derivation that tells you exactly when an implication fails:

```formula
¬(p → q) ≡ ¬(¬p ∨ q)
         ≡ ¬¬p ∧ ¬q
         ≡ p ∧ ¬q
where
p, q: propositions, each true or false
¬: NOT: flips true and false
→: implies: "if p then q"
∨: OR: true when at least one side is true
∧: AND: true only when both sides are true
≡: is logically equivalent to
In words: an implication is false exactly when p is true and q is false. The steps use the implication law, then De Morgan, then double negation.
```


## Key takeaways
- De Morgan changes AND to OR or OR to AND while negating both parts.
- A derivation preserves truth only when every step applies a valid equivalence.

## Further reading
- [MIT Mathematics for Computer Science](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/mit6_042js15_textbook.pdf)
- [De Morgan's laws — Wikipedia](https://en.wikipedia.org/wiki/De_Morgan%27s_laws)
