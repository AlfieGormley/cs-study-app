---
id: cx-tight-bounds
sourceLesson: cx-asymptotic-notation
title: Lower and tight bounds
level: basic
minutes: 4
summary: Distinguish lower bounds, tight bounds and input cases.
---

Here n is the input size. A lower bound and a tight bound add information that an upper bound alone cannot provide.

## Big-Omega: a lower bound

**Definition.** Big-Omega is the mirror image: f is eventually at least a fixed positive multiple of g.

```formula
f(n) = Ω(g(n))  means:
f(n) ≥ c g(n) ≥ 0  for all n ≥ n_0
f(n) = 3n^2 + 5n + 2
f(n) ≥ 3n^2 for n ≥ 0
c = 3
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

The quadratic polynomial from the upper-bound example also has a quadratic lower bound: its remaining terms are nonnegative. The example follows the definition below.

Omega is used to say "at least this much work is unavoidable". A famous example you will meet later: any sorting algorithm that only compares elements needs Ω(n log n) comparisons in the worst case, where n is the number of items being sorted.

## Big-Theta: a tight bound

**Definition.** Big-Theta says f is squeezed between two multiples of g, so it is both O(g) and Ω(g):

```formula
f(n) = Θ(g(n))  means:
c_1 × g(n) ≤ f(n) ≤ c_2 × g(n)
for all n ≥ n_0
3n^2 ≤ 3n^2 + 5n + 2 ≤ 10n^2
c_1 = 3, c_2 = 10, n_0 = 1
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

The same polynomial is squeezed between the two quadratic multiples below. This makes Theta the most informative statement: it pins growth down up to constants.

> [!note] Industry "Big-O" usually means Theta
> Strictly, O is only an upper bound. Binary search on n items is O(log n), but it is also O(n) and O(n^2), because those are bigger. All true, the last two useless. When engineers say "this is O(n)", they almost always mean "this is Θ(n)": the bound is tight. In interviews and code reviews, give the tightest bound you can.

## Not every function has a tidy Theta

Consider a function doing one step on odd input sizes and as many steps as the input size on even sizes. It is O(n) and Ω(1), where n is the input size, but neither Θ(n) nor Θ(1). A tight bound still exists: every function has its own growth rate as a tight bound, or use that same piecewise cost as the comparison. It simply does not match a familiar monotone growth class.

## Big-O is not "worst case"

A very common confusion. **O, Ω and Θ describe functions. Best, average and worst case describe which input you are talking about.** They are independent. For insertion sort on n items:

- Its worst-case time is Θ(n^2).
- Its best-case time (already-sorted input) is Θ(n).
- So its running time overall is O(n^2) and Ω(n).

You can put a Θ on the worst case, an O on the average case, and so on. The code-analysis lessons cover cases in detail.

## Key takeaways
- A tight bound combines an upper and lower bound for the same cost function.
- Best, average and worst cases describe inputs; asymptotic notation describes the resulting functions.
- An irregular function need not fit a familiar monotone growth class.

## Further reading
- [Big O notation — Wikipedia](https://en.wikipedia.org/wiki/Big_O_notation)
- [Asymptotic analysis — Wikipedia](https://en.wikipedia.org/wiki/Asymptotic_analysis)
