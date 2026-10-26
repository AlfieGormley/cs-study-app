---
id: cplx-approximation-spectrum
title: "Approximation schemes and representative limits"
level: intermediate
minutes: 5
summary: "Guarantees and hardness limits vary widely by problem and metric assumptions."
sourceLesson: cplx-coping
---

### A spectrum of approximability

Approximation quality depends on the problem and its assumptions. A factor near one is strong; a factor that grows with input size becomes weaker on larger instances. These are representative results, not a list of current records.

| Problem | Available guarantee | Limitation |
|---|---|---|
| Knapsack | Chosen relative accuracy | FPTAS trades time for accuracy |
| Symmetric metric TSP | Factor 1.5; slight improvements known | No PTAS unless P equals NP |
| Vertex Cover | Factor two | No PTAS unless P equals NP |
| Unweighted Set Cover | Factor logarithmic in universe size | Near-logarithmic hardness |
| General TSP | No constant factor unless P equals NP | Metric assumptions matter |
| Clique | Much weaker size-dependent bounds | Near-linear factor hardness |

For example, the knapsack FPTAS can guarantee at least 99 percent of optimum value. It rounds item values and runs dynamic programming on the rounded values, reducing the table size while controlling the loss. Tighter accuracy requires more work.

For symmetric metric TSP, distances are nonnegative and obey the triangle inequality. Christofides gives factor 1.5; published work improves that bound slightly. General TSP allows arbitrary nonnegative weights, so a construction with expensive non-edges can defeat every fixed constant guarantee.

Greedy unweighted set cover repeatedly picks the set that covers most uncovered elements. Its guarantee grows logarithmically in the number of elements. Exact numeric thresholds are useful references, but the choice here is whether the problem admits freely adjustable accuracy or a barrier prevents it.

A PTAS is polynomial for each fixed accuracy; its input-size exponent may depend on that accuracy. An FPTAS is polynomial jointly in input length and inverse accuracy. For knapsack, first discard items heavier than the capacity. The largest remaining single-item value is then at most the optimum, so rounding each value down loses less than one rounding step per selected item. Choosing the step as the allowed error times that largest feasible value divided by the item count limits the total loss to the allowed fraction of the optimum. Zero-value or empty feasible instances are trivial.

For integer objective values polynomially bounded in input length, choosing relative error smaller than the reciprocal of that bound makes the allowed additive loss less than one. An FPTAS must then return the exact integer optimum in polynomial time. This rules out an FPTAS for the stated hard families unless P equals NP.

## Key takeaways

- Guarantees and hardness limits vary widely by problem and metric assumptions.
- Knapsack has an FPTAS with runtime polynomial in input length and inverse accuracy.
- A PTAS for an APX-hard problem would imply P equals NP.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
- [Deterministic metric TSP improvement](https://arxiv.org/abs/2212.06296)
- [The Design of Approximation Algorithms — Williamson and Shmoys](https://www.designofapproxalgs.com/book.pdf)
- [Metric TSP hardness — Karpinski, Lampis and Schmied](https://arxiv.org/abs/1303.6437)
