---
id: cplx-tqbf-hardness
title: "Sharing the reachability formula"
level: advanced
minutes: 3
summary: "A naive reachability formula doubles its subformula at every level."
sourceLesson: cplx-space
---

TQBF asks whether a fully quantified Boolean formula is true and can be evaluated in polynomial space. To establish completeness we also need PSPACE-hardness: turn any polynomial-space computation into a polynomial-size quantified formula.

Hardness, in outline: for a machine using space p(n), write a formula saying "configuration c1 reaches configuration c2 within 2 to the power k steps", defined recursively using a midpoint:

```formula essential
R(c1, c2, k) = ∃m ∀c3 ∀c4
  [((c3, c4) = (c1, m) ∨
    (c3, c4) = (m, c2))
   → R(c3, c4, k − 1)]
|R(k)| = |R(k − 1)| + O(p(n))
|R(k)| = O(kp(n)) = O(p(n)^2)
where
R(c1, c2, k): the formula "configuration c1 reaches configuration c2 in at most 2^k steps"
c1, c2: the start and end configurations, each written as about p(n) Boolean variables
m: the midpoint configuration
c3, c4: universally quantified configuration encodings; the implication constrains the recursive check only when this pair equals one of the two halves
n: the input length in bits
[ ]: grouping the implication; vector equality means equality of every corresponding bit
k: the recursion level; k = O(p(n)), because the machine has at most 2^{O(p(n))} configurations
p(n): the machine's polynomial space bound on an n-bit input
|R(k)|: the length of the formula at level k
∃: "there exists"; ∀: "for all"
∨: OR; →: implies ("if the left side holds, the right side must too")
O(...): Big O: at most a constant times this
In words: one copy of the level-(k − 1) formula serves both halves, because ∀ makes it check whichever pair is plugged in. Each level adds only about p(n) symbols, so the whole formula is polynomial size.
```

The midpoint is chosen first, and universal variables then require both endpoint pairs to pass the one shared recursive test. Other pairs make the implication automatically true.

The naive version would write the sub-formula twice per level and double in size each time, giving exponentially many copies. This is Savitch's recursion written as a formula.

The base case says that the configurations are equal or joined by one legal machine step. Each configuration is a polynomial-length Boolean vector, and each quantified vector abbreviates one quantifier for each of its bits. Fresh bound-variable names avoid capture when a recursive template is substituted. One may arrange a unique accepting configuration without changing the polynomial-space bound.

## Key takeaways

- A naive reachability formula doubles its subformula at every level.
- Universal configuration variables let one copy check both halves.
- Polynomial formula length establishes PSPACE-hardness.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
