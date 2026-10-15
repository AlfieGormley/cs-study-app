---
id: logp-propositional-implication
title: Reading implications and contrapositives
level: basic
minutes: 4
sourceLesson: logp-propositional
summary: An implication fails only when its premise holds and its conclusion fails.
---

## Why implication works this way

The bottom two rows of p implies q surprise everyone. Why is "if p then q" true whenever p is false? Here is the rule in one place:

```formula
p → q = F   when p = T and q = F
p → q = T   otherwise
where
p: the "if" part (the premise or antecedent), a proposition; here "you pass the exam"
q: the "then" part (the conclusion or consequent), a proposition; here "I buy you dinner"
→: implies: "if p then q"
T: true
F: false
In words: an implication is broken only by a true premise with a false conclusion; in the other three rows it holds.
```

Think of p implies q as a **promise**. "If you pass the exam, I'll buy you dinner." The only way I break the promise is if you pass (p true) and I don't buy dinner (q false). If you fail, I have kept my word whatever I do. A promise that was never triggered was never broken.

This is called **vacuous truth**, and it matters. "Every element of the empty list is negative" is true, because there is no element to break it. Python agrees: `all([])` is `True`.

The connective defined by this table is the **material conditional**. It says nothing about cause. "If 2 plus 2 equals 5 then the Moon is cheese" is true, because the premise is false. That feels wrong in English, but it is the definition that makes proofs work.

> [!tip] Reading p implies q
> All of these mean p implies q: "if p then q", "p implies q", "p only if q", "q if p", "p is sufficient for q", "q is necessary for p". The phrase "p only if q" catches people out: it means p cannot happen without q, which is p implies q, not q implies p.


## Converse, inverse, contrapositive

From an implication p implies q you can form three related statements by swapping the two sides, negating both, or doing both:

```formula
p → q
q → p
¬p → ¬q
¬q → ¬p
where
p → q: the original implication, "if p then q"
q → p: the converse: the two sides swapped
¬p → ¬q: the inverse: both sides negated
¬q → ¬p: the contrapositive: swapped and negated
p, q: propositions, each true or false
¬: NOT: ¬p is true exactly when p is false
→: implies: false only when the left side is true and the right side is false
In words: the original, its converse, its inverse and its contrapositive. Only the contrapositive always has the same truth table as the original.
```

| Name | Form | Same as p implies q? |
|---|---|---|
| Contrapositive | not q implies not p | Yes, always |
| Converse | q implies p | Not in general |
| Inverse | not p implies not q | Not in general |

"If it is raining, the ground is wet" does not mean "if the ground is wet, it is raining" (a sprinkler could be on). That is the converse, and assuming it is one of the most common reasoning errors in proofs, code reviews and incident postmortems.

The contrapositive, "if the ground is not wet, it is not raining", is equivalent. You can check by truth table: both are false in exactly one row: p true and q false. The converse and the inverse are equivalent to *each other* (one is the contrapositive of the other).


## Key takeaways
- An implication fails only when its premise holds and its conclusion fails.
- Only the contrapositive is always equivalent to the original implication; a converse needs separate justification.

## Further reading
- [MIT Mathematics for Computer Science](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/mit6_042js15_textbook.pdf)
- [Truth table — Wikipedia](https://en.wikipedia.org/wiki/Truth_table)
