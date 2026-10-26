---
id: cplx-pcp-approximation
title: "PCP theorem gaps and the seven-eighths limit"
level: intermediate
minutes: 4
summary: "PCP theorem connects local random proof checks to hard approximation gaps."
sourceLesson: cplx-coping
---

### Where the limits come from: the PCP theorem

The **PCP theorem** (Arora, Safra, Lund, Motwani, Sudan and Szegedy, 1992) says every NP statement has a polynomial-length proof format that a polynomial-time verifier, using logarithmically many random bits, can check by reading only a **constant number of randomly chosen bits**, catching any false claim with probability at least 1/2. An equivalent form is a gap that is hard to see:

```formula essential
f_max = 1   or   f_max ≤ s
where
f_max: the largest fraction of a 3-SAT formula's clauses that any true/false assignment satisfies, between 0 and 1
s: a fixed constant below 1 given by the theorem
In words: given a 3-SAT formula that is either fully satisfiable or can have at most a fraction s of its clauses satisfied, telling which is NP-hard. A deterministic algorithm guaranteeing a fraction of the optimum strictly greater than s would distinguish these promised cases, contradicting the gap hardness unless P equals NP. Randomised guarantees need a corresponding randomised-hardness assumption.
```

The sharpest result is Håstad's (2001), for MAX-3SAT with three distinct variables per clause. A clause (a ∨ b ∨ c) is "a OR b OR c", so it fails only when all three are false. A uniformly random assignment makes each clause false only when all three independent variable choices falsify their literals: one of eight equally likely settings. Each clause is therefore satisfied with probability seven eighths. Adding expectations gives seven eighths of all clauses on average, even if clauses share variables. Conditional expectation can turn this into a deterministic guarantee.

Håstad proved that guaranteeing any fixed positive improvement over seven eighths of the optimum is NP-hard. This is a worst-case guarantee over instances, not a claim that no particular formula can be solved exactly.

> [!warning] Proven versus conjectured hardness
> The vertex-cover limit of about 1.414 (the square root of 2) is a theorem conditional only on P differing from NP (Khot, Minzer and Safra, 2017–18; it improved Dinur and Safra's 1.36). The limit of 2 relies on the **Unique Games Conjecture** (Khot, 2002), which is open. Always check which assumption a hardness-of-approximation result uses.

These limits have different assumptions. A theorem conditional on the Unique Games Conjecture cannot be reported as following from P differing from NP alone.

Two other barriers need only P differing from NP: general, non-metric TSP has no constant-factor approximation, and Set Cover cannot beat its natural-logarithm-of-universe-size factor by any fixed proportional margin. The TSP barrier follows from a gap reduction from Hamiltonian Cycle; Dinur and Steurer established the Set Cover barrier in 2014.

## Key takeaways

- PCP theorem connects local random proof checks to hard approximation gaps.
- Independent fair variable choices satisfy seven eighths of distinct-variable clauses in expectation.
- Vertex-cover hardness near two uses UGC; hardness near the square root of two does not.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
- [Optimal inapproximability — Håstad](https://people.kth.se/~johanh/optimalinap.pdf)
- [The 2-to-2 games result — Khot, Minzer and Safra](https://annals.math.princeton.edu/2023/198-1/p01)
- [Set Cover hardness — Dinur and Steurer](https://www.dsteurer.org/paper/productgames.pdf)
