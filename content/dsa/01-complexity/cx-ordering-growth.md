---
id: cx-ordering-growth
sourceLesson: cx-asymptotic-notation
title: Ordering growth with limits
level: basic
minutes: 5
summary: Use ratios and the growth ladder to compare unfamiliar cost functions.
---

Here n is the input size; logarithms use base 2 unless a different base is stated. Use the simplification rules and ratio limits together.

## The limit test

A quick way to compare two functions is to look at what their ratio does as n grows without limit:

```formula
L = lim_{n→∞} f(n) / g(n)
L = 0: f(n) = O(g(n))
L = 0: f(n) = o(g(n))
L = 0: f(n) ∉ Ω(g(n))
0 < L < ∞: f(n) = Θ(g(n))
L = ∞: f(n) = Ω(g(n))
L = ∞: f(n) ∉ O(g(n))
where
L: the value the ratio settles towards
lim_{n→∞}: "the limit as n tends to infinity": the value f(n) / g(n) gets closer and closer to as n grows without bound
n: the input size
f(n), g(n): the two functions being compared, both positive for large n
∞: infinity: growing without any upper limit
→: "tends to", "heads towards"
O: an eventual upper growth bound
Ω: an eventual lower growth bound
Θ: matching upper and lower growth bounds
o: strictly slower growth
∉: is not a member of the indicated growth class
<: less than
In words: divide one function by the other and watch what the answer heads towards as n gets enormous.
```

| Ratio limit | Conclusion |
|---|---|
| Zero | upper bound, no lower bound |
| Finite positive constant | tight bound |
| Infinity | lower bound, no upper bound |

For example, compare the linear and quadratic functions in the following substitution:

```formula
f(n) / g(n) = n / n^2 = 1 / n
1 / n → 0   as n → ∞
f(n) = n, g(n) = n^2
where
f(n): here n, a linear function
g(n): here n^2, n × n
n: the input size
→: "tends to"
∞: infinity, growing without limit
In words: n divided by n squared shrinks towards zero, so n grows strictly slower than n squared.
```

The linear function therefore has a quadratic upper bound but no quadratic tight bound. A zero ratio limit is also called **little-o**: strictly slower growth. The limit test only works when a limit exists; for oscillating functions, return to the definitions.

## The ladder of common classes

From slowest to fastest, these classes use n for input size. Logarithms are base two, a square root means the nonnegative root, and factorial is the product of all positive integers up to the item count. Most example algorithms are studied later.

| Class | Name | Example |
|---|---|---|
| O(1) | constant | array index |
| O(log n) | logarithmic | binary search |
| O(√n) | square root | divisors up to the square root |
| O(n) | linear | scan a list |
| O(n log n) | linearithmic | merge sort |
| O(n^2) | quadratic | all pairs |
| O(n^3) | cubic | naive matrix multiply |
| O(2^n) | exponential | all subsets |
| O(n!) | factorial | all orderings |

A few points worth knowing:

- **O(1)** means bounded by a constant, not "one step". Reading 1,000 fixed fields is still O(1).
- **O(log n)** is what you get by repeatedly halving the problem. The base-2 log of a billion is about 30, because 2^30 ≈ 1.07 billion.
- **Factorial** grows faster than any exponential with a fixed base. Stirling’s approximation gives its size; taking its logarithm gives the comparison-sorting lower bound:

```formula
n! = n(n − 1) × … × 2 × 1
log(n!) = Θ(n log(n))
20! ≈ 2.4 × 10^18
25! ≈ 1.6 × 10^25
where
n!: n factorial: the number of different orders n items can be arranged in
n: a whole number, here the number of items
…: "and so on": every whole number in between
log: the logarithm (base 2 here; the base only changes a constant)
Θ: Big-Theta: grows at the same rate as, up to constant factors
≈: approximately equal to
In words: the number of orderings of n items is astronomically large, but its logarithm grows only like n log n.
```

- **Multiple variables** are fine and often necessary. A graph algorithm might be O(V + E), where V is the number of vertices and E the number of edges; joining two lists of lengths n and m might be O(n + m). Do not collapse them into one n unless you know how they relate.

## Key takeaways
- A ratio limit compares growth when that limit exists.
- Polynomial, exponential and factorial functions can be ordered by their eventual growth.
- The logarithm of a factorial grows like the item count times its logarithm.

## Further reading
- [Big O notation — Wikipedia](https://en.wikipedia.org/wiki/Big_O_notation)
- [Stirling's approximation — Wikipedia](https://en.wikipedia.org/wiki/Stirling%27s_approximation)
