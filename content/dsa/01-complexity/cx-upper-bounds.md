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

| Notation | Read as | Like |
|---|---|---|
| f = O(g) | f grows no faster than g | f ≤ g |
| f = Ω(g) | f grows at least as fast as g | f ≥ g |
| f = Θ(g) | f grows at the same rate as g | f = g |

O is the capital letter O ("Big-O"), Ω is the Greek capital omega ("Big-Omega") and Θ is the Greek capital theta ("Big-Theta"). Here f is usually the exact operation count of an algorithm and g is a simple function such as n^2 (n × n).

## Big-O: an upper bound

**Definition.** Big-O says f is eventually no bigger than a fixed multiple of g:

```formula
f(n) = O(g(n))  means:
0 ≤ f(n) ≤ c × g(n)  for all n ≥ n_0
where
f(n): the function being described, usually the number of operations an algorithm does on an input of size n
g(n): the simple comparison function, such as n or n^2
n: the input size, a whole number
O(g(n)): Big-O of g: the set of all functions that are eventually at most a constant times g(n)
c: some fixed positive constant (c > 0) that you get to choose; it must not depend on n
n_0: a threshold input size you also get to choose; the inequality only has to hold from there on
≤, ≥: less than or equal to, greater than or equal to
In words: beyond some starting point n_0, f never exceeds a fixed multiple of g.
```

The two constants are what let us ignore details. c absorbs constant factors (a faster machine, a different way of counting). n_0 lets us ignore small inputs, where odd things can happen.

### Proving a Big-O bound

To prove a Big-O claim you find one pair of constants c and n_0 that makes the definition true. Take the claim that f(n) = 3n^2 + 5n + 2 is O(n^2). For n of at least 1 we know n ≤ n^2 and 1 ≤ n^2, so we can replace each smaller term with n^2, which can only make the right-hand side bigger:

```formula
f(n) = 3 × n^2 + 5 × n + 2
f(n) ≤ 3 × n^2 + 5 × n^2 + 2 × n^2
f(n) ≤ 10 × n^2   for n ≥ 1
where
f(n): the exact operation count being bounded
n: the input size, a whole number of at least 1
n^2: n squared, n × n
≤, ≥: less than or equal to, greater than or equal to
In words: once n is at least 1, f(n) is never more than 10 times n^2, so c = 10 and n_0 = 1 prove that f(n) = O(n^2).
```

So c = 10 and n_0 = 1 work. Any larger c or n_0 would also work; you only need one pair.

A quick table confirms it:

| n | 3n^2+5n+2 | 10n^2 |
|---|---|---|
| 1 | 10 | 10 |
| 2 | 24 | 40 |
| 10 | 352 | 1,000 |
| 100 | 30,502 | 100,000 |

The ratio f(n) / n^2 settles towards 3 (at n = 100 it is 30,502 / 10,000 ≈ 3.05). The bound with c = 10 is loose, but loose is fine for Big-O.

### Disproving one

To disprove a Big-O claim you show that no choice of constants can work. Claim: n^2 is **not** O(n). Suppose it were:

```formula
n^2 ≤ c × n   for all n ≥ n_0
n ≤ c   for all n ≥ n_0
where
n: the input size, a positive whole number
n^2: n squared, n × n
c: the fixed positive constant the definition of O(n) would need
n_0: the threshold input size the definition would need
≤, ≥: less than or equal to, greater than or equal to
O(n): Big-O of n: functions eventually at most a constant times n
In words: dividing both sides of the first line by n (which is positive, so ≤ stays the same way round) gives the second line: if n squared were O(n), then n itself would have to stay below a fixed number c forever, which it does not.
```

But n keeps growing and c is fixed, so this fails as soon as n is bigger than c. Contradiction.

For an eventually positive g, showing that the ratio f(n) / g(n) tends to infinity disproves f = O(g), but it is not necessary: the ratio may oscillate. The general requirement is that for every c and n_0, some n of at least n_0 has f(n) > c × g(n).

## Key takeaways
- An upper bound eventually holds with one fixed multiplier.
- Proving a bound means choosing constants that work for every sufficiently large input.
- A valid upper bound may be looser than useful.

## Further reading
- [Big O notation — Wikipedia](https://en.wikipedia.org/wiki/Big_O_notation)
- [Algorithms by Jeff Erickson (free textbook)](https://jeffe.cs.illinois.edu/teaching/algorithms/)
