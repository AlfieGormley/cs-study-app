---
id: logp-propositional-equivalences
title: Simplifying conditions with logical laws
level: basic
minutes: 3
sourceLesson: logp-propositional
summary: De Morgan changes AND to OR or OR to AND while negating both parts.
---

## Logical equivalence

Two formulas are **logically equivalent** if they have the same truth value in every row. Equivalence means agreement on every allowed assignment, not merely agreement in the examples tested.

These are the laws you use daily to simplify conditions. The following two laws can be checked with a four-row truth table.

```formula essential
¬(p ∧ q) ≡ ¬p ∨ ¬q
¬(p ∨ q) ≡ ¬p ∧ ¬q
where
p, q: propositions, each true or false
¬: NOT: flips true and false
∧: AND: true only when both sides are true
∨: OR (inclusive): true when at least one side is true
≡: is logically equivalent to: same truth value in every row
In words: negating “both” means at least one part fails; negating “either” means both parts fail.
```

**De Morgan's laws** are the ones you will use most: to negate an AND, negate each part and switch to OR (and vice versa).

Commutativity means order doesn't matter; associativity means grouping doesn't matter. The identity laws say that AND with true and OR with false leave the other input unchanged. OR with true always succeeds; AND with false always fails.

> [!example] Simplifying a guard
> A code review finds `if not (user.banned or not user.verified):`. Assume Boolean attributes without side effects. Apply De Morgan and double negation.

Negate each alternative and join them with AND: the user must be not banned and not unverified. Double negation turns the latter into verified.

So it is `if not user.banned and user.verified:`. With ordinary Boolean attributes, both guards admit exactly the same cases.

Python evaluates `and` and `or` from left to right and may stop early. A logical rewrite that changes evaluation order can therefore be unsafe if an expression raises an exception or has side effects. Check an object is not `None` before reading its attributes.

The same reasoning explains the failing case of an implication. Its premise must hold and its conclusion must fail. That describes the same single failing row as the truth-table definition.


## Key takeaways
- De Morgan changes AND to OR or OR to AND while negating both parts.
- A derivation preserves truth only when every step applies a valid equivalence.

## Further reading
- [MIT Mathematics for Computer Science](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/mit6_042js15_textbook.pdf)
- [De Morgan's laws — Wikipedia](https://en.wikipedia.org/wiki/De_Morgan%27s_laws)
