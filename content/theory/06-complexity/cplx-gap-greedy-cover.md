---
id: cplx-gap-greedy-cover
title: "Gap reductions and greedy set cover"
level: intermediate
minutes: 3
summary: "Large non-edge weights rule out constant-factor general-TSP approximation unless P equals NP."
sourceLesson: cplx-coping
---

Approximation guarantees compare a feasible solution with the optimum on every permitted input. A hardness gap instead separates two kinds of input so widely that a good approximation would decide an NP-hard decision problem.

Fix any proposed approximation factor at least one. The general TSP trick reduces Hamiltonian cycle (is there a closed tour using only the graph's edges?) to TSP. Give each edge of an n-vertex graph weight 1 and each missing edge a huge weight w:

```formula essential
w = αn + 1
OPT_yes = n
c_no ≥ (n − 1) + w
c_no ≥ (1 + α)n > αn
where
w: the weight given to every pair of vertices that is not an edge of the graph
α: alpha, the approximation factor being ruled out, any constant at least 1
n: the number of vertices (cities)
OPT_yes: the length of the shortest tour when the graph has a Hamiltonian cycle: n edges of weight 1
c_no: the length of any tour when the graph has no Hamiltonian cycle, so the tour must use at least one missing edge
In words: with a Hamiltonian cycle the best tour costs n, so an α-approximation returns at most α × n. Without one, every tour costs more than α × n. Reading the approximation's output would decide an NP-complete problem.
```

This works only because non-metric weights can break the triangle inequality, which is why metric TSP escapes it.

For unweighted Set Cover, repeatedly choose the set covering most uncovered elements. Assume the available sets cover the whole universe. Its quality bound is a harmonic number, which grows logarithmically with the number of elements. The exact reference bound is:

```formula reference
H(n) = 1 + 1/2 + 1/3 + … + 1/n
H(n) ≤ ln(n) + 1
where
H(n): the nth harmonic number: the sum of 1/1, 1/2, … up to 1/n
n: the number of elements to cover
ln(n): the natural logarithm of n (log to base e ≈ 2.718)
≈: approximately equal to
In words: the greedy cover uses at most a harmonic-number factor more sets than the optimum; this factor grows logarithmically with the universe size. Improving the leading logarithmic factor by any fixed positive fraction is NP-hard.
```

## Key takeaways

- Large non-edge weights rule out constant-factor general-TSP approximation unless P equals NP.
- The weighting trick relies on non-metric distances.
- Greedy set cover has a harmonic-number guarantee growing logarithmically.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
- [The Design of Approximation Algorithms — Williamson and Shmoys](https://www.designofapproxalgs.com/book.pdf)
