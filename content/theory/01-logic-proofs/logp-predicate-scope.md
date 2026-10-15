---
id: logp-predicate-scope
title: Quantifier laws and variable scope
level: basic
minutes: 3
sourceLesson: logp-predicate
summary: Universal quantification distributes over AND; existential quantification distributes over OR.
---

## Quantifiers and connectives

Some laws let you split quantified statements; some look similar but only hold in one direction:

```formula
∀x (P(x) ∧ Q(x)) ≡ ∀x P(x) ∧ ∀x Q(x)
∃x (P(x) ∨ Q(x)) ≡ ∃x P(x) ∨ ∃x Q(x)
∀x P(x) ∨ ∀x Q(x) ⊨ ∀x (P(x) ∨ Q(x))
∃x (P(x) ∧ Q(x)) ⊨ ∃x P(x) ∧ ∃x Q(x)
where
x: a variable ranging over the domain
P(x), Q(x): predicates, true or false for each x
∀: for all
∃: there exists at least one
∧: AND
∨: OR
≡: is logically equivalent to (holds both ways)
⊨: logically implies (holds left to right only)
In words: "for all" splits over AND and "there exists" splits over OR, in both directions. "For all" over OR and "there exists" over AND only work one way.
```

Why not the reverse of the last two? Over the integers:

```formula
∀x (Even(x) ∨ Odd(x)) = T
∀x Even(x) ∨ ∀x Odd(x) = F
where
x: a variable ranging over the integers
Even(x): "x is even"
Odd(x): "x is odd"
∀: for all
∨: OR
T: true
F: false
In words: every integer is even or odd, but it is false that every integer is even, and false that every integer is odd.
```

Similarly, there is an even number and there is an odd number, but no number is both, so the ∃-over-AND law can't be reversed either.


## Free and bound variables

In the formula below, x is a **bound variable**, while y is a **free variable**:

```formula
∀x (x > y)
∀x P(x) ≡ ∀z P(z)
where
x, z: bound variables: each belongs to the quantifier in front of it, like a loop variable
y: a free variable: nothing quantifies it, so its value must come from outside
P: any predicate
>: is greater than
∀: for all
≡: is logically equivalent to
In words: the first formula has a free variable y and needs an assignment to it. Its truth need not change between assignments; for example, over all integers it is always false. Renaming a bound variable (x to z) changes nothing.
```

An open formula is evaluated using an assignment to its free variables. Its truth may depend on that assignment, though an open formula can be true or false for every assignment in a particular structure. For example, over the integers the first displayed formula is false for every integer assigned to the free variable; there is always an integer no greater than it.

A bound variable is like a loop variable or a function parameter. Renaming it consistently to a fresh name, without capturing a free variable, changes nothing. Reusing the same name in nested scopes is legal but confusing, exactly as shadowing is in code.


## Key takeaways
- Universal quantification distributes over AND; existential quantification distributes over OR.
- Independent witnesses cannot generally be merged, and renaming bound variables must avoid capture.

## Further reading
- [Open Logic Project](https://forallx.openlogicproject.org/)
