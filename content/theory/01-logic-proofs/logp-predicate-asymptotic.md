---
id: logp-predicate-asymptotic
title: Reading Big-O as a quantified promise
level: basic
minutes: 4
sourceLesson: logp-predicate
summary: Big-O requires a fixed multiplier and threshold that work for all later input sizes.
---

## A real definition: Big-O

Big-O describes an eventual upper bound on growth. For eventually nonnegative functions on natural-number inputs, choose one positive constant multiplier and one starting threshold. The scaled comparison function must then bound the cost at every input beyond that threshold. Both choices must stay fixed as the input grows.

```formula reference
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
In words: an asymptotic upper bound uses one fixed multiplier and one threshold that work for every later input size.
```

The order of the choices matters: you cannot increase the multiplier every time a larger input defeats it.

For a cost of three steps per item plus ten startup steps, four steps per item is an upper bound once the input has at least ten items. The multiplier and threshold remain fixed as the input grows.

Now consider what it takes to disprove the bound.

To disprove a proposed asymptotic bound, defeat every fixed multiplier and threshold: find a later input where the bound fails. One isolated small-input exception is insufficient.

For example, compare quadratic growth with linear growth:

A square grows faster than any fixed multiple of its input. Given any proposed multiplier and threshold, choose an integer beyond the threshold and larger than the multiplier. Its square then exceeds the proposed linear bound.

Negating the definition tells you exactly what you have to show.


## Key takeaways
- Big-O requires a fixed multiplier and threshold that work for all later input sizes.
- Disproving Big-O requires a violating input for every proposed multiplier and threshold.

## Further reading
- [Open Logic Project](https://forallx.openlogicproject.org/)
- [Mathematics for Computer Science — MIT OpenCourseWare](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/)
