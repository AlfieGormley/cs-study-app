---
id: disc-sets-functions
title: Sets and functions
level: basic
minutes: 16
summary: Set notation and operations, power sets and Cartesian products, injective, surjective and bijective functions, and why infinite sets come in different sizes.
---

Almost every structure in computer science is built from two ideas: a **set** (a collection of things) and a **function** (a rule that maps each thing in one set to exactly one thing in another). A simple model treats a type as a set of values and a mathematical relation as a set of tuples. SQL tables can contain duplicate rows, and a hash table usually maps a key through a hash value to a bucket. Getting fluent with the vocabulary pays off everywhere else in this subject.

## Sets

A set is an unordered collection of distinct elements. Curly braces list what is in it, and only membership counts: the order you write the elements in and any repeats make no difference.

```formula
{1, 2, 3} = {3, 1, 2} = {1, 1, 2, 3}
where
{ }: curly braces: the set whose elements are the things listed inside, separated by commas
=: the two sets are equal: they have exactly the same elements
In words: all three ways of writing it describe the same set, the one containing exactly 1, 2 and 3. Changing the order or repeating 1 does not make a new set.
```

Notation you will see constantly:

| Symbol | Meaning |
|---|---|
| x ∈ A | x is an element of A |
| x ∉ A | x is not an element of A |
| A ⊆ B | every element of A is in B |
| A ⊂ B | A ⊆ B and A ≠ B (proper subset) |
| ∅ | the empty set, {} |
| \|A\| | the cardinality (size) of A |

In this table, ≠ means "is not equal to", and the capital letters A and B stand for any two sets.

For example, with A = {1, 2} and B = {1, 2, 3}:

```formula
1 ∈ A     3 ∉ A
A ⊆ B     A ⊂ B
|A| = 2   |B| = 3
where
A: the example set {1, 2}
B: the example set {1, 2, 3}
∈: is an element of
∉: is not an element of
⊆: is a subset of: every element of the left-hand set is also in the right-hand set (the two may be equal)
⊂: is a proper subset of: a subset that is not equal, so the right-hand set has at least one extra element
| |: vertical bars around a set mean its cardinality: the number of elements it has
In words: 1 is in A but 3 is not; everything in A is also in B, and B has an extra element (3), so A is a proper subset of B; A has 2 elements and B has 3.
```

Sets can be written by listing elements, or with **set-builder notation**, which describes the elements by a rule. It resembles a Python comprehension, but mathematical sets can also be infinite:

```formula
E = { x ∈ ℤ : 0 ≤ x < 10, x mod 2 = 0 }
E = {0, 2, 4, 6, 8}
where
E: the set being defined (the even numbers below 10)
x: a stand-in for each candidate element
ℤ: the integers: …, −2, −1, 0, 1, 2, …
∈: is an element of
{ x ∈ ℤ : … }: set-builder notation: the set of all integers x that make the condition after the colon true. The colon reads "such that"; some books write a vertical bar | instead
≤: is less than or equal to
<: is less than
mod: the remainder after dividing, so x mod 2 = 0 means x is even
In words: E is the set of integers x with 0 ≤ x < 10 that are even, which works out to {0, 2, 4, 6, 8}.
```

The same set in Python, where `%` is the remainder operator:

```python
E = {x for x in range(10) if x % 2 == 0}
```

Common number sets: ℕ (natural numbers; whether 0 is included varies by author, so check), ℤ (integers), ℚ (rationals, the fractions of integers) and ℝ (reals, every point on the number line).

> [!warning] Elements versus subsets
> The empty set is a subset of every set, but it is an element of a set only if that set literally lists the empty set inside its braces. The set containing just the empty set has one element; the empty set itself has none.

```formula
∅ ⊆ A   for every A
∅ ∈ {∅}     ∅ ∉ {1, 2}
|{∅}| = 1   |∅| = 0
where
∅: the empty set, the set with no elements, also written {}
A: any set at all
⊆: is a subset of: every element of the left-hand set is in the right-hand set
∈: is an element of
∉: is not an element of
{ }: curly braces: the set of the things listed inside
| |: the cardinality: the number of elements in the set
In words: the empty set is a subset of everything (it has no element that could fail to be in A), but it is only an element of a set that lists it, like {∅}. That set has one element; ∅ has none.
```

## Set operations

These operations build new sets from old ones. The **universe** U is the set of everything under discussion (all users, all integers), which a complement needs so it knows what "not in A" ranges over.

```formula
A ∪ B = { x : x ∈ A or x ∈ B }
A ∩ B = { x : x ∈ A and x ∈ B }
A \ B = { x : x ∈ A and x ∉ B }
A ⊕ B = (A ∪ B) \ (A ∩ B)
Aᶜ = U \ A
where
A, B: any two sets
x: a stand-in for an element
U: the universe: the set of everything under discussion
∪: union: in A or B (or both)
∩: intersection: in both A and B
\: set difference: in A but not in B (some books write A − B)
⊕: symmetric difference: in exactly one of the two sets (some books write A △ B)
ᶜ: complement: everything in the universe U that is not in A
∈: is an element of
∉: is not an element of
{ x : … }: the set of all x that make the condition after the colon true
In words: union keeps anything in either set, intersection keeps what they share, difference keeps A's elements that B lacks, symmetric difference keeps what is in exactly one, and the complement is everything in the universe that is not in A.
```

The picture shows how the three regions of two overlapping sets line up with these operations:

```
   +-------+-------+
   |  A    |    B  |
   | only  | both  |  only
   |  A\B  |  A∩B  |  B\A
   +-------+-------+
```

A worked example, with a universe of the numbers 1 to 6:

```formula
A = {1, 2, 3, 4}   B = {3, 4, 5}
A ∪ B = {1, 2, 3, 4, 5}
A ∩ B = {3, 4}
A \ B = {1, 2}
A ⊕ B = {1, 2, 5}
Aᶜ = {5, 6}   for U = {1, 2, 3, 4, 5, 6}
where
A, B: the two example sets
U: the universe, here the numbers 1 to 6
∪: union: in A or B (or both)
∩: intersection: in both
\: difference: in A but not in B
⊕: symmetric difference: in exactly one of A and B
ᶜ: complement: in the universe but not in A
In words: the union has every number from either set, the intersection only the shared 3 and 4, the difference A's numbers that B lacks, the symmetric difference everything except the shared 3 and 4, and the complement the numbers in U that A misses.
```

Python's built-in set supports union, intersection, difference and symmetric difference; complement needs an explicit universe, `U - a`. They are the bread and butter of practical code (deduplicating, finding common users, permission checks):

```python
a = {1, 2, 3, 4}
b = {3, 4, 5}
a | b   # {1, 2, 3, 4, 5}
a & b   # {3, 4}
a - b   # {1, 2}
a ^ b   # {1, 2, 5}
a <= b  # False: is a a subset of b?
```

Two laws worth memorising are **De Morgan's laws**, which mirror the logic versions. They say how a complement passes through a union or an intersection:

```formula
(A ∪ B)ᶜ = Aᶜ ∩ Bᶜ
(A ∩ B)ᶜ = Aᶜ ∪ Bᶜ
where
A, B: any two sets inside a universe U
ᶜ: complement: everything in the universe U that is not in the set
∪: union: in either set
∩: intersection: in both sets
In words: "not in (A or B)" is the same as "not in A and not in B", and "not in (A and B)" is the same as "not in A or not in B". The complement flips union into intersection and back.
```

Check the first law with the example sets from above:

```formula
A = {1, 2, 3, 4}   B = {3, 4, 5}
(A ∪ B)ᶜ = {1, 2, 3, 4, 5}ᶜ = {6}
Aᶜ ∩ Bᶜ = {5, 6} ∩ {1, 2, 6} = {6}
where
A, B: the two example sets, inside the universe U = {1, 2, 3, 4, 5, 6}
U: the universe: everything under discussion, here the numbers 1 to 6
ᶜ: complement: the elements of U that are not in the set
∪: union: in either set
∩: intersection: in both sets
In words: only 6 is outside both sets, and computing it either way gives {6}, so the two sides of the law agree.
```

This is the same rewrite you do when you push a `NOT` through an SQL WHERE clause.

## Power sets and Cartesian products

The **power set** P(A) is the set of all subsets of A. Its size is a power of two, because each element is independently either in or out of a subset: two choices, made once per element.

```formula
|P(A)| = 2^n   when |A| = n
A = {a, b, c}
P(A) = { ∅, {a}, {b}, {c}, {a, b},
         {a, c}, {b, c}, {a, b, c} }
|P(A)| = 2^3 = 8
where
A: any finite set; in the example, the set of the three letters a, b and c
a, b, c: the three elements of the example set
P(A): the power set of A: the set whose elements are all the subsets of A
n: the number of elements in A
| |: the cardinality: the number of elements in a set
∅: the empty set, the subset with nothing in it
{ }: the set of the things listed inside
2^n: n copies of 2 multiplied together
In words: a set of n elements has 2^n subsets, counting both the empty set and the whole set. Three elements give 2 × 2 × 2 = 8 subsets.
```

That "in or out" view is exactly how programmers enumerate subsets with a **bitmask**: an integer whose binary digits (bits) say which elements are in. Number the elements from 0 upwards; each bit of the mask is 1 when the element with that number is in the subset.

```formula
m = x_0 × 2^0 + x_1 × 2^1 + …
      + x_{n−1} × 2^{n−1}
0 ≤ m ≤ 2^n − 1
{b, c} → m = 0 × 1 + 1 × 2 + 1 × 4 = 6
where
m: the mask: one whole number standing for one subset
x_0, x_1, x_{n−1}: the bits of the mask: bit number i is 1 if element number i is in the subset and 0 if not, for i from 0 up to n − 1
n: the number of elements in the set
2^0, 2^1, 2^{n−1}: powers of 2 (1, 2, 4, …), the place value of each bit
…: and so on, one term for every element
≤: is less than or equal to
→: is encoded as
b, c: in the last line, elements 1 and 2 of {a, b, c} (a is element 0)
In words: every subset of an n-element set corresponds to exactly one whole number from 0 to 2^n − 1. For {a, b, c}, the subset {b, c} is mask 6, binary 110.
```

The loop below visits every mask and decodes it back into a subset:

```python
items = ['a', 'b', 'c']
n = len(items)
for mask in range(1 << n):
    sub = [items[i] for i in range(n)
           if mask >> i & 1]
    print(mask, sub)
```

There are 2ⁿ subsets: about a million for 20 items and about a trillion for 40. Runtime also includes work per subset. The loop above checks n bit positions for each of the 2ⁿ masks:

```formula
T(n) = Θ(n × 2^n)
T(20) ≈ 20 × 1,048,576 ≈ 21,000,000
where
T(n): the number of elementary operations the loop performs for an n-element set
n: the number of elements
Θ( ): grows at the same rate as the expression inside, up to a constant factor (big-Theta notation)
≈: approximately equal to
In words: the work is roughly n bit checks for each of the 2^n subsets, so 20 items already cost about 21 million basic steps before any printing.
```

This assumes each bit check costs one step (a unit-cost model) and ignores the cost of formatting and printing.

The **Cartesian product** A × B is the set of all ordered pairs whose first part comes from A and whose second part comes from B. Every element of A is paired with every element of B, so the sizes multiply:

```formula
A × B = { (a, b) : a ∈ A and b ∈ B }
|A × B| = |A| × |B|
{1, 2} × {x, y}
  = {(1,x), (1,y), (2,x), (2,y)}
|{1, 2} × {x, y}| = 2 × 2 = 4
where
A, B: any two sets
a: an element of A
b: an element of B
x, y: the two elements of the example's second set
×: between sets, the Cartesian product; between numbers, ordinary multiplication
( , ): an ordered pair: order matters, so (1, x) and (x, 1) are different
∈: is an element of
| |: the cardinality: the number of elements
{ : }: the set of all things of the form before the colon that satisfy the condition after it
In words: the Cartesian product pairs every element of A with every element of B, so a 2-element set times a 2-element set gives 4 pairs.
```

A relational table is the same idea with more columns. Each column draws its values from a set of allowed values (its domain), and the table holds a set of rows chosen from all the combinations:

```formula
T ⊆ D_1 × D_2 × … × D_k
where
T: the set of rows in the table, each row a k-tuple (a list of k values in column order)
D_1, D_2, D_k: the domains: the sets of allowed values for column 1, column 2 and column k
k: the number of columns
×: Cartesian product
…: and so on, one factor per column
⊆: is a subset of
In words: a relation (in the database sense) is a set of rows chosen from all possible combinations of column values.
```

Real SQL tables go a little beyond this model: they can hold duplicate rows. An SQL CROSS JOIN combines every input-row occurrence with every occurrence on the other side, retaining duplicate multiplicities.

## Functions

A **function** assigns to every element of its **domain** exactly one element of its **codomain**. Two conditions: every input has an output, and no input has two outputs.

```formula
f : A → B
f(a) ∈ B   for every a ∈ A
where
f: the function's name
A: the domain: the set of allowed inputs
B: the codomain: the set the outputs are declared to lie in
a: any input taken from A
f(a): the single output f gives for input a
→: in "f : A → B", "maps elements of A to elements of B"
∈: is an element of
In words: f takes each element of A and gives back exactly one element of B.
```

The **image** (often called the range) is the set of outputs actually hit:

```formula
f(A) = { f(a) : a ∈ A }
f(A) ⊆ B
where
f(A): the image of f: every output that some input actually produces
f: a function from the set A to the set B
A: the domain, the set of inputs
B: the codomain
a: an input taken from A
f(a): the output for input a
∈: is an element of
⊆: is a subset of
{ : }: the set of all values f(a), one for each a in A
In words: the image collects every output f really produces. It is always inside the codomain and may be smaller.
```

For example, doubling an integer:

```formula
f : ℤ → ℤ,   f(x) = 2 × x
f(ℤ) = {…, −4, −2, 0, 2, 4, …}
where
f: the doubling function
x: an integer input
ℤ: the integers: …, −2, −1, 0, 1, 2, …
f(ℤ): the image of f: every output it actually produces
→: in "f : ℤ → ℤ", f takes integers and its declared codomain is the integers
…: and so on in both directions
In words: doubling hits only the even integers, so the image is smaller than the codomain: 3, for example, is in the codomain but never an output.
```

Three properties matter:

- **Injective** (one-to-one): different inputs give different outputs.
- **Surjective** (onto): every element of the codomain is hit by some input, so the image equals the codomain.
- **Bijective**: both. Every element of the codomain is hit by exactly one input, so f has an **inverse** function that undoes it.

In symbols, for a function f from A to B, the first line is injectivity, the second surjectivity, and the last two describe the inverse of a bijection:

```formula
f(x) = f(y) means x = y
∀ b ∈ B, ∃ a ∈ A such that f(a) = b
f^{−1} : B → A
f^{−1}(f(a)) = a   and   f(f^{−1}(b)) = b
where
f: a function from A to B
A: the domain, the set of inputs
B: the codomain, the set outputs lie in
x, y: any two inputs from A
a: an input from A
b: an element of the codomain B
∀: "for every"
∃: "there exists": at least one such element exists
f^{−1}: the inverse of f, read "f inverse": the function that sends each output back to the one input that produced it. The −1 is a label, not a power: f^{−1} is not 1 / f
∈: is an element of
→: in "f^{−1} : B → A", "maps elements of B to elements of A"
In words: injective means two inputs only share an output if they are the same input; surjective means every b in B is the output of at least one a; when both hold (bijective), every b has exactly one a, so f^{−1} can run f backwards and the round trip in either direction gets you back where you started.
```

```
injective    surjective   bijective
not onto     not 1-to-1
a -> 1       a -> 1       a -> 1
b -> 2       b -> 1       b -> 2
c -> 3       c -> 2       c -> 3
     4
```

In the left column nothing maps to 4, so the map is not onto. In the middle, a and b share 1, so it is not one-to-one. The right column is a perfect pairing.

For finite sets these properties limit the sizes. An injection from A to B can exist only when A is no bigger than B; a surjection only when A is at least as big as B; and a bijection only when they are the same size:

```formula
|A| ≤ |B|
|A| ≥ |B|
|A| = |B|
where
A: the domain, a finite set
B: the codomain, a finite set
| |: the cardinality: the number of elements
≤: is less than or equal to
≥: is greater than or equal to
In words: line 1 must hold for an injection (you cannot send more things to fewer places without two sharing), line 2 for a surjection (you cannot cover more places than you have things), and line 3 for a bijection (a perfect pairing needs equal sizes).
```

The first one is the **pigeonhole principle** in disguise: put 5 pigeons in 4 holes and two pigeons must share.

> [!example] Why hash functions collide
> Standard SHA-256 accepts messages shorter than 2⁶⁴ bits and produces one of 2²⁵⁶ outputs. Its finite input domain is still vastly larger than its output space. No function from a larger set to a smaller one can be injective, so collisions must exist. Cryptographic hashes are designed so that *finding* one is infeasible, not so that none exist.

### Composition and inverses

**Composition** chains two functions: apply one, then feed its output to the other.

```formula
(g ∘ f)(x) = g(f(x))
f(x) = x + 1,  g(y) = 2 × y
(g ∘ f)(3) = g(4) = 8
where
f: the first function applied, from A to B
g: the second function applied, from B to C
x: an input from the domain A of f
y: an input to g, from the set B
∘: composition, read "after": g ∘ f means "g after f"
In words: g ∘ f runs f first and then g on the result. With f adding 1 and g doubling, 3 becomes 4 and then 8. The order matters: f ∘ g would give 2 × 3 + 1 = 7.
```

Compositions preserve the properties above: two injections compose to an injection, two surjections to a surjection, and two bijections to a bijection.

If g ∘ f is injective, then f must be injective (if f merged two inputs, g could not separate them again). If a stage merges two reachable states that arose from distinct valid inputs, later deterministic stages cannot recover that distinction without additional information. Non-injectivity only on states the pipeline never reaches need not lose information.

### Counting functions

For finite sets, you can count how many functions of each kind exist. Each input chooses an output; for an injection, each choice must avoid the outputs already used.

```formula
N_all = n^m
N_inj = n! / (n − m)!   if m ≤ n
N_inj = 0   if m > n
N_bij = m!   when A = B
where
N_all: the number of functions from A to B
N_inj: the number of injections from A to B
N_bij: the number of bijections from A to itself

A: the domain, with m elements
B: the codomain, with n elements
m: the number of elements in A (the inputs)
n: the number of elements in B (the possible outputs)
n^m: m copies of n multiplied together
!: factorial: k! = k × (k − 1) × … × 2 × 1, with 0! = 1
≤: is less than or equal to
>: is greater than
In words: each of the m inputs freely picks one of n outputs, giving n^m functions; an injection must use a new output each time, giving n × (n − 1) × … for m factors; a bijection from a set to itself is a reordering (permutation), and there are m! of those.
```

A worked example with m = 3 inputs and n = 4 outputs:

```formula
n^m = 4^3 = 64
n! / (n − m)! = 4! / 1! = 4 × 3 × 2 = 24
where
n: the number of possible outputs, here 4
m: the number of inputs, here 3
!: factorial: the product of all whole numbers from 1 up to that number, so 4! = 24 and 1! = 1
In words: from a 3-element set to a 4-element set there are 64 functions, of which 24 never repeat an output.
```

Use the counting convention 0⁰ = 1 for the unique empty-domain function. There are 2⁸ = 256 functions from the 8 bit positions of a byte to {0, 1}: one per byte value.

## Functions in real code

The mathematical idea of a function is stricter than a programming "function". A routine whose result depends on changing hidden state may return different results for the same explicit arguments. Including the relevant state in the mathematical input gives a function again; reading an immutable constant does not itself violate determinism. Pure terminating routines fit the simple total-function model and can be easier to test, memoise and parallelise.

Bijections show up whenever you need a lossless round trip:

- **Serialisation**: `decode(encode(x)) == x` for every valid x is a requirement that `encode` is injective, and `decode` is its inverse on the image.
- **Base64, UTF-8, gzip**: with a fixed encoder configuration and appropriate valid input domain, lossless round trips require injectivity. Ordinary lossy JPEG and MP3 encoding merge distinct inputs; the JPEG family also includes lossless modes.
- **Primary keys**: projecting each row to its primary-key value uniquely identifies that row. A primary key combines uniqueness with non-nullness; a bare UNIQUE constraint can permit multiple nulls depending on the database and configuration.
- **Permutations in shuffles and ciphers**: a block cipher with a fixed key is a bijection on blocks, otherwise decryption would be ambiguous.

## Infinite sets have different sizes

For infinite sets you cannot count elements, so "same size" is defined by pairing them up: two sets have the same cardinality exactly when there is a bijection between them, so their elements pair off one-to-one with nothing left over on either side. This leads to surprises.

A set is **countable** if it is finite or in bijection with ℕ, the natural numbers 0, 1, 2, …: you can list its elements in a sequence that eventually reaches each one. ℤ (the integers) is countable, even though it seems twice as big, because this bijection lists it as 0, 1, −1, 2, −2, …:

```formula
f(n) = (n + 1) / 2   for n = 1, 3, 5, …
f(n) = −n / 2   for n = 0, 2, 4, …
|ℕ| = |ℤ|
where
ℕ: the natural numbers 0, 1, 2, 3, …
ℤ: the integers …, −2, −1, 0, 1, 2, …
f: a bijection from ℕ to ℤ
n: a natural number, the position in the list
f(n): the integer at position n
…: and so on without end
| |: the cardinality: the size of a set
In words: odd positions get the positive integers (1 → 1, 3 → 2, 5 → 3) and even positions get zero and the negatives (0 → 0, 2 → −1, 4 → −2). Every integer appears once and only once, so ℕ and ℤ have the same size.
```

So is ℚ (the fractions), and so is the set of all finite strings over a finite alphabet, which means **the set of all programs is countable**.

**Cantor's diagonal argument** shows that the set of infinite binary sequences (equivalently, the power set of ℕ, or the real numbers) is **not** countable. Suppose you had a complete list of sequences. Build a new sequence d by flipping the i-th bit of the i-th sequence:

```formula
d(i) = 1 − s_i(i)
d(i) ≠ s_i(i)   for every i
where
s_i: the i-th infinite 0/1 sequence in the supposedly complete list (s_1 first, s_2 second, …)
s_i(i): bit number i of sequence s_i: the bits on the diagonal
d: the new sequence being built
d(i): bit number i of d
i: a position, 1, 2, 3, …
≠: is not equal to
In words: d takes the diagonal bit of each listed sequence and flips it (1 − 0 = 1, 1 − 1 = 0), so d disagrees with every listed sequence somewhere and cannot be on the list.
```

```
s1 = 0 1 1 0 1 ...
s2 = 1 1 0 0 0 ...
s3 = 0 0 0 1 1 ...
s4 = 1 0 1 1 0 ...
d  = 1 0 1 0 ...   (flip diagonal)
```

The diagonal bits are 0, 1, 0, 1, so d starts 1, 0, 1, 0. It differs from s1 in position 1, from s2 in position 2, and so on, so it is not on the list, contradicting completeness. More generally, **Cantor's theorem** says every set is strictly smaller than its power set:

```formula
|P(A)| > |A|   for every A
where
A: any set, finite or infinite
P(A): the power set of A, the set of all its subsets
| |: the cardinality: the size of a set
>: is strictly larger than: there is an injection from A into P(A) but no bijection between them
In words: a set always has more subsets than elements. For finite sets this is 2^n > n; for infinite ones it means there is no largest infinity.
```

> [!note] Why CS cares
> Programs are countable but the set of functions from ℕ to {0, 1} (all possible yes/no problems) is not. So almost all problems have no program that solves them. The halting problem, covered in the computability module, is a concrete example built with the same diagonal trick.

## Pitfalls

- **Codomain versus image.** Whether a function is surjective depends on the declared codomain: squaring real numbers hits every non-negative real, but no negative one (see below).
- **Sets are unordered and deduplicated.** Converting a list to a set and back loses order and duplicates. Python sets only hold hashable elements, so use `frozenset` for a set of sets.
- **Off-by-one in power sets.** The count of subsets includes both the empty set and the whole set. "Non-empty subsets" is one fewer (see below).
- **"Function" in code is not always a function.** Changing hidden state can break the same-explicit-input/same-result rule; an output side effect can violate purity even when the returned result is deterministic.

The two numeric pitfalls in symbols:

```formula
f(x) = x^2,   f(ℝ) = [0, ∞)
N_ne = 2^n − 1
N_ne = 2^3 − 1 = 7   for n = 3
where
f: the squaring function, with domain ℝ
x: a real-number input
x^2: x multiplied by itself
ℝ: the real numbers: every point on the number line
f(ℝ): the image of f: every output it actually produces
[0, ∞): the non-negative reals: every real number from 0 upwards, with no upper limit
∞: infinity: the interval goes on without end
N_ne: the number of non-empty subsets
n: the number of elements in the set whose subsets you count
In words: squaring hits exactly the non-negative reals, so it is surjective if its declared codomain is [0, ∞) and not surjective if the codomain is all of ℝ (−1 is never an output). A set of n elements has 2^n subsets, and all but the empty one are non-empty: 7 for a 3-element set.
```

## Key takeaways
- A set is an unordered collection of distinct elements; union, intersection, difference and symmetric difference map to Python's |, &, - and ^; complement needs an explicit universe U, written U - A in Python.
- A set with n elements has 2ⁿ subsets, and a Cartesian product has as many pairs as the two sizes multiplied; bitmasks identify the 2ⁿ subsets, and listing each subset explicitly costs about n × 2ⁿ elementary operations in total.
- Injective means no collisions, surjective means every output is hit, bijective means both and implies an inverse.
- From a larger finite set to a smaller one no injection exists, which is why hash collisions are unavoidable.
- Countable sets can be listed; Cantor's diagonal argument shows the power set of ℕ cannot, so most problems have no program.

## Further reading
- [Set (mathematics) — Wikipedia](https://en.wikipedia.org/wiki/Set_(mathematics))
- [Bijection, injection and surjection — Wikipedia](https://en.wikipedia.org/wiki/Bijection)
- [Cantor's diagonal argument — Wikipedia](https://en.wikipedia.org/wiki/Cantor%27s_diagonal_argument)
- [Mathematics for Computer Science (Lehman, Leighton, Meyer), MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
- [Mathematics for Computer Science — MIT OpenCourseWare](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/)
