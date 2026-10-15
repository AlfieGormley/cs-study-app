---
id: logp-predicate-negation
title: Negating quantified requirements
level: basic
minutes: 3
sourceLesson: logp-predicate
summary: Negation swaps universal and existential quantifiers and negates the condition.
---

## Negating quantifiers

Negation swaps the quantifier and pushes the ¬ inside. These are De Morgan's laws for quantifiers.

```formula
¬∀x P(x) ≡ ∃x ¬P(x)
¬∃x P(x) ≡ ∀x ¬P(x)
where
x: a variable ranging over the domain
P(x): a predicate, true or false for each x
¬: NOT: negates whatever follows it
∀: for all
∃: there exists at least one
≡: is logically equivalent to
In words: "not everything has P" means "something lacks P", and "nothing has P" means "everything lacks P".
```

"Not every test passed" means "some test did not pass"; skipped or pending tests are not automatically failed tests. "No test failed" means "every test did not fail".

With a restricted quantifier, combine this with the rule from the first lesson that "not (if p then q)" is "p and not q":

```formula
¬∀x (A(x) → B(x))
  ≡ ∃x ¬(A(x) → B(x))
  ≡ ∃x (A(x) ∧ ¬B(x))
where
x: a variable ranging over the domain
A(x), B(x): predicates, true or false for each x
¬: NOT
→: implies: false only when the left side is true and the right side false
∧: AND: true only when both sides are true
∀: for all
∃: there exists at least one
≡: is logically equivalent to
In words: "not every A is a B" means "some A is not a B". The first step flips the quantifier; the second uses the fact that an implication fails exactly when its left side is true and its right side false.
```

> [!example] An SLO, negated
> Hypothetical universal requirement: "every completed request to /checkout takes at most 300 ms". Take r to range over completed requests; the requirement S and its logical negation are below.

```formula
S ≡ ∀r (Checkout(r) → Time(r) ≤ 300)
¬S ≡ ∃r (Checkout(r) ∧ Time(r) > 300)
where
S: the requirement as a single proposition
r: a variable ranging over completed requests
Checkout(r): the predicate "r was a request to /checkout"
Time(r): how long request r took, in milliseconds (ms)
≤: is at most (less than or equal to)
>: is more than
∀: for all
∃: there exists at least one
→: implies
∧: AND
¬: NOT
≡: is logically equivalent to (here, "is defined as")
In words: the requirement fails exactly when some checkout request took more than 300 ms.
```

One slow completed request refutes this universal requirement. Real SLOs commonly allow an error budget; this is not a recommendation to page on every slow request. Note that ≤ flips to >, not to <.


## Key takeaways
- Negation swaps universal and existential quantifiers and negates the condition.
- One offending completed request refutes a universal maximum request duration; a real service objective may allow an error budget.

## Further reading
- [Open Logic Project](https://forallx.openlogicproject.org/)
- [Classical Logic — Stanford Encyclopedia of Philosophy](https://plato.stanford.edu/entries/logic-classical/)
