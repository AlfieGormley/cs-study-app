---
id: cx-master-root
sourceLesson: cx-recurrences
title: Master Theorem: root work dominates
level: advanced
minutes: 2
summary: Check regularity and apply the complete three-case shortcut.
---

The root dominates when outside work is sufficiently large and consistently shrinks down the recursion tree. Here n is input size, with fixed fractional children and bounded positive base cases.

## Larger is not enough without regularity

For the third Master Theorem case, outside work must exceed leaf growth by a fixed positive power. The children's combined outside work must also be at most a fixed fraction less than the parent's, for all sufficiently large inputs:

```formula essential
f(n) = Ω(n^{c+ε})
a f(n/b) ≤ q f(n)
T(n) = Θ(f(n))
where
f(n): nonnegative outside work
n: input size
c: the critical exponent from the recurrence's branching and shrinking
ε: a fixed positive exponent gap
a: fixed number of equal-size children
b: fixed shrink divisor greater than one
q: a fixed positive fraction strictly below one
T(n): total work
Ω: an eventual lower growth bound
Θ: a tight growth bound
≤: at most; the middle condition must hold for all sufficiently large inputs
In words: if outside work is polynomially larger than leaf growth and decreases by a fixed fraction across each generation, the root's growth determines the total.
```

Two half-size children with quadratic outside work satisfy both conditions. Each child's outside work is a quarter of the parent's, so together they cost half. Later levels keep halving. Adding all of them changes only a constant factor: total work is Θ(n²).

The regularity condition prevents a wildly varying outside-work function from hiding large costs deeper in the tree. Ordinary power functions with exponent above the critical exponent satisfy it. "Outside work looks bigger" is not a complete proof for an arbitrary function.

## The three-case picture

| Comparison with leaf growth | Behaviour |
|---|---|
| Polynomially smaller | leaves dominate |
| Matching power, covered log factors | accumulate across levels |
| Polynomially larger and regular | root dominates |

Use that picture to explain the answer, then check the relevant conditions. A table of remembered recurrence answers is less reliable than understanding where the work sits.

## Key takeaways
- Root domination needs a power gap and regularity.
- Regularity makes level totals shrink geometrically.
- Explain which part of the tree supplies the dominant work.

## Further reading
- [MIT: Master theorem, including power gaps and regularity](https://people.csail.mit.edu/thies/6.046-web/master.pdf)
- [Erickson: Solving Recurrences](https://jeffe.cs.illinois.edu/teaching/algorithms/notes/99-recurrences.pdf)
