---
id: cplx-shor-grover
title: "Shor, Grover and the limits of quantum evidence"
level: advanced
minutes: 4
summary: "Shor gives quantum polynomial-time factoring and discrete logarithms."
sourceLesson: cplx-randomised-quantum
---

BQP contains decision problems solved with bounded error by uniform polynomial-size quantum circuits. Factoring and search also have function versions, where the algorithm returns a factorisation or an item. Use the associated decision version when placing them in a decision complexity class.

### Shor and Grover

- **Shor (1994)** factors integers and computes discrete logarithms in polynomial time on a quantum computer. The associated factoring decision problem is in BQP; Shor also recovers the factors. It is **not known** to be outside BPP; the leading general-purpose classical method (the general number field sieve) has a heuristic expected subexponential-time analysis. This breaks RSA and elliptic-curve cryptography once large fault-tolerant machines exist, which is why NIST standardised post-quantum schemes such as ML-KEM (FIPS 203) in 2024. Published resource estimates for RSA-2048 have fallen over time (Gidney's 2025 estimate is under a million noisy qubits running for under a week). This is a dated resource estimate under stated hardware assumptions, not a measurement of currently available machines.
- **Grover (1996)** searches unstructured items with about the square root of the number of queries a classical search needs (below). This is **proven optimal** for black-box search (Bennett, Bernstein, Brassard and Vazirani, 1997). For brute-force SAT it is a quadratic speed-up, still exponential.

```formula
Q ≈ (π/4) × √N
Q ≈ 0.785 × √(2^128) ≈ 1.4 × 10^19
N = 2^n  gives  √N = 2^{n/2}
where
Q: the number of queries (evaluations of the black-box function) Grover's algorithm makes
N: the number of possible items to search; 2^128 for a 128-bit key
π: pi, about 3.14159, so π/4 ≈ 0.785
√N: the square root of N; √(2^128) = 2^64 ≈ 1.8 × 10^19
n: the number of bits (or Boolean variables) being searched over, so there are 2^n candidates
≈: approximately equal to
In words: a classical black-box search needs about N tries; Grover needs about the square root of N. That turns 2^128 into about 2^64, and a SAT search over n variables from 2^n into about 2^{n/2}: much faster, but still exponential.
```

> [!warning] Quantum computers are not believed to solve NP-complete problems efficiently
> Factoring is in both NP and coNP and not believed NP-complete. Grover's bound shows that any quantum algorithm treating SAT as a black box needs about the square root of the 2-to-the-n brute-force steps (n variables). Whether NP is contained in BQP is open, but it is widely believed false.

### Evidence about BQP

- **Oracle separations**: Raz and Tal (2018) found an oracle relative to which BQP is not contained in the polynomial hierarchy. This is evidence, not proof, about the real world (use the earlier relativisation barrier).
- **Quantum advantage experiments**: Google's 2019 random-circuit sampling claim targeted a *sampling* task believed hard classically under complexity assumptions. Improved classical simulations later narrowed the claimed gap. Such experiments test conjectures; they don't prove separations.

## The map, with confidence levels

| Relationship | Status |
|---|---|
| P inside BPP inside BQP inside PSPACE | Proven |
| BPP inside Σ₂ and Π₂ | Proven |
| P equals BPP | Conjectured |
| BPP inside NP | Open |
| Factoring in BQP | Proven (Shor) |
| Factoring not in BPP | Believed, unproven |
| NP inside BQP | Believed false |

The Grover estimate assumes one marked item, ideal coherent oracle access and a sufficiently large search space. With multiple solutions the query count depends on how many are marked; with none, a search procedure needs an appropriate existence test. Cipher evaluations here mean reversible quantum oracle queries, not equal-cost classical CPU operations. Doubling a symmetric key length restores the generic query exponent in this model; physical costs, parallelism and nongeneric cryptanalysis need separate analysis. The dated factoring-resource estimate assumes a square grid with interactions only between adjacent hardware sites, a 0.1 percent gate error rate, one-microsecond surface-code cycles and a ten-microsecond control response; it describes a proposed fault-tolerant machine, not an experiment performed here.

## Key takeaways

- Shor gives quantum polynomial-time factoring and discrete logarithms.
- Grover’s square-root black-box speed-up remains exponential for assignment search.
- Oracle and sampling evidence do not prove an unrelativised decision-class separation.

## Further reading

- [Shor’s factoring algorithm](https://arxiv.org/abs/quant-ph/9508027)
- [Grover’s search algorithm](https://arxiv.org/abs/quant-ph/9605043)
- [Dated RSA resource estimate — Gidney, 2025](https://arxiv.org/abs/2505.15917)
- [ML-KEM standard — NIST](https://csrc.nist.gov/pubs/fips/203/final)
