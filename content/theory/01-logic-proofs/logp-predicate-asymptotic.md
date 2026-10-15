---
id: logp-predicate-asymptotic
title: Reading Big-O as a quantified promise
level: basic
minutes: 4
sourceLesson: logp-predicate
summary: Big-O requires a fixed multiplier and threshold that work for all later input sizes.
---

## A real definition: Big-O

You have already met a nested-quantifier statement. For eventually nonnegative functions on natural-number inputs, Big-O is defined like this:

```formula
f(n) = O(g(n))   iff
∃c > 0 ∃n_0 ∀n ≥ n_0 : f(n) ≤ c · g(n)
where
f(n): the function being bounded, e.g. an algorithm's step count for input size n
g(n): the bounding growth function, e.g. n or n^2
n: the input size, a natural number (0, 1, 2, …)
O(g(n)): "Big-O of g": grows no faster than a constant times g, once n is large enough
c: a positive constant multiplier, chosen by the prover
n_0: a non-negative integer threshold input size, chosen by the prover; the inequality only has to hold from n_0 upwards
∃: there exists at least one
∀: for all
≥, ≤: is at least, is at most
·: multiplied by
:: "such that" (separates the quantifiers from the condition)
>: greater than
In words: f is O(g) when you can pick a constant c and a starting point n_0 so that, for every n from n_0 on, f(n) is at most c times g(n).
```

Read it as a game. You choose a constant c and a threshold n₀; then any n beyond n₀ must satisfy the inequality.

To show 3n + 10 equals O(n), give witnesses: c equals 4 and n₀ equals 10.

```formula
3n + 10 ≤ 3n + n = 4n   for n ≥ 10
c = 4,  n_0 = 10
where
n: the input size; from n_0 = 10 on, 10 is at most n
c: the constant multiplier chosen as a witness
n_0: the threshold chosen as a witness
≤: is at most
≥: at least
In words: once n is at least 10, the "+ 10" is no bigger than another n, so 3n + 10 is at most 4n. That is the definition with c = 4 and n_0 = 10.
```

To show n squared is **not** O(n), prove the negation of the definition (every quantifier flips and ≤ becomes >):

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
≥: at least
>: greater than
In words: whatever constant and threshold are chosen, you can always find a larger input where n² beats c times n.
```

Here is how to find that n for any given c and n₀:

```formula
n = max(n_0, ⌊c⌋ + 1)
n > c
n^2 = n · n > c · n
where
n: the input size you pick
n_0: the non-negative integer threshold you were given
c: the positive constant you were given
max(a, b): the larger of a and b, so n is at least n_0
⌊c⌋: the floor of c: c rounded down to a whole number (⌊2.7⌋ = 2), so ⌊c⌋ + 1 is bigger than c
·: multiplied by
>: greater than
⌊: floor: round down to the nearest integer
⌋: closes the floor operation
In words: pick n at least n_0 and bigger than c. Then n times n is bigger than c times n. For example, with c = 2.7 and n_0 = 1, n = 3 gives 9 > 8.1.
```

Negating the definition tells you exactly what you have to show.


## Key takeaways
- Big-O requires a fixed multiplier and threshold that work for all later input sizes.
- Disproving Big-O requires a violating input for every proposed multiplier and threshold.

## Further reading
- [Open Logic Project](https://forallx.openlogicproject.org/)
- [Mathematics for Computer Science — MIT OpenCourseWare](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/)
