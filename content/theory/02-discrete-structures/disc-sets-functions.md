---
id: disc-sets-functions
title: Sets and functions
level: basic
minutes: 12
summary: Set notation and operations, power sets and Cartesian products, injective, surjective and bijective functions, and why infinite sets come in different sizes.
---

Almost every structure in computer science is built from two ideas: a **set** (a collection of things) and a **function** (a rule that maps each thing in one set to exactly one thing in another). A simple model treats a type as a set of values and a mathematical relation as a set of tuples. SQL tables can contain duplicate rows, and a hash table usually maps a key through a hash value to a bucket. Getting fluent with the vocabulary pays off everywhere else in this subject.

## Sets

A set is an unordered collection of distinct elements. Order and repetition don't matter:

```
{1, 2, 3} = {3, 1, 2} = {1, 1, 2, 3}
```

Notation you will see constantly:

| Symbol | Meaning |
|---|---|
| x ∈ A | x is an element of A |
| A ⊆ B | every element of A is in B |
| A ⊂ B | A ⊆ B and A ≠ B (proper subset) |
| ∅ | the empty set, {} |
| \|A\| | the cardinality (size) of A |

Sets can be written by listing elements, or with **set-builder notation**, which resembles a Python comprehension (mathematical sets can also be infinite):

```
E = { x ∈ ℤ : 0 ≤ x < 10 and x even }
  = {0, 2, 4, 6, 8}

# Python
E = {x for x in range(10) if x % 2 == 0}
```

Common number sets: ℕ (natural numbers; whether 0 is included varies by author, so check), ℤ (integers), ℚ (rationals), ℝ (reals).

> [!warning] Elements versus subsets
> ∅ ⊆ A is true for every set A, but ∅ ∈ A is only true if A literally contains the empty set as an element. {∅} is a set with one element; ∅ has none.

## Set operations

```
A ∪ B   union: in A or B (or both)
A ∩ B   intersection: in both
A \ B   difference: in A but not B
A ⊕ B   symmetric difference:
        in exactly one of them
Aᶜ      complement: not in A
        (relative to a universe U)
```

```
   +-------+-------+
   |  A    |    B  |
   | only  | both  |  only
   |  A\B  |  A∩B  |  B\A
   +-------+-------+
```

Python's built-in set supports union, intersection, difference and symmetric difference; complement needs an explicit universe, U - a, and they are the bread and butter of practical code (deduplicating, finding common users, permission checks):

```python
a = {1, 2, 3, 4}
b = {3, 4, 5}
a | b   # {1, 2, 3, 4, 5}
a & b   # {3, 4}
a - b   # {1, 2}
a ^ b   # {1, 2, 5}
a <= b  # False: is a a subset of b?
```

Two laws worth memorising are **De Morgan's laws**, which mirror the logic versions:

```
(A ∪ B)ᶜ = Aᶜ ∩ Bᶜ
(A ∩ B)ᶜ = Aᶜ ∪ Bᶜ
```

In words: "not in (A or B)" is "not in A and not in B". This is the same rewrite you do when you push a `NOT` through an SQL `WHERE` clause.

## Power sets and Cartesian products

The **power set** P(A) is the set of all subsets of A. If |A| = n then |P(A)| = 2ⁿ, because each element is independently either in or out of a subset: two choices, n times.

```
A    = {a, b, c}
P(A) = { ∅, {a}, {b}, {c}, {a,b},
         {a,c}, {b,c}, {a,b,c} }
|P(A)| = 2³ = 8
```

That "in or out" view is exactly how programmers enumerate subsets with a **bitmask**: the integers 0 to 2ⁿ − 1, where bit i says whether element i is included.

```python
items = ['a', 'b', 'c']
n = len(items)
for mask in range(1 << n):
    sub = [items[i] for i in range(n)
           if mask >> i & 1]
    print(mask, sub)
```

There are 2ⁿ subsets: about a million for 20 items and a trillion for 40. Runtime also includes work per subset. The shown construction scans n positions for each mask, taking Θ(n·2ⁿ) elementary operations under a unit-cost bit model, before accounting for formatting and printing.

The **Cartesian product** A × B is the set of ordered pairs (a, b) with a ∈ A and b ∈ B, so |A × B| = |A| · |B|. A relational table with columns drawn from domains D₁, …, Dₖ is a subset of D₁ × … × Dₖ, and an SQL CROSS JOIN combines every input-row occurrence with every occurrence on the other side, retaining duplicate multiplicities.

## Functions

A **function** f : A → B assigns to every element of the **domain** A exactly one element of the **codomain** B. Two conditions: every input has an output, and no input has two outputs.

The **image** (often called the range) is the set of outputs actually hit, f(A) = { f(a) : a ∈ A }. It is a subset of the codomain and may be smaller.

Three properties matter:

- **Injective** (one-to-one): different inputs give different outputs. f(x) = f(y) implies x = y.
- **Surjective** (onto): every element of B is hit by some input. Image = codomain.
- **Bijective**: both. Every element of B is hit by exactly one element of A, so f has an **inverse** f⁻¹ : B → A.

```
injective    surjective   bijective
not onto     not 1-to-1
a -> 1       a -> 1       a -> 1
b -> 2       b -> 1       b -> 2
c -> 3       c -> 2       c -> 3
     4
```

For finite sets these give size constraints:

- An injection A → B exists only if |A| ≤ |B|.
- A surjection A → B exists only if |A| ≥ |B|.
- A bijection exists only if |A| = |B|.

The first one is the **pigeonhole principle** in disguise: map more pigeons than holes and two pigeons must share.

> [!example] Why hash functions collide
> Standard SHA-256 accepts messages shorter than 2⁶⁴ bits and produces one of 2²⁵⁶ outputs. Its finite input domain is still vastly larger than its output space. No function from a larger set to a smaller one can be injective, so collisions must exist. Cryptographic hashes are designed so that *finding* one is infeasible, not so that none exist.

### Composition and inverses

The **composition** (g ∘ f)(x) = g(f(x)) applies f first, then g. Compositions preserve the properties above: two injections compose to an injection, two bijections to a bijection.

If g ∘ f is injective, then f must be injective (if f merged two inputs, g could not separate them again). If a stage merges two reachable states that arose from distinct valid inputs, later deterministic stages cannot recover that distinction without additional information. Non-injectivity only on states the pipeline never reaches need not lose information.

### Counting functions

For finite sets with |A| = m and |B| = n:

```
all functions A -> B   n^m
injections A -> B      n!/(n-m)! if m<=n
                      0 if m>n
bijections A -> A      m!   (permutations)
```

Use the counting convention 0⁰ = 1 for the unique empty-domain function. There are nᵐ functions because each of the m inputs independently picks one of n outputs. For example, there are 2⁸ = 256 functions from an 8-bit position set to {0, 1}: one per byte value.

## Functions in real code

The mathematical idea of a function is stricter than a programming "function". A routine whose result depends on changing hidden state may return different results for the same explicit arguments. Including the relevant state in the mathematical input gives a function again; reading an immutable constant does not itself violate determinism. Pure terminating routines fit the simple total-function model and can be easier to test, memoise and parallelise.

Bijections show up whenever you need a lossless round trip:

- **Serialisation**: `decode(encode(x)) == x` for every valid x is a requirement that `encode` is injective, and `decode` is its inverse on the image.
- **Base64, UTF-8, gzip**: with a fixed encoder configuration and appropriate valid input domain, lossless round trips require injectivity. Ordinary lossy JPEG and MP3 encoding merge distinct inputs; the JPEG family also includes lossless modes.
- **Primary keys**: projecting each row to its primary-key value uniquely identifies that row. A primary key combines uniqueness with non-nullness; a bare UNIQUE constraint can permit multiple nulls depending on the database and configuration.
- **Permutations in shuffles and ciphers**: a block cipher with a fixed key is a bijection on blocks, otherwise decryption would be ambiguous.

## Infinite sets have different sizes

For infinite sets we define "same size" using bijections: |A| = |B| if a bijection A → B exists. This leads to surprises.

A set is **countable** if it is finite or in bijection with ℕ (you can list its elements in a sequence that eventually reaches each one). ℤ is countable: list it as 0, 1, −1, 2, −2, …. So is ℚ, and so is the set of all finite strings over a finite alphabet, which means **the set of all programs is countable**.

**Cantor's diagonal argument** shows that the set of infinite binary sequences (equivalently, P(ℕ), or the reals) is **not** countable. Suppose you had a complete list s₁, s₂, s₃, … Build a new sequence d by flipping the i-th bit of sᵢ:

```
s1 = 0 1 1 0 1 ...
s2 = 1 1 0 0 0 ...
s3 = 0 0 0 1 1 ...
s4 = 1 0 1 1 0 ...
d  = 1 0 1 0 ...   (flip diagonal)
```

d differs from every sᵢ at position i, so it is not on the list, contradicting completeness. More generally, Cantor's theorem says |P(A)| > |A| for every set A.

> [!note] Why CS cares
> Programs are countable but the set of functions from ℕ to {0, 1} (all possible yes/no problems) is not. So almost all problems have no program that solves them. The halting problem, covered in the computability module, is a concrete example built with the same diagonal trick.

## Pitfalls

- **Codomain versus image.** Whether f is surjective depends on the declared codomain. With domain ℝ, f(x) = x² is surjective onto [0, ∞) but not onto ℝ.
- **Sets are unordered and deduplicated.** Converting a list to a set and back loses order and duplicates. Python sets only hold hashable elements, so use `frozenset` for a set of sets.
- **Off-by-one in power sets.** 2ⁿ includes both ∅ and A itself. "Non-empty subsets" is 2ⁿ − 1.
- **"Function" in code is not always a function.** Changing hidden state can break the same-explicit-input/same-result rule; an output side effect can violate purity even when the returned result is deterministic.

## Key takeaways
- A set is an unordered collection of distinct elements; union, intersection, difference and symmetric difference map to Python's |, &, - and ^; complement is U - A for an explicit universe U.
- |P(A)| = 2ⁿ and |A × B| = |A|·|B|; bitmasks identify 2ⁿ subsets; constructing each list explicitly costs Θ(n·2ⁿ) total elementary operations.
- Injective means no collisions, surjective means every output is hit, bijective means both and implies an inverse.
- From a larger finite set to a smaller one no injection exists, which is why hash collisions are unavoidable.
- Countable sets can be listed; Cantor's diagonal argument shows P(ℕ) cannot, so most problems have no program.

## Further reading
- [Set (mathematics) — Wikipedia](https://en.wikipedia.org/wiki/Set_(mathematics))
- [Bijection, injection and surjection — Wikipedia](https://en.wikipedia.org/wiki/Bijection)
- [Cantor's diagonal argument — Wikipedia](https://en.wikipedia.org/wiki/Cantor%27s_diagonal_argument)
- [Mathematics for Computer Science (Lehman, Leighton, Meyer), MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
- [Mathematics for Computer Science — MIT OpenCourseWare](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/)
