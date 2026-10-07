---
id: cx-asymptotic-notation
title: Big-O, Big-Omega and Big-Theta
level: basic
minutes: 10
summary: The formal definitions behind asymptotic notation, how to prove a bound, why constants and lower-order terms vanish, and the ladder of common complexity classes from O(1) to O(n!).
---

The last lesson said we keep the fastest-growing term and drop constants. **Asymptotic notation** is the precise language for doing that. It describes how a function behaves as n grows towards infinity, which is why it is called *asymptotic*.

There are three main symbols. Think of them as comparisons between growth rates:

| Notation | Read as | Like |
|---|---|---|
| f = O(g) | f grows no faster than g | f ≤ g |
| f = Ω(g) | f grows at least as fast as g | f ≥ g |
| f = Θ(g) | f grows at the same rate as g | f = g |

Here f is usually the exact operation count of an algorithm and g is a simple function such as `n^2`.

## Big-O: an upper bound

**Definition.** `f(n) = O(g(n))` if there exist constants `c > 0` and `n0` such that

```
0 <= f(n) <= c * g(n)   for all n >= n0
```

In words: beyond some starting point n0, f never exceeds a fixed multiple of g.

The two constants are what let us ignore details. `c` absorbs constant factors (a faster machine, a different way of counting). `n0` lets us ignore small inputs, where odd things can happen.

### Proving a Big-O bound

Claim: `f(n) = 3n^2 + 5n + 2` is `O(n^2)`.

We need to find c and n0. For `n >= 1`, we know `n <= n^2` and `1 <= n^2`, so we can replace each smaller term with `n^2`:

```
3n^2 + 5n + 2
  <= 3n^2 + 5n^2 + 2n^2
  =  10n^2         for n >= 1
```

So `c = 10` and `n0 = 1` work. Any larger c or n0 would also work; you only need one pair.

A quick table confirms it:

```
  n    3n^2+5n+2     10n^2
  1           10        10
  2           24        40
 10          352     1,000
100       30,502   100,000
```

The ratio f/g settles towards 3. The bound with c = 10 is loose, but loose is fine for Big-O.

### Disproving one

Claim: `n^2` is **not** `O(n)`.

Suppose it were. Then `n^2 <= c * n` for all `n >= n0`. Dividing by n gives `n <= c`. But n keeps growing and c is fixed, so this fails as soon as `n > c`. Contradiction.

For eventually positive g, showing `f(n) / g(n)` tends to infinity disproves O(g), but is not necessary: the ratio may oscillate. The general requirement is that for every c and n0, some n ≥ n0 has f(n) > c g(n).

## Big-Omega: a lower bound

**Definition.** `f(n) = Ω(g(n))` if there exist `c > 0` and `n0` such that

```
f(n) >= c * g(n) >= 0   for all n >= n0
```

For `3n^2 + 5n + 2`, take `c = 3`: the extra terms are positive, so `f(n) >= 3n^2` for every `n >= 0`. Hence `f = Ω(n^2)`.

Omega is used to say "at least this much work is unavoidable". A famous example you will meet later: any sorting algorithm that only compares elements needs `Ω(n log n)` comparisons in the worst case.

## Big-Theta: a tight bound

**Definition.** `f(n) = Θ(g(n))` if f is both `O(g)` and `Ω(g)`. That is, there exist `c1, c2 > 0` and `n0` with

```
c1*g(n) <= f(n) <= c2*g(n)   for n >= n0
```

We showed `3 n^2 <= 3n^2 + 5n + 2 <= 10 n^2` for `n >= 1`, so `f = Θ(n^2)`. Theta is the most informative statement: it pins the growth rate down exactly, up to constants.

> [!note] Industry "Big-O" usually means Theta
> Strictly, O is only an upper bound. Binary search is `O(log n)`, but it is also `O(n)` and `O(n^2)`, because those are bigger. All true, the last two useless. When engineers say "this is O(n)", they almost always mean "this is Θ(n)": the bound is tight. In interviews and code reviews, give the tightest bound you can.

## The limit test

A quick way to compare two functions is to look at the ratio as n grows:

| lim f(n)/g(n) | Conclusion |
|---|---|
| 0 | f = O(g), not Ω(g) |
| constant > 0 | f = Θ(g) |
| ∞ | f = Ω(g), not O(g) |

For example, `n / n^2 = 1/n`, which goes to 0, so `n = O(n^2)` but not `Θ(n^2)`. When the limit is 0 we also write `f = o(g)` ("little-o"): f grows strictly slower than g.

## Simplification rules

These all follow from the definitions:

- **Constants vanish.** `5n^2 = Θ(n^2)`. The constant goes into c.
- **Sums take the maximum.** `n^3 + 100n^2 + 10^6 = Θ(n^3)`. Lower-order terms are eventually dwarfed.
- **Log bases do not matter.** `log_a n = log_b n / log_b a`, which differs only by the constant `1 / log_b a`. So we just write `O(log n)`.
- **Exponent bases do matter.** `3^n / 2^n = 1.5^n`, which grows without limit, so `3^n` is not `O(2^n)`. Likewise `4^n = 2^(2n)` is not `O(2^n)`.
- **Polynomials beat logs, exponentials beat polynomials.** `(log n)^100 = o(n^0.01)` and `n^100 = o(1.01^n)`, even though both look backwards for small n.
- **Products multiply.** If one loop is `Θ(n)` and its body is `Θ(log n)`, the whole is `Θ(n log n)`.

> [!warning] The "=" is one-way
> `f = O(g)` really means "f belongs to the set of functions bounded by g". So `n = O(n^2)` is true but `O(n^2) = n` is meaningless, and from `f = O(n^2)` and `g = O(n^2)` you cannot conclude `f = g`. Some books write `f ∈ O(g)` to make this clear.

## The ladder of common classes

From slowest-growing to fastest, with typical examples (most are covered properly in later modules):

| Class | Name | Example |
|---|---|---|
| O(1) | constant | array index |
| O(log n) | logarithmic | binary search |
| O(sqrt n) | square root | divisors up to sqrt n |
| O(n) | linear | scan a list |
| O(n log n) | linearithmic | merge sort |
| O(n^2) | quadratic | all pairs |
| O(n^3) | cubic | naive matrix multiply |
| O(2^n) | exponential | all subsets |
| O(n!) | factorial | all orderings |

A few points worth knowing:

- **O(1)** means bounded by a constant, not "one step". Reading 1,000 fixed fields is still O(1).
- **O(log n)** is what you get by repeatedly halving the problem. `log2` of a billion is about 30.
- **n!** grows faster than any `c^n`. By Stirling's approximation, `log(n!) = Θ(n log n)`, which is where the sorting lower bound comes from. 20! is about 2.4 x 10^18; 25! is about 1.6 x 10^25.
- **Multiple variables** are fine and often necessary. A graph algorithm might be `O(V + E)`; joining two lists might be `O(n + m)`. Do not collapse them into one n unless you know how they relate.

## Not every function has a tidy Theta

Consider a function that does `n` work when n is even and 1 unit of work when n is odd. It is `O(n)` and `Ω(1)`, but it is neither Θ(n) nor Θ(1). A tight bound still exists: trivially f = Θ(f), or use the same piecewise expression as g. It simply does not match one of the usual monotone growth classes.

## Big-O is not "worst case"

A very common confusion. **O, Ω and Θ describe functions. Best, average and worst case describe which input you are talking about.** They are independent:

- Insertion sort's worst-case time is `Θ(n^2)`.
- Its best-case time (already-sorted input) is `Θ(n)`.
- So its running time overall is `O(n^2)` and `Ω(n)`.

You can put a Θ on the worst case, an O on the average case, and so on. Lesson 3 covers cases in detail.

## Key takeaways
- `f = O(g)`: f is eventually at most a constant times g (upper bound). `Ω` is the lower bound; `Θ` is both, a tight bound.
- To prove a bound, exhibit constants c and n0. To disprove, show that no eventual constant upper bound contains f/g (a limit of infinity is sufficient).
- Constants and lower-order terms disappear; log bases do not matter; exponent bases do.
- The ladder: 1 < log n < sqrt n < n < n log n < n^2 < n^3 < 2^n < n!.
- In practice "Big-O" usually means a tight bound. Give the tightest one you can.
- Asymptotic notation and best/average/worst case are separate ideas.

## Further reading
- [Big O notation — Wikipedia](https://en.wikipedia.org/wiki/Big_O_notation)
- [Asymptotic analysis — Wikipedia](https://en.wikipedia.org/wiki/Asymptotic_analysis)
- [Stirling's approximation — Wikipedia](https://en.wikipedia.org/wiki/Stirling%27s_approximation)
- [Algorithms by Jeff Erickson (free textbook)](https://jeffe.cs.illinois.edu/teaching/algorithms/)
- [Big-O cheat sheet](https://www.bigocheatsheet.com/)
