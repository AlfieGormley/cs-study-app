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

```formula essential
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

With a restricted quantifier, the counterexample must belong to the restricted group:

To refute “every admin is verified”, find an actual admin who is unverified. A non-admin cannot be that counterexample.

> [!example] An SLO, negated
> Hypothetical universal requirement: "every completed request to /checkout takes at most 300 ms". Only completed requests count, and the boundary is inclusive.

The requirement fails if some completed checkout request takes more than 300 milliseconds. Exactly 300 milliseconds is permitted; the failing case is strictly greater.

One slow completed request refutes this universal requirement. Real SLOs commonly allow an error budget; this is not a recommendation to page on every slow request. Note that ≤ flips to >, not to <.


## Key takeaways
- Negation swaps universal and existential quantifiers and negates the condition.
- One offending completed request refutes a universal maximum request duration; a real service objective may allow an error budget.

## Further reading
- [Open Logic Project](https://forallx.openlogicproject.org/)
- [Classical Logic — Stanford Encyclopedia of Philosophy](https://plato.stanford.edu/entries/logic-classical/)
