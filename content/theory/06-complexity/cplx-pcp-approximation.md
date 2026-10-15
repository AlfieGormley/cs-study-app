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

```formula
f_max = 1   or   f_max ≤ s
where
f_max: the largest fraction of a 3-SAT formula's clauses that any true/false assignment satisfies, between 0 and 1
s: a fixed constant below 1 given by the theorem
In words: given a 3-SAT formula that is either fully satisfiable or can have at most a fraction s of its clauses satisfied, telling which is NP-hard. A deterministic algorithm guaranteeing a fraction of the optimum strictly greater than s would distinguish these promised cases, contradicting the gap hardness unless P equals NP. Randomised guarantees need a corresponding randomised-hardness assumption.
```

The sharpest result is Håstad's (2001), for MAX-3SAT with three distinct variables per clause. A clause (a ∨ b ∨ c) is "a OR b OR c", so it fails only when all three are false. A uniformly random assignment gives:

```formula
Pr_fail = (1/2)^3 = 1/8
Pr_sat = 1 − 1/8 = 7/8
E_sat = (7/8)m
where
Pr_fail: the probability a given clause is false: each of its three distinct variables is false with probability 1/2, independently
Pr_sat: the probability the clause is satisfied
E_sat: the expected number of satisfied clauses
m: the number of clauses; with m = 800, E_sat = 700
In words: a coin flip per variable satisfies seven eighths of the clauses on average. Håstad proved that guaranteeing 7/8 + ε of the optimum, for any ε > 0, is NP-hard, so the seven-eighths approximation threshold is optimal unless P equals NP. A random assignment gives this in expectation; conditional expectation can derandomise it to an assignment satisfying at least that fraction of all clauses.
```

> [!warning] Proven versus conjectured hardness
> The vertex-cover limit of about 1.414 (the square root of 2) is a theorem conditional only on P differing from NP (Khot, Minzer and Safra, 2017–18; it improved Dinur and Safra's 1.36). The limit of 2 relies on the **Unique Games Conjecture** (Khot, 2002), which is open. Always check which assumption a hardness-of-approximation result uses.

Stated as formulas:

```formula
ρ_VC ≥ √2 − ε   if P ≠ NP
ρ_VC ≥ 2 − ε    if UGC
where
ρ_VC: the approximation ratio any polynomial-time vertex-cover algorithm can guarantee
ε: epsilon, any small positive number
√2: the square root of 2, about 1.414
P: the class of problems solvable in polynomial time
NP: the class of problems whose yes-answers can be checked in polynomial time
≠: is not equal to
UGC: the Unique Games Conjecture, an unproven conjecture by Subhash Khot about a particular labelling problem
In words: if P ≠ NP, nobody can beat about 1.414; if the Unique Games Conjecture is also true, nobody can beat 2, so the simple matching algorithm would be best possible.
```

## Key takeaways

- PCP theorem connects local random proof checks to hard approximation gaps.
- Independent fair variable choices satisfy seven eighths of distinct-variable clauses in expectation.
- Vertex-cover hardness near two uses UGC; hardness near the square root of two does not.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
- [Optimal inapproximability — Håstad](https://people.kth.se/~johanh/optimalinap.pdf)
