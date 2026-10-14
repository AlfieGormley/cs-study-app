---
id: cx-upper-bounds
sourceLesson: cx-asymptotic-notation
title: Proving an upper bound
level: basic
minutes: 5
summary: Use fixed constants to prove or disprove a Big-O claim.
---

The last lesson said we keep the fastest-growing term and drop constants. **Asymptotic notation** is the precise language for doing that. It describes how a function behaves as n, the input size, grows towards infinity, which is why it is called *asymptotic*.

There are three main symbols. Think of them as comparisons between growth rates, where f and g are two functions of n:

| Notation | Read as | Pointwise analogy |
|---|---|---|
| Big-O | upper growth bound | no greater than |
| Big-Omega | lower growth bound | no smaller than |
| Big-Theta | tight growth bound | equality |

O is the capital letter O ("Big-O"), Ω is Greek capital omega and Θ is Greek capital theta. Here f is the exact operation-count function and g a simpler comparison function, often quadratic. These labels compare eventual growth, rather than literal pointwise inequalities.

## Big-O: an upper bound

**Definition.** Big-O says f is eventually no bigger than a fixed multiple of g:

```formula
f(n) = O(g(n))  means:
0 ≤ f(n) ≤ c g(n)  for all n ≥ n_0
where
f(n): the algorithm’s operation-count function
g(n): the simpler comparison function
n: the input size, a whole number
O(g(n)): functions eventually bounded by a fixed multiple of g(n)
c: a chosen fixed positive multiplier, independent of input size
n_0: the chosen input threshold where the bound starts
≤, ≥: less than or equal to, greater than or equal to
In words: beyond some starting point n_0, f never exceeds a fixed multiple of g.
```

The two constants are what let us ignore details. c absorbs constant factors (a faster machine, a different way of counting). n_0 lets us ignore small inputs, where odd things can happen.

### Proving a Big-O bound

To prove a Big-O claim, find fixed constants that make its definition true. The example below bounds a quadratic polynomial by replacing its smaller terms with quadratic terms, which only increases the right-hand side.

```formula
f(n) = 3n^2 + 5n + 2
f(n) ≤ 3n^2 + 5n^2 + 2n^2
f(n) ≤ 10n^2   for n ≥ 1
n ≤ n^2 and 1 ≤ n^2 for n ≥ 1
c = 10, n_0 = 1
f(100) / 100^2 = 30502 / 10000 ≈ 3.05
where
f(n): the exact operation count being bounded
n: the input size, a whole number of at least 1
≤, ≥: less than or equal to, greater than or equal to
c: the fixed upper-bound multiplier
n_0: the first input size for the bound
≈: approximately equal
In words: once n is at least 1, f(n) is never more than 10 times n^2, so c = 10 and n_0 = 1 prove that f(n) = O(n^2).
```

These constants work. Any larger multiplier or starting threshold also works; one pair suffices.

A quick table confirms it:

| Items | Exact count | Upper limit |
|---|---|---|
| 1 | 10 | 10 |
| 2 | 24 | 40 |
| 10 | 352 | 1,000 |
| 100 | 30,502 | 100,000 |

The ratio of the polynomial to the square settles towards 3. The card evaluates it at 100 items, giving about 3.05. A multiplier of 10 is loose, but loose is fine for Big-O.

### Disproving one

To disprove a Big-O claim, show that no fixed constants can work. A quadratic function is **not** O(n), where n is the input size. Suppose that bound were possible:

```formula
n^2 ≤ cn   for all n ≥ n_0
n ≤ c   for all n ≥ n_0
for every c > 0 and every n_0:
some n ≥ n_0: f(n) > cg(n)
where
n: the input size, a positive whole number
c: the fixed positive constant the definition of O(n) would need
n_0: the threshold input size the definition would need
≤, ≥: less than or equal to, greater than or equal to
O(n): Big-O of n: functions eventually at most a constant times n
f(n): the count whose proposed upper bound is being disproved
g(n): the eventually positive comparison function
>: greater than
In words: division by positive input forces that input below a fixed multiplier forever, a contradiction. Generally, every proposed multiplier and threshold must fail at some later input.
```

But n keeps growing and c is fixed, so this fails as soon as n is bigger than c. Contradiction.

A ratio tending to infinity disproves an upper bound for an eventually positive comparison function. It is sufficient, not necessary: ratios can oscillate. The card’s final condition gives the general negation.

## Key takeaways
- An upper bound eventually holds with one fixed multiplier.
- Proving a bound means choosing constants that work for every sufficiently large input.
- A valid upper bound may be looser than useful.

## Further reading
- [Big O notation — Wikipedia](https://en.wikipedia.org/wiki/Big_O_notation)
- [Algorithms by Jeff Erickson (free textbook)](https://jeffe.cs.illinois.edu/teaching/algorithms/)
