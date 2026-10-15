---
id: logp-predicate-nested
title: Quantifier order and witness choice
level: basic
minutes: 3
sourceLesson: logp-predicate
summary: A witness chosen after another variable may depend on that variable.
---

## Nested quantifiers

Statements with several variables need several quantifiers, and their **order matters** when they are of different kinds.

Let the domain be people and L(x, y) mean "x trusts y".

- for every x there exists y L(x, y): everyone trusts somebody (possibly different people).
- there exists y for every x L(x, y): there is one person whom everyone trusts.

The second is much stronger. It implies the first, but not the other way round:

```formula
∃y ∀x L(x, y)  ⊨  ∀x ∃y L(x, y)
∀x ∃y L(x, y)  ⊭  ∃y ∀x L(x, y)
where
x, y: variables ranging over people
L(x, y): the predicate "x trusts y"
∀: for all
∃: there exists at least one
⊨: logically implies: in every domain and interpretation where the left side is true, the right side is true too
⊭: does not logically imply: some interpretation makes the left side true and the right side false
In words: if one person is trusted by everyone, then everyone trusts somebody. But everyone trusting somebody does not mean there is one person trusted by all.
```

A counterexample to the second line, over the integers with "y is greater than x" in place of L(x, y):

```formula
∀x ∃y (y > x)
y = x + 1
∃y ∀x (y > x)
where
x, y: variables ranging over the integers (…, −2, −1, 0, 1, 2, …)
>: is greater than
∀: for all
∃: there exists at least one
In words: "every integer has a bigger one" is true, because y = x + 1 is a witness for each x. "Some integer is bigger than every integer" is false: it would need a largest integer.
```

Quantifiers of the **same** kind commute (can swap places):

```formula
∀x ∀y P(x, y) ≡ ∀y ∀x P(x, y)
∃x ∃y P(x, y) ≡ ∃y ∃x P(x, y)
where
x, y: variables ranging over the domain
P(x, y): a predicate of two variables
∀: for all
∃: there exists at least one
≡: is logically equivalent to
In words: two "for all"s, or two "there exists"es, can be written in either order. Only mixed pairs are order-sensitive.
```

Nested quantifiers are nested loops:

```python
xs = [3, 1, 2]

# Each item needs a larger list member.
print(all(any(y > x for y in xs)
          for x in xs))     # False

# One member must dominate the whole list.
print(any(all(y >= x for x in xs)
          for y in xs))     # True
```

The first fails at x equals 3, since nothing in the list exceeds it. The second succeeds with the witness y equals 3.

To negate a nested statement, walk left to right, flipping each quantifier, then negate the inside:

```formula
¬∀x ∃y P(x, y)
  ≡ ∃x ¬∃y P(x, y)
  ≡ ∃x ∀y ¬P(x, y)
where
x, y: variables ranging over the domain
P(x, y): a predicate of two variables
¬: NOT
∀: for all
∃: there exists at least one
≡: is logically equivalent to
In words: "not everyone has someone they P" means "someone has nobody they P". Each step moves the ¬ one quantifier to the right and flips that quantifier.
```


## Key takeaways
- A witness chosen after another variable may depend on that variable.
- A single witness that works for everyone is stronger than a potentially different witness for each person.

## Further reading
- [Open Logic Project](https://forallx.openlogicproject.org/)
- [The Open Logic Project (free textbooks)](https://builds.openlogicproject.org/)
