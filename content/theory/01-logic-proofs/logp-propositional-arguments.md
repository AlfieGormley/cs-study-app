---
id: logp-propositional-arguments
title: Valid arguments and reasoning errors
level: basic
minutes: 4
sourceLesson: logp-propositional
summary: Validity rules out a true-premises, false-conclusion assignment.
---

## Valid arguments

A **logical argument** has premises and a conclusion. It is **logically valid** if the conclusion is true in every row where all the premises are true. Equivalently:

```formula
(P_1 ∧ P_2 ∧ ... ∧ P_k) → C ≡ T
where
P_1, P_2, ..., P_k: the k premises, each a formula
C: the conclusion, a formula
k: the number of premises
∧: AND: true only when every part is true
→: implies: false only when the left side is true and the right side false
≡: is logically equivalent to
T: the constant true, so "≡ T" means "is a tautology"
In words: an argument is valid exactly when "if all the premises hold then the conclusion holds" is true in every row.
```

The standard valid forms, written with derives ("therefore"):

```formula
p → q, p ⊢ q
p → q, ¬q ⊢ ¬p
p → q, q → r ⊢ p → r
p ∨ q, ¬p ⊢ q
p ∨ q, p → r, q → r ⊢ r
where
p, q, r: propositions, each true or false
,: separates the premises
⊢: "therefore": the formula on the right follows validly from the premises on the left. (Strictly ⊢ means "can be derived by the rules of a proof system", and ∴ is the usual "therefore" sign; for classical propositional logic the soundness and completeness theorems make ⊢ coincide with "true in every row where the premises are true", which is written ⊨)
→: implies
¬: NOT
∨: OR (inclusive)
In words: line by line, modus ponens, modus tollens, hypothetical syllogism, disjunctive syllogism and proof by cases (disjunction elimination).
```

| Rule | Premises | Conclusion |
|---|---|---|
| Modus ponens | p implies q, p | q |
| Modus tollens | p implies q, not q | not p |
| Hypothetical syllogism | p implies q, q implies r | p implies r |
| Disjunctive syllogism | p or q, not p | q |
| Proof by cases | p or q, p implies r, q implies r | r |

And two famous invalid ones:

- **Affirming the consequent**: from p implies q and q, conclude p. Invalid (row p equals F, q equals T).
- **Denying the antecedent**: from p implies q and not p, conclude not q. Invalid (same row).

```formula
p → q, q ⊬ p
p → q, ¬p ⊬ ¬q
where
p, q: propositions, each true or false
→: implies
¬: NOT
⊬: "does not follow": some row makes every premise true and the conclusion false
In words: knowing the "then" part is true doesn't tell you the "if" part, and knowing the "if" part is false doesn't tell you the "then" part. The row p = F, q = T breaks both.
```

> [!warning] Debugging with the converse
> "If the cache is down, latency spikes. Latency spiked, so the cache is down." That is affirming the consequent. Latency spikes have many causes. Modus tollens is the safe direction: "latency did not spike, so the cache is not down" (given the premise holds).

Validity is about form, not truth. "If pigs fly, I am the Queen; pigs fly; so I am the Queen" is valid. Its conclusion is false only because a premise is false. An argument that is valid *and* has true premises is called a **sound argument**.


## Key takeaways
- Validity rules out a true-premises, false-conclusion assignment.
- Affirming the consequent and denying the antecedent are invalid even when a particular conclusion happens to be true.

## Further reading
- [MIT Mathematics for Computer Science](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/mit6_042js15_textbook.pdf)
- [Mathematics for Computer Science — MIT OpenCourseWare](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/)
