---
id: logp-predicate
title: Predicate logic and quantifiers
level: basic
minutes: 16
summary: Predicates, domains and the quantifiers ∀ and ∃, how to translate English and code into them, negating and nesting quantifiers correctly, and where they show up in Big-O, Python and SQL.
---

Propositional logic cannot say "every user has an email address" without listing every user. It treats each statement as an indivisible true-or-false value, with no way to talk about *things* and their *properties*.

**Predicate logic** (also called first-order logic) adds exactly that: variables that range over objects, properties of those objects, and the words "for all" and "there exists". It is the language most mathematics is written in, and it is what you are really writing when you use `all()`, `any()` or SQL's `EXISTS`.

## Predicates and domains

A **predicate** is a statement with variables, which becomes a proposition once you plug in values.

- Even(x): "x is even".
- Admin(u): "user u is an admin".
- Less(x, y): "x is less than y", a predicate of two variables.

Plugging in a value gives a plain true-or-false proposition:

```formula
Even(4) = T
Even(7) = F
Less(2, 5) = T
where
Even(x): the predicate "x is even", for a whole number x
Less(x, y): the predicate "x is less than y", for numbers x and y
x, y: variables: placeholders for values from the domain
T: true
F: false
In words: a predicate is a function from values to true or false. "4 is even" is true, "7 is even" is false, "2 is less than 5" is true.
```

Every variable ranges over a **domain** (or **universe of discourse**): the set of things it may stand for. The domain is part of the meaning. "There is a number whose square is 2" is true over the real numbers (the square root of 2, about 1.414) and false over the integers.

## The two quantifiers

Two symbols turn a predicate into a proposition about the whole domain:

```formula
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
| ∀x P(x) | universal | P holds for every x | `all(P(x) for x in D)` |
| ∃x P(x) | existential | P holds for at least one x | `any(P(x) for x in D)` |

The Python analogy assumes finite iterables, terminating predicates and no side effects. On a finite domain {d₁, d₂, d₃}, the quantifiers are just big connectives:

```formula
∀x P(x) ≡ P(d_1) ∧ P(d_2) ∧ P(d_3)
∃x P(x) ≡ P(d_1) ∨ P(d_2) ∨ P(d_3)
where
d_1, d_2, d_3: the three members of the domain
x: a variable ranging over that domain
P(x): a predicate, true or false for each x
∀: for all: every member of the domain
∃: there exists: at least one member of the domain
∧: AND: true only when every part is true
∨: OR: true when at least one part is true
≡: is logically equivalent to: always has the same truth value
In words: on a finite domain, "for all" is a long AND over every member, and "there exists" is a long OR.
```

Standard first-order structures usually require a nonempty universe. Restricted quantification over an empty subset is still meaningful; the same conventions apply if empty universes are explicitly allowed. That explains the empty-set behaviour. An empty AND is true and an empty OR is false, so over an empty domain every ∀ statement is (vacuously) true and every ∃ statement is false. `all([])` is `True` and `any([])` is `False` for exactly this reason.

To **disprove** a ∀ claim you need one **counterexample**. To **prove** an ∃ claim you need one **witness**. Proving a ∀ claim over an infinite domain, or disproving an ∃ claim, needs an actual argument; that is what the next lessons are about.

## Translating English

Most real statements quantify over *some* of the domain: "every admin", "some order". These **restricted quantifiers** have a fixed shape, and getting it wrong is the most common error in the whole subject. Over a domain of users:

```formula
∀u (Admin(u) → Verified(u))
∃u (Admin(u) ∧ Verified(u))
where
u: a variable ranging over all users
Admin(u): the predicate "u is an admin"
Verified(u): the predicate "u is verified"
∀: for all users
∃: there exists at least one user
→: implies: "if ... then ...", false only when the left side is true and the right side false
∧: AND: true only when both sides are true
In words: "every user, if an admin, is verified" (every admin is verified) and "some user is both an admin and verified" (some admin is verified).
```

The four common patterns (¬ is NOT):

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

## Nested quantifiers

Statements with several variables need several quantifiers, and their **order matters** when they are of different kinds.

Let the domain be people and L(x, y) mean "x trusts y".

- ∀x ∃y L(x, y): everyone trusts somebody (possibly different people).
- ∃y ∀x L(x, y): there is one person whom everyone trusts.

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

A counterexample to the second line, over the integers with "y > x" in place of L(x, y):

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

# ∀x ∃y: y > x ?
print(all(any(y > x for y in xs)
          for x in xs))     # False

# ∃y ∀x: y >= x ?
print(any(all(y >= x for x in xs)
          for y in xs))     # True
```

The first fails at x = 3, since nothing in the list exceeds it. The second succeeds with the witness y = 3.

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

## A real definition: Big-O

You have already met a nested-quantifier statement. For eventually nonnegative functions on natural-number inputs, Big-O is defined like this:

```formula
f(n) = O(g(n))   iff
∃c > 0 ∃n_0 ∀n ≥ n_0 : f(n) ≤ c · g(n)
where
f(n): the function being bounded, e.g. an algorithm's step count for input size n
g(n): the comparison function, e.g. n or n^2
n: the input size, a natural number (0, 1, 2, …)
O(g(n)): "Big-O of g": grows no faster than a constant times g, once n is large enough
c: a positive constant multiplier, chosen by the prover
n_0: a threshold input size, chosen by the prover; the inequality only has to hold from n_0 upwards
∃: there exists at least one
∀: for all
≥, ≤: is at least, is at most
·: multiplied by
:: "such that" (separates the quantifiers from the condition)
In words: f is O(g) when you can pick a constant c and a starting point n_0 so that, for every n from n_0 on, f(n) is at most c times g(n).
```

Read it as a game. You choose a constant c and a threshold n₀; then any n beyond n₀ must satisfy the inequality.

To show 3n + 10 = O(n), give witnesses: c = 4 and n₀ = 10.

```formula
3 × n + 10 ≤ 3 × n + n = 4 × n   for n ≥ 10
c = 4,  n_0 = 10
where
n: the input size; from n_0 = 10 on, 10 is at most n
c: the constant multiplier chosen as a witness
n_0: the threshold chosen as a witness
≤: is at most
In words: once n is at least 10, the "+ 10" is no bigger than another n, so 3n + 10 is at most 4n. That is the definition with c = 4 and n_0 = 10.
```

To show n² is **not** O(n), prove the negation of the definition (every quantifier flips and ≤ becomes >):

```formula
∀c > 0 ∀n_0 ∃n ≥ n_0 : n^2 > c · n
where
c: any positive constant the opponent picks
n_0: any threshold the opponent picks
n: an input size you must find, at or beyond n_0
n^2: n multiplied by itself
∀: for all
∃: there exists at least one
·: multiplied by
:: "such that"
In words: whatever constant and threshold are chosen, you can always find a larger input where n² beats c times n.
```

Here is how to find that n for any given c and n₀:

```formula
n = max(n_0, ⌊c⌋ + 1)
n > c
n^2 = n · n > c · n
where
n: the input size you pick
n_0, c: the threshold and constant you were given
max(a, b): the larger of a and b, so n is at least n_0
⌊c⌋: the floor of c: c rounded down to a whole number (⌊2.7⌋ = 2), so ⌊c⌋ + 1 is bigger than c
·: multiplied by
In words: pick n at least n_0 and bigger than c. Then n times n is bigger than c times n. For example, with c = 2.7 and n_0 = 1, n = 3 gives 9 > 8.1.
```

Negating the definition tells you exactly what you have to show.

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

In the formula below, the quantifier **binds** x, while y is left **free**:

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
In words: "every x is bigger than y" depends on what y is, so it is a predicate of y, not a proposition. Renaming a bound variable (x to z) changes nothing.
```

A formula with free variables is a predicate, not a proposition: its truth depends on y.

A bound variable is like a loop variable or a function parameter. Renaming it consistently to a fresh name, without capturing a free variable, changes nothing. Reusing the same name in nested scopes is legal but confusing, exactly as shadowing is in code.

## Quantifiers in SQL

SQL has existence tests through EXISTS and quantified comparisons through ALL. It has no standalone FOR ALL quantifier for arbitrary predicates, so universal queries use the negation law:

```formula
∀x P(x) ≡ ¬∃x ¬P(x)
where
x: a variable ranging over the domain (here, rows of a table)
P(x): a predicate, true or false for each x
∀: for all
∃: there exists at least one (SQL `EXISTS`)
¬: NOT (SQL `NOT`)
≡: is logically equivalent to
In words: "everything has P" means "there is nothing without P".
```

"Customers who have ordered **every** product" becomes a double `NOT EXISTS`:

```formula
∀p ∃o Ord(c, p, o)
  ≡ ¬∃p ¬∃o Ord(c, p, o)
where
c: the customer being tested
p: a variable ranging over products
o: a variable ranging over orders
Ord(c, p, o): the predicate "o is an order by customer c for product p"
∀: for all
∃: there exists at least one
¬: NOT
≡: is logically equivalent to
In words: "c ordered every product" means "there is no product that c has no order for".
```

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

In practice, tools such as Z3 and the Dafny verifier handle large, useful parts of it automatically. The undecidability shows up as timeouts and "unknown" answers, especially around quantifiers.

## Key takeaways
- A predicate becomes a proposition once its variables are fixed; the domain is part of the meaning.
- ∀ (for all) is a big AND and ∃ (there exists) is a big OR; over an empty domain ∀ is true and ∃ is false.
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
