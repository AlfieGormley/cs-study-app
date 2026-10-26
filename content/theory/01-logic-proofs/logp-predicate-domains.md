---
id: logp-predicate-domains
title: Predicates, domains and quantifiers
level: basic
minutes: 4
sourceLesson: logp-predicate
summary: The domain determines which values a quantified variable may take.
---


Propositional logic cannot say "every user has an email address" without listing every user. It treats each statement as an indivisible true-or-false value, with no way to talk about *things* and their *properties*.

**Predicate logic** (also called first-order logic) adds exactly that: variables that range over objects, properties of those objects, and the words "for all" and "there exists". It is the language most mathematics is written in, and it is what you are really writing when you use `all()`, `any()` or SQL's `EXISTS`.

## Predicates and domains

A **predicate** is a statement with variables, which becomes a proposition once you plug in values.

- Even(x): "x is even".
- Admin(u): "user u is an admin".
- Less(x, y): "x is less than y", a predicate of two variables.

Plugging in a value gives a plain true-or-false proposition:

For example, “4 is even” is true, “7 is even” is false, and “2 is less than 5” is true. Supplying values turns each predicate into a proposition.

Every variable ranges over a **domain** (or **universe of discourse**): the set of things it may stand for. The domain is part of the meaning. "There is a number whose square is 2" is true over the real numbers (the square root of 2, about 1.414) and false over the integers.


## The two quantifiers

Two symbols turn a predicate into a proposition about the whole domain:

```formula essential
∀x P(x)
∃x P(x)
where
x: a variable ranging over the domain D
D: the domain, the set of things x may stand for
P(x): a predicate: a statement about x that is true or false once x is fixed
∀: "for all", the universal quantifier. ∀x P(x) is true when P(x) is true for every x in D
∃: "there exists", the existential quantifier. ∃x P(x) is true when P(x) is true for at least one x in D
In words: "P holds for every x" and "P holds for at least one x". The symbols are an upside-down A (for "All") and a backwards E (for "Exists").
```

| Symbol | Name | Meaning | Python |
|---|---|---|---|
| for every x P(x) | universal | P holds for every x | `all(P(x) for x in D)` |
| there exists x P(x) | existential | P holds for at least one x | `any(P(x) for x in D)` |

The Python analogy assumes finite iterables, terminating predicates and no side effects. On a finite domain {d₁, d₂, d₃}, the quantifiers are just big connectives:

On a finite domain, “for all” combines the results with AND, while “there exists” combines them with OR.

Standard first-order structures usually require a nonempty universe. Restricted quantification over an empty subset is still meaningful; the same conventions apply if empty universes are explicitly allowed. That explains the empty-set behaviour. An empty AND is true and an empty OR is false, so over an empty domain every ∀ statement is (vacuously) true and every ∃ statement is false. `all([])` is `True` and `any([])` is `False` for exactly this reason.

To **disprove** a ∀ claim you need one **counterexample**. To **prove** an ∃ claim you need one **witness**. Proving a ∀ claim over an infinite domain, or disproving an ∃ claim, needs an actual argument; that is what the next lessons are about.


## Key takeaways
- The domain determines which values a quantified variable may take.
- A universal claim needs all domain members; an existential claim needs one witness.

## Further reading
- [Open Logic Project](https://forallx.openlogicproject.org/)
- [First-order logic — Wikipedia](https://en.wikipedia.org/wiki/First-order_logic)
