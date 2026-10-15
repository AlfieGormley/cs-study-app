---
id: cplx-reduction-approximation
title: "Why exact reductions need not preserve ratios"
level: intermediate
minutes: 3
summary: "Exact decision equivalence does not ensure approximation equivalence."
sourceLesson: cplx-reductions
---

The preceding exact maps connect Independent Set, Vertex Cover and Clique. Approximation additionally asks how a returned feasible solution compares with the optimum. For an objective where lower cost is better, factor two means a cost at most twice optimum; for maximisation it means a value at least half optimum.

These three problems are the same problem viewed three ways. Yet they behave very differently once you approximate (in the coping-strategy units). Vertex cover has a simple factor-2 approximation, while clique has a much worse limit:

```formula
ρ_VC ≤ 2
ρ_CLIQUE > n^(1 − ε)   if P ≠ NP
1000^{0.99} ≈ 933
where
ρ_VC: the best approximation ratio known for vertex cover in polynomial time: the returned cover is at most 2 times the smallest
ρ_CLIQUE: the approximation ratio any polynomial-time clique algorithm can promise: how many times smaller than the largest clique its answer might be
n: the number of vertices in the graph
ε: epsilon, any fixed number strictly between zero and one, however small; the third line uses ε = 0.01
≈: approximately equal to
≠: is not equal to
≤: is at most
P: the complexity class P: decision problems a deterministic algorithm solves in polynomial time (at most about n^k steps for some fixed k)
NP: the class NP (nondeterministic polynomial time): decision problems whose yes-answers have a short certificate checkable in polynomial time
In words: vertex cover can always be solved to within a factor of 2, but unless P equals NP no polynomial-time algorithm can promise a clique within a factor of n to the power 0.99 (or any power below 1) of the largest one. The expression n to the power 0.99 is about 933 at a thousand vertices; this illustrates the size of the asymptotic ratio, not hardness for a single fixed graph size.
```

A guarantee that weak is almost useless. The exact reductions above preserve yes/no answers, not approximation ratios.

## Key takeaways

- Exact decision equivalence does not ensure approximation equivalence.
- A factor-two cover can leave an empty independent-set complement.
- Clique and independent set have much worse polynomial-time approximation limits.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
