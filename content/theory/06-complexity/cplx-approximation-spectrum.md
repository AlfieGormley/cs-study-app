---
id: cplx-approximation-spectrum
title: "Approximation schemes and representative limits"
level: intermediate
minutes: 5
summary: "Guarantees and hardness limits vary widely by problem and metric assumptions."
sourceLesson: cplx-coping
---

### A spectrum of approximability

Each row gives a representative published guarantee and a hardness limit, as an approximation ratio. The card first defines the symbols used in the table.

```formula
ρ = ALG / OPT
ρ_metric ≥ 123 / 122 ≈ 1.0082
√2 ≈ 1.414
ln(n) + 1 ≈ 14.8   for n = 10^6
where
ρ: rho, for a positive optimum in the standard nonnegative-objective setting, the approximation ratio: how many times worse than the optimum the answer can be; for a maximisation problem, ρ = OPT / ALG, so ρ ≥ 1 either way
ALG: the cost of the algorithm's answer
OPT: the cost of the best answer
ρ_metric: the best ratio any polynomial-time algorithm for metric TSP can guarantee; below 123/122 is NP-hard
ε: epsilon, any small positive number you choose, such as 0.01
√2: the square root of 2, the number that gives 2 when multiplied by itself
ln(n): the natural logarithm of n (log to base e ≈ 2.718)
n: the input size: the number of elements for set cover, the number of vertices for clique
polylog: a power of log n, such as (log n)^2; it grows far slower than n
n^(1−ε): n to the power 1 − ε, only slightly less than n itself
UGC: the Unique Games Conjecture (below)
FPTAS: fully polynomial-time approximation scheme: a ratio of 1 + ε for any ε, in time polynomial in n and 1/ε
≈: approximately equal to
In words: a ratio near 1 is excellent and one that grows with n is weak. Set cover's guarantee grows slowly (about 15 for a million elements); clique's is almost as bad as n.
```

| Problem | Representative guarantee | Known limit (if P differs from NP) |
|---|---|---|
| Knapsack | 1 + ε, any ε | none (FPTAS) |
| Metric TSP | about 1.5 | about 1.0082 |
| Vertex cover | two | square root of two; two assuming UGC |
| Set cover | ln n + 1 | (1 − ε) ln n |
| General TSP | none | no constant ratio |
| Clique | n / polylog | n^(1−ε) |

- **Knapsack** has an FPTAS. You get as close to optimal as you like, by rounding the values and running the pseudo-polynomial DP (formula below).
- **Metric TSP** (distances obey the triangle inequality): Christofides' algorithm (1976) gives 1.5. Karlin, Klein and Oveis Gharan's 2020 work gave a randomised expected-cost bound a tiny amount below 1.5 (the improvement is more than 10⁻³⁶); their 2022 work derandomised it. The gain is tiny but significant theoretically.
- **General TSP** has no constant-factor approximation unless P equals NP, by a weighting trick (formula below).
- **Greedy set cover** (repeatedly take the set covering most uncovered elements) achieves about ln n + 1, and doing much better is NP-hard (Dinur and Steurer, 2014).

The knapsack FPTAS is written as a fraction of the optimum, because knapsack is a maximisation problem:

```formula
ALG ≥ (1 − ε) × OPT
ALG ≥ 0.99 × OPT   for ε = 0.01
where
ALG: the total value of the items the algorithm packs
OPT: the best possible total value that fits
ε: epsilon, the error you allow, any number between 0 and 1
In words: choose ε = 0.01 and you are guaranteed at least 99 % of the best value, in time polynomial in n (the number of items) and in 1/ε = 100. This is a ratio of 1 / (1 − ε), approximately 1 + ε for small ε; a scheme can reparameterise its accuracy to promise a literal ratio of 1 + ε.
```

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
