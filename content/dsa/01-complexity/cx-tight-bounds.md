---
id: cx-tight-bounds
sourceLesson: cx-asymptotic-notation
title: Lower and tight bounds
level: basic
minutes: 2
summary: Distinguish lower bounds, tight bounds and input cases.
---

An upper bound says how fast a cost can grow. A lower bound says how slowly it cannot grow. A tight bound combines both for the same cost function.

## Lower and tight bounds

Big-Omega gives an eventual lower bound:

```formula essential
f(n) = Ω(g(n))
f(n) ≥ c g(n) for all n ≥ n_0
where
f(n): a nonnegative cost function
g(n): an eventually positive comparison function
n: input size
Ω: Big-Omega; the first line holds when fixed constants satisfy the second
c: a fixed positive lower-bound multiplier
n_0: a fixed starting size
≥: at least
In words: after a fixed starting size, the cost never falls below a fixed positive multiple of the comparison function.
```

Big-Theta puts the cost between two such bounds:

```formula essential
f(n) = Θ(g(n))
c_1 g(n) ≤ f(n) ≤ c_2 g(n)
for all n ≥ n_0
where
f(n): a nonnegative cost function
g(n): an eventually positive comparison function
n: input size
Θ: Big-Theta; the first line holds when the displayed bounds hold
c_1, c_2: fixed positive lower and upper multipliers
n_0: a fixed starting size
≤, ≥: at most, at least
In words: the cost stays between two fixed multiples of the same growth function, pinning down its growth up to constant factors.
```

## Bounds and input cases answer different questions

For insertion sort on n items, already sorted input takes Θ(n) time; reverse-sorted distinct input takes Θ(n²). Thus the worst-case function has a tight quadratic bound and the best-case function a tight linear bound. All inputs share a quadratic upper bound and a linear lower bound, but not one common tight bound depending only on item count.

O does not mean worst case, and Omega does not mean best case. State the input case separately.

Nor must a function fit a familiar growth class. Suppose its cost is one step at every odd size and one step per item at every even size. It has a linear upper bound and constant lower bound. The even sizes defeat a constant upper bound; the odd sizes defeat a linear lower bound. Its piecewise description is still an exact description.

## Key takeaways
- Theta needs matching upper and lower growth bounds.
- Specify best, average or worst case separately from the notation.
- Irregular costs need not match a familiar monotone growth class.

## Further reading
- [Erickson: Introduction](https://jeffe.cs.illinois.edu/teaching/algorithms/book/00-intro.pdf)
