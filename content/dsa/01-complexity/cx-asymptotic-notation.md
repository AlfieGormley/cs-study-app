---
id: cx-asymptotic-notation
title: Big-O, Big-Omega and Big-Theta
level: basic
minutes: 14
summary: The formal definitions behind asymptotic notation, how to prove a bound, why constants and lower-order terms vanish, and the ladder of common complexity classes from O(1) to O(n!).
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

## Big-Omega: a lower bound

**Definition.** Big-Omega is the mirror image: f is eventually at least a fixed positive multiple of g.

```formula
f(n) = Ω(g(n))  means:
f(n) ≥ c × g(n) ≥ 0  for all n ≥ n_0
where
f(n): the function being described, usually an operation count
g(n): the simple comparison function
n: the input size, a whole number
Ω(g(n)): Big-Omega of g (Ω is the Greek capital omega): the set of functions that are eventually at least a positive constant times g(n)
c: some fixed positive constant (c > 0) that does not depend on n
n_0: a threshold input size; the inequality must hold from there on
≥: greater than or equal to
In words: beyond some starting point, f never drops below a fixed fraction of g.
```

For f(n) = 3n^2 + 5n + 2, take c = 3: the extra terms 5n and 2 are never negative, so f(n) ≥ 3n^2 for every n ≥ 0. Hence f = Ω(n^2).

Omega is used to say "at least this much work is unavoidable". A famous example you will meet later: any sorting algorithm that only compares elements needs Ω(n log n) comparisons in the worst case, where n is the number of items being sorted.

## Big-Theta: a tight bound

**Definition.** Big-Theta says f is squeezed between two multiples of g, so it is both O(g) and Ω(g):

```formula
f(n) = Θ(g(n))  means:
c_1 × g(n) ≤ f(n) ≤ c_2 × g(n)
for all n ≥ n_0
where
f(n): the function being described, usually an operation count
g(n): the simple comparison function
n: the input size, a whole number
Θ(g(n)): Big-Theta of g (Θ is the Greek capital theta): functions that grow at the same rate as g(n), up to constant factors
c_1: a fixed positive constant for the lower bound
c_2: a fixed positive constant for the upper bound
n_0: a threshold input size; both inequalities must hold from there on
≤, ≥: less than or equal to, greater than or equal to
In words: beyond some point, f stays between two fixed multiples of g, so it grows at exactly g's rate.
```

We showed 3n^2 ≤ 3n^2 + 5n + 2 ≤ 10n^2 for every n of at least 1, so c_1 = 3, c_2 = 10 and n_0 = 1 give f = Θ(n^2). Theta is the most informative statement: it pins the growth rate down exactly, up to constants.

> [!note] Industry "Big-O" usually means Theta
> Strictly, O is only an upper bound. Binary search on n items is O(log n), but it is also O(n) and O(n^2), because those are bigger. All true, the last two useless. When engineers say "this is O(n)", they almost always mean "this is Θ(n)": the bound is tight. In interviews and code reviews, give the tightest bound you can.

## The limit test

A quick way to compare two functions is to look at what their ratio does as n grows without limit:

```formula
L = lim_{n→∞} f(n) / g(n)
where
L: the value the ratio settles towards
lim_{n→∞}: "the limit as n tends to infinity": the value f(n) / g(n) gets closer and closer to as n grows without bound
n: the input size
f(n), g(n): the two functions being compared, both positive for large n
∞: infinity: growing without any upper limit
→: "tends to", "heads towards"
In words: divide one function by the other and watch what the answer heads towards as n gets enormous.
```

| L | Conclusion |
|---|---|
| 0 | f = O(g), not Ω(g) |
| constant > 0 | f = Θ(g) |
| ∞ | f = Ω(g), not O(g) |

For example, with f(n) = n and g(n) = n^2:

```formula
f(n) / g(n) = n / n^2 = 1 / n
1 / n → 0   as n → ∞
where
f(n): here n, a linear function
g(n): here n^2, n × n
n: the input size
→: "tends to"
∞: infinity, growing without limit
In words: n divided by n squared shrinks towards zero, so n grows strictly slower than n squared.
```

So n = O(n^2) but not Θ(n^2). When the limit is 0 we also write f = o(g) ("little-o", a lower-case o): f grows strictly slower than g. The limit test only works when the limit exists; for oscillating functions go back to the definitions.

## Simplification rules

These all follow from the definitions. In each, n is the input size:

- **Constants vanish.** 5n^2 = Θ(n^2). The constant 5 goes into c.
- **Sums take the maximum.** n^3 + 100n^2 + 10^6 = Θ(n^3). Lower-order terms are eventually dwarfed.
- **Log bases do not matter.** Any two logarithms of n differ only by a constant factor (shown below), so we just write O(log n).
- **Exponent bases do matter.** 3^n is not O(2^n), and neither is 4^n (shown below).
- **Polynomials beat logs, exponentials beat polynomials.** (log n)^100 = o(n^0.01) and n^100 = o(1.01^n), even though both look backwards for small n.
- **Products multiply.** If one loop runs Θ(n) times and its body costs Θ(log n), the whole is Θ(n log n).

Why log bases don't matter: the change-of-base rule turns a log in one base into a log in another by dividing by a constant.

```formula
log_a(n) = log_b(n) / log_b(a)
log_2(n) = log_10(n) / log_10(2)
log_2(n) ≈ 3.32 × log_10(n)
where
log_a(n): the logarithm of n to base a: the power you raise a to in order to get n
log_b(n): the logarithm of n to base b
log_b(a): the logarithm of a to base b, a fixed number because a and b are fixed
log_2(n): the base-2 logarithm of n
log_10(n): the base-10 logarithm of n (log_10(1000) = 3)
a, b: any two fixed bases greater than 1
n: the input size
≈: approximately equal to
In words: switching the base of a logarithm just multiplies it by a constant, and Big-O ignores constants, so O(log_2 n) and O(log_10 n) are the same class.
```

Why exponent bases do matter: dividing one exponential by another leaves an exponential, not a constant.

```formula
3^n / 2^n = (3 / 2)^n = 1.5^n
4^n = (2^2)^n = 2^{2 × n}
4^n / 2^n = 2^n
where
3^n: n copies of 3 multiplied together
2^n: n copies of 2 multiplied together
4^n: n copies of 4 multiplied together
1.5^n: n copies of 1.5 multiplied together, which grows without limit
n: the input size
In words: the ratio of two exponentials with different bases keeps growing, so no constant c can cover it and the faster one is not Big-O of the slower one.
```

> [!warning] The "=" is one-way
> f = O(g) really means "f belongs to the set of functions bounded by g". So n = O(n^2) is true but "O(n^2) = n" is meaningless, and from f = O(n^2) and g = O(n^2) you cannot conclude f = g. Some books write f ∈ O(g) (∈ means "is a member of") to make this clear.

## The ladder of common classes

From slowest-growing to fastest, with typical examples (most are covered properly in later modules). n is the input size; log n is log_2(n); √n is the square root of n; n! is n factorial, n × (n − 1) × … × 2 × 1:

| Class | Name | Example |
|---|---|---|
| O(1) | constant | array index |
| O(log n) | logarithmic | binary search |
| O(√n) | square root | divisors up to √n |
| O(n) | linear | scan a list |
| O(n log n) | linearithmic | merge sort |
| O(n^2) | quadratic | all pairs |
| O(n^3) | cubic | naive matrix multiply |
| O(2^n) | exponential | all subsets |
| O(n!) | factorial | all orderings |

A few points worth knowing:

- **O(1)** means bounded by a constant, not "one step". Reading 1,000 fixed fields is still O(1).
- **O(log n)** is what you get by repeatedly halving the problem. The base-2 log of a billion is about 30, because 2^30 ≈ 1.07 billion.
- **n!** (factorial) grows faster than c^n for any fixed number c. Stirling's approximation gives the size of a factorial, and taking its logarithm shows where the sorting lower bound comes from:

```formula
n! = n × (n − 1) × … × 2 × 1
log(n!) = Θ(n × log(n))
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

## Not every function has a tidy Theta

Consider a function that does n units of work when n is even and 1 unit of work when n is odd. It is O(n) and Ω(1), but it is neither Θ(n) nor Θ(1). A tight bound still exists: trivially f = Θ(f), or use the same piecewise expression as g. It simply does not match one of the usual monotone (steadily increasing) growth classes.

## Big-O is not "worst case"

A very common confusion. **O, Ω and Θ describe functions. Best, average and worst case describe which input you are talking about.** They are independent. For insertion sort on n items:

- Its worst-case time is Θ(n^2).
- Its best-case time (already-sorted input) is Θ(n).
- So its running time overall is O(n^2) and Ω(n).

You can put a Θ on the worst case, an O on the average case, and so on. Lesson 3 covers cases in detail.

## Key takeaways
- f = O(g): f is eventually at most a constant times g (upper bound). Ω is the lower bound; Θ is both, a tight bound.
- To prove a bound, exhibit constants c and n_0. To disprove, show that no eventual constant upper bound contains f/g (a limit of infinity is sufficient).
- Constants and lower-order terms disappear; log bases do not matter (they differ by a constant factor); exponent bases do.
- The ladder: 1 < log n < √n < n < n log n < n^2 < n^3 < 2^n < n!.
- In practice "Big-O" usually means a tight bound. Give the tightest one you can.
- Asymptotic notation and best/average/worst case are separate ideas.

## Further reading
- [Big O notation — Wikipedia](https://en.wikipedia.org/wiki/Big_O_notation)
- [Asymptotic analysis — Wikipedia](https://en.wikipedia.org/wiki/Asymptotic_analysis)
- [Stirling's approximation — Wikipedia](https://en.wikipedia.org/wiki/Stirling%27s_approximation)
- [Algorithms by Jeff Erickson (free textbook)](https://jeffe.cs.illinois.edu/teaching/algorithms/)
- [Big-O cheat sheet](https://www.bigocheatsheet.com/)
