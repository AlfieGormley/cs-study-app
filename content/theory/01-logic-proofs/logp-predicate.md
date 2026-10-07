---
id: logp-predicate
title: Predicate logic and quantifiers
level: basic
minutes: 13
summary: Predicates, domains and the quantifiers ∀ and ∃, how to translate English and code into them, negating and nesting quantifiers correctly, and where they show up in Big-O, Python and SQL.
---

Propositional logic cannot say "every user has an email address" without listing every user. It treats each statement as an indivisible T or F, with no way to talk about *things* and their *properties*.

**Predicate logic** (also called first-order logic) adds exactly that: variables that range over objects, properties of those objects, and the words "for all" and "there exists". It is the language most mathematics is written in, and it is what you are really writing when you use `all()`, `any()` or SQL's `EXISTS`.

## Predicates and domains

A **predicate** is a statement with variables, which becomes a proposition once you plug in values.

- Even(x): "x is even". Even(4) is true, Even(7) is false.
- Admin(u): "user u is an admin".
- Less(x, y): "x < y", a predicate of two variables.

Every variable ranges over a **domain** (or universe of discourse): the set of things it may stand for. The domain is part of the meaning. "There is an x with x² = 2" is true over the real numbers and false over the integers.

## The two quantifiers

| Symbol | Name | Meaning | Python |
|---|---|---|---|
| ∀x P(x) | universal | P holds for every x | `all(P(x) for x in D)` |
| ∃x P(x) | existential | P holds for at least one x | `any(P(x) for x in D)` |

The Python analogy assumes finite iterables, terminating predicates and no side effects. On a finite domain {a, b, c}, the quantifiers are just big connectives:

```
∀x P(x)  ≡  P(a) ∧ P(b) ∧ P(c)
∃x P(x)  ≡  P(a) ∨ P(b) ∨ P(c)
```

Standard first-order structures usually require a nonempty universe. Restricted quantification over an empty subset is still meaningful; the same conventions apply if empty universes are explicitly allowed. That explains the empty-set behaviour. An empty ∧ is true and an empty ∨ is false, so over an empty domain every ∀ statement is (vacuously) true and every ∃ statement is false. `all([])` is `True` and `any([])` is `False` for exactly this reason.

To **disprove** a ∀ claim you need one counterexample. To **prove** an ∃ claim you need one witness. Proving a ∀ claim over an infinite domain, or disproving an ∃ claim, needs an actual argument; that is what the next lessons are about.

## Translating English

Most real statements quantify over *some* of the domain: "every admin", "some order". These **restricted quantifiers** have a fixed shape, and getting it wrong is the most common error in the whole subject.

| English | Formula |
|---|---|
| Every admin is verified | ∀u (Admin(u) → Verified(u)) |
| Some admin is verified | ∃u (Admin(u) ∧ Verified(u)) |
| No admin is verified | ∀u (Admin(u) → ¬Verified(u)) |
| Not every admin is verified | ∃u (Admin(u) ∧ ¬Verified(u)) |

For these restricted-domain translations, use implication under ∀ and conjunction under ∃. This is not a restriction on which connectives may appear in quantified formulas.

> [!warning] The two classic mistranslations
> - ∀u (Admin(u) ∧ Verified(u)) says *everyone* is an admin and verified. Far too strong.
> - ∃u (Admin(u) → Verified(u)) is true as soon as there is a single non-admin, because the implication is then vacuously true. Far too weak.

In code the same shapes appear naturally:

```python
# every admin is verified
all(u.verified for u in users
    if u.admin)

# some admin is verified
any(u.admin and u.verified
    for u in users)
```

The `if` filter in a comprehension plays the role of the →.

## Negating quantifiers

Negation swaps the quantifier and pushes the ¬ inside. These are De Morgan's laws for quantifiers.

```
¬∀x P(x)  ≡  ∃x ¬P(x)
¬∃x P(x)  ≡  ∀x ¬P(x)
```

"Not every test passed" means "some test did not pass"; skipped or pending tests are not automatically failed tests. "No test failed" means "every test did not fail".

With a restricted quantifier, use the earlier rule ¬(p → q) ≡ p ∧ ¬q:

```
¬∀x (A(x) → B(x))
≡ ∃x ¬(A(x) → B(x))
≡ ∃x (A(x) ∧ ¬B(x))
```

> [!example] An SLO, negated
> Hypothetical universal requirement: "every completed request to /checkout takes at most 300 ms".
>
> Taking r to range over completed requests: ∀r (Checkout(r) → Time(r) ≤ 300)
>
> Its logical negation is ∃r (Checkout(r) ∧ Time(r) > 300): one slow completed request refutes this universal requirement. Real SLOs commonly allow an error budget; this is not a recommendation to page on every slow request. Note that ≤ flips to >, not to <.

## Nested quantifiers

Statements with several variables need several quantifiers, and their **order matters** when they are of different kinds.

Let the domain be people and L(x, y) mean "x trusts y".

- ∀x ∃y L(x, y): everyone trusts somebody (possibly different people).
- ∃y ∀x L(x, y): there is one person whom everyone trusts.

The second is much stronger. It implies the first, but not the other way round.

```
∃y ∀x P(x,y)  →  ∀x ∃y P(x,y)   valid
∀x ∃y P(x,y)  →  ∃y ∀x P(x,y)   NOT valid
```

Counterexample to the second: over the integers, ∀x ∃y (y > x) is true (take y = x + 1), but ∃y ∀x (y > x) would need a largest integer.

Quantifiers of the **same** kind commute: ∀x ∀y ≡ ∀y ∀x and ∃x ∃y ≡ ∃y ∃x.

Nested quantifiers are nested loops:

```python
xs = [3, 1, 2]

# ∀x ∃y: y > x ?
print(all(any(y > x for y in xs)
          for x in xs))     # False

# ∃y ∀x: y >= x ?
print(any(all(y >= x for x in xs)
          for y in xs))     # True
```

The first fails at x = 3, since nothing in the list exceeds it. The second succeeds with the witness y = 3.

To negate a nested statement, walk left to right, flipping each quantifier, then negate the inside:

```
¬∀x ∃y P(x,y)
≡ ∃x ¬∃y P(x,y)
≡ ∃x ∀y ¬P(x,y)
```

## A real definition: Big-O

You have already met a nested-quantifier statement. For eventually nonnegative functions on natural-number inputs, the definition of f(n) = O(g(n)) is:

```
∃c > 0  ∃n₀  ∀n ≥ n₀ :
    f(n) ≤ c · g(n)
```

Read it as a game. You choose a constant c and a threshold n₀; then any n beyond n₀ must satisfy the inequality.

To show 3n + 10 = O(n), give witnesses: c = 4 and n₀ = 10. For n ≥ 10, 3n + 10 ≤ 3n + n = 4n.

To show n² is **not** O(n), prove the negation:

```
∀c > 0  ∀n₀  ∃n ≥ n₀ :
    n² > c · n
```

Given any c and n₀, pick n = max(n₀, ⌊c⌋ + 1). Then n > c, so n² = n · n > c · n. Negating the definition tells you exactly what you have to show.

## Quantifiers and connectives

Some laws let you split quantified statements; some look similar but are false.

| Statement | Status |
|---|---|
| ∀x (P ∧ Q) ≡ ∀x P ∧ ∀x Q | equivalent |
| ∃x (P ∨ Q) ≡ ∃x P ∨ ∃x Q | equivalent |
| ∀x P ∨ ∀x Q → ∀x (P ∨ Q) | one way only |
| ∃x (P ∧ Q) → ∃x P ∧ ∃x Q | one way only |

Why not the reverse? Over the integers, every number is even or odd, so ∀x (Even ∨ Odd) is true. But "every number is even" and "every number is odd" are both false. Similarly, there is an even number and there is an odd number, but no number is both.

## Free and bound variables

In ∀x (x > y), the variable x is **bound** by the quantifier and y is **free**. A formula with free variables is a predicate, not a proposition: its truth depends on y.

A bound variable is like a loop variable or a function parameter. Renaming it consistently to a fresh name, without capturing a free variable, changes nothing: ∀x P(x) and ∀z P(z) mean the same. Reusing the same name in nested scopes is legal but confusing, exactly as shadowing is in code.

## Quantifiers in SQL

SQL has existence tests through EXISTS and quantified comparisons through ALL. It has no standalone FOR ALL quantifier for arbitrary predicates, so universal queries use the negation law ∀x P ≡ ¬∃x ¬P.

"Customers who have ordered **every** product" is ∀p ∃o (o is an order by c for p). Rewritten as ¬∃p ¬∃o, it becomes a double `NOT EXISTS`:

```sql
SELECT c.id FROM customers c
WHERE NOT EXISTS (
  SELECT 1 FROM products p
  WHERE NOT EXISTS (
    SELECT 1 FROM orders o
    WHERE o.customer_id = c.id
      AND o.product_id = p.id));
```

This pattern is called **relational division**. If the products table is empty, every customer is returned: vacuous truth again.

## How far can you automate it?

For propositional logic, you can always decide whether a formula is valid by checking every row (slowly). First-order logic is different. Church and Turing proved in 1936 that no algorithm can decide validity for every first-order formula. Gödel's completeness theorem (1929) says every valid formula has a proof, so you can *search* for proofs, but the search may run forever on a formula that is not valid.

In practice, tools such as Z3 and the Dafny verifier handle huge, useful fragments of it automatically. The undecidability shows up as timeouts and "unknown" answers, especially around quantifiers.

## Key takeaways
- A predicate becomes a proposition once its variables are fixed; the domain is part of the meaning.
- ∀ is a big ∧ and ∃ is a big ∨; over an empty domain ∀ is true and ∃ is false.
- Restricted quantifiers: ∀ pairs with →, ∃ pairs with ∧.
- ¬∀x P ≡ ∃x ¬P and ¬∃x P ≡ ∀x ¬P; to negate nested quantifiers, flip each one left to right.
- ∃y ∀x is stronger than ∀x ∃y; mixed quantifiers cannot be swapped.
- Big-O, SLOs and SQL's double NOT EXISTS are all quantified statements in disguise.

## Further reading
- [First-order logic — Wikipedia](https://en.wikipedia.org/wiki/First-order_logic)
- [Quantifier (logic) — Wikipedia](https://en.wikipedia.org/wiki/Quantifier_(logic))
- [Classical Logic — Stanford Encyclopedia of Philosophy](https://plato.stanford.edu/entries/logic-classical/)
- [The Open Logic Project (free textbooks)](https://builds.openlogicproject.org/)
- [Mathematics for Computer Science — MIT OpenCourseWare](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/)
