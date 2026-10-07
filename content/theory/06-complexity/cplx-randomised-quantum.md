---
id: cplx-randomised-quantum
title: Randomised and quantum complexity
level: advanced
minutes: 15
summary: RP, coRP, ZPP and BPP, error amplification, Freivalds and polynomial identity testing, the conjecture that P = BPP, and BQP with what Shor and Grover do and don't show, keeping proven results apart from beliefs.
---

Some of the most useful algorithms flip coins. Miller–Rabin is widely used in probable-prime generation, randomised quicksort illustrates efficient expected-time sorting, and hashing with random seeds defends against adversarial inputs. Randomness also gives us algorithms for problems where no deterministic polynomial algorithm is known at all.

Quantum computers go further: they manipulate amplitudes that can interfere. This lesson looks at both through complexity classes, and keeps a careful line between what is **proven** and what is **believed**.

## Two kinds of randomised algorithm

- **Las Vegas**: always correct, running time is random. Randomised quicksort with distinct keys and uniform random pivots: always sorts, expected O(n log n).
- **Monte Carlo**: a bounded running-time guarantee, but some chance of a wrong answer. Actual running time can still vary. Miller–Rabin: may call a composite "probably prime".

The error probability is over the algorithm's own coin flips, for **every** input. No assumption about the input being random is needed.

## The classes

RP, coRP and BPP use a worst-case polynomial time bound; ZPP uses expected polynomial time.

| Class | If answer is yes | If answer is no |
|---|---|---|
| RP | accept w.p. ≥ 1/2 | always reject |
| coRP | always accept | reject w.p. ≥ 1/2 |
| BPP | accept w.p. ≥ 2/3 | reject w.p. ≥ 2/3 |
| ZPP | never wrong | expected poly time |

**ZPP = RP ∩ coRP**: run both one-sided algorithms until one gives a certain answer.

The constants 1/2 and 2/3 don't matter, thanks to amplification.

## Amplification

**One-sided error (RP).** Run k times and accept if any run accepts. A no-instance is never accepted; a yes-instance is missed only if every run misses: probability ≤ 2^−k. Twenty runs give an error below one in a million.

**Two-sided error (BPP).** Run r times and take the **majority**. By the Chernoff bound the error falls exponentially in r. Starting from error 1/3:

```python
from math import comb

def majority_error(r, p=1/3):
    # P(at least half of r runs wrong)
    return sum(comb(r, i) * p**i
               * (1 - p)**(r - i)
               for i in range((r + 1) // 2,
                              r + 1))

for r in (1, 11, 31, 101):
    print(r, f"{majority_error(r):.2g}")
# 1 0.33
# 11 0.12
# 31 0.027
# 101 0.00027
```

So BPP with error 2^−100 is the same class as BPP with error 1/3. The mathematical error bound assumes independent random choices and correct execution; it is not a hardware-reliability estimate.

## Randomness in action

### Freivalds: checking a matrix product

The naive matrix product uses O(n³) arithmetic operations; subcubic algorithms also exist. The comparison below is with naive multiplication, not a claim about the current best exponent. Checking a claimed product C = AB is cheaper: using exact integer or field arithmetic, pick a random 0/1 vector r and compare A(Br) with Cr, three matrix-vector products costing O(n²).

```python
import random

def freivalds(A, B, C, trials=20):
    n = len(A)
    def mul(M, x):
        return [sum(M[i][j] * x[j]
                    for j in range(n))
                for i in range(n)]
    for _ in range(trials):
        r = [random.randint(0, 1)
             for _ in range(n)]
        if mul(A, mul(B, r)) != mul(C, r):
            return False  # surely wrong
    return True  # wrong w.p. <= 2**-trials

A = [[1, 2], [3, 4]]
B = [[5, 6], [7, 8]]
good = [[19, 22], [43, 50]]
bad = [[19, 22], [43, 51]]
print(freivalds(A, B, good))  # True
print(freivalds(A, B, bad))   # False
# (True w.p. 2**-20)
```

If AB ≠ C, a single trial catches it with probability at least 1/2. For `bad`, the only wrong entry is at row 1, column 1 (0-indexed), so a trial catches it exactly when r[1] = 1, with probability exactly 1/2.

> [!note] Content gap: empirical measurement
> The previous measured detection-rate claim has been omitted because no reproducible run record was available to verify it. The probability calculation above follows directly from the two equally likely values of r[1]. With 20 trials, `bad` slips through with probability 2^−20.

### Polynomial identity testing

Given an arithmetic circuit computing a polynomial p(x1, ..., xn) of degree d, is p identically zero? Expanding it can produce exponentially many terms.

The **Schwartz–Zippel lemma**: if p is not the zero polynomial and each xi is chosen independently and uniformly from a finite subset S of the coefficient field, then p evaluates to 0 with probability at most d/|S|. Evaluate at one random point: if the result is nonzero, p is certainly nonzero.

So polynomial identity testing is in **coRP**, and **no deterministic polynomial-time algorithm is known**. Kabanets and Impagliazzo (2004) showed that derandomising it would imply circuit lower bounds that nobody can currently prove.

### Primality: a derandomisation story

Miller–Rabin declares a composite "probably prime" with probability at most 1/4 per random base, so 20 bases give error ≤ 4^−20 ≈ 10^−12. This put PRIMES in coRP (composites are detected with one-sided error) decades ago. In 2002 the AKS algorithm put PRIMES in **P**. Practice still uses Miller–Rabin: it's much faster.

## How BPP relates to the rest

Proven:

- P ⊆ ZPP ⊆ RP ⊆ BPP, and RP ⊆ NP (an accepting coin sequence is a certificate).
- **BPP ⊆ PSPACE** (try every coin sequence, count acceptances, reuse space).
- **BPP ⊆ Σ₂ ∩ Π₂**, the second level of the polynomial hierarchy (Sipser, Gács and Lautemann, 1983). So if P = NP, then P = BPP.
- **BPP ⊆ P/poly** (Adleman, 1978): after amplifying error below 2^−n for inputs of length n, a union bound shows there exists one polynomial-length coin string that works for all inputs of that length. The string is non-uniform advice, not a known efficient way to find it.

Open, and surprising: whether **BPP ⊆ NP**. Nobody has proved that randomised algorithms can be simulated by short certificates.

Conjectured: **P = BPP**. Impagliazzo and Wigderson (1997) proved that if some problem in E (time 2^O(n)) requires circuits of size 2^Ω(n), then P = BPP. Under widely believed hardness assumptions, randomness gives at most a polynomial speed-up for decision problems. The primality story fits that pattern.

> [!note] What "P = BPP" would and wouldn't mean
> It wouldn't make randomness useless: randomised algorithms are often simpler or faster by a polynomial factor, and randomness is essential in cryptography, distributed protocols and sampling. It would mean randomness can't turn exponential into polynomial for decision problems.

## Quantum: BQP

A quantum computer on n qubits has a state described by 2ⁿ complex **amplitudes**. Gates update all of them at once, and measurement returns outcome x with probability |amplitude of x|². The power isn't "trying everything in parallel"; measurement gives you one outcome. It is **interference**: arranging for amplitudes of wrong answers to cancel and right answers to reinforce.

**BQP** is the set of decision problems solvable by a polynomial-time-uniform family of polynomial-size quantum circuits with error at most 1/3 (amplifiable, as for BPP).

What's proven:

```
P ⊆ BPP ⊆ BQP ⊆ PP ⊆ PSPACE
```

- BQP ⊆ PSPACE (Bernstein and Vazirani, 1993): sum the amplitudes path by path, reusing space.
- BQP ⊆ PP (Adleman, DeMarrais and Huang, 1997).

Because BQP ⊆ PSPACE, proving BQP ≠ BPP would prove P ≠ PSPACE, which is far beyond current techniques. This rules out claiming a proven separation of BQP from BPP. It does not rule out proven query-complexity advantages or smaller speed-ups within polynomial time.

### Shor and Grover

- **Shor (1994)** factors integers and computes discrete logarithms in polynomial time on a quantum computer. The associated factoring decision problem is in BQP; Shor also recovers the factors. It is **not known** to be outside BPP; the best known classical algorithm (the number field sieve) is sub-exponential. This breaks RSA and elliptic-curve cryptography once large fault-tolerant machines exist, which is why NIST standardised post-quantum schemes such as ML-KEM (FIPS 203) in 2024. Published resource estimates for RSA-2048 have fallen over time (Gidney's 2025 estimate is under a million noisy qubits running for under a week). This is a dated resource estimate under stated hardware assumptions, not a measurement of currently available machines.
- **Grover (1996)** searches N unstructured items with O(√N) queries instead of O(N). This is **proven optimal** for black-box search (Bennett, Bernstein, Brassard and Vazirani, 1997). For brute-force SAT it turns 2ⁿ into about 2^(n/2): a quadratic speed-up, still exponential.

> [!warning] Quantum computers are not believed to solve NP-complete problems efficiently
> Factoring is in NP ∩ coNP and not believed NP-complete. Grover's bound shows that any quantum algorithm treating SAT as a black box needs about 2^(n/2) steps. Whether NP ⊆ BQP is open, but it is widely believed false.

### Evidence about BQP

- **Oracle separations**: Raz and Tal (2018) found an oracle relative to which BQP is not contained in the polynomial hierarchy. This is evidence, not proof, about the real world (recall relativisation from lesson 1).
- **Quantum advantage experiments**: Google's 2019 random-circuit sampling claim targeted a *sampling* task believed hard classically under complexity assumptions. Improved classical simulations later narrowed the claimed gap. Such experiments test conjectures; they don't prove separations.

## The map, with confidence levels

| Relationship | Status |
|---|---|
| P ⊆ BPP ⊆ BQP ⊆ PSPACE | Proven |
| BPP ⊆ Σ₂ ∩ Π₂ | Proven |
| P = BPP | Conjectured |
| BPP ⊆ NP | Open |
| Factoring in BQP | Proven (Shor) |
| Factoring not in BPP | Believed, unproven |
| NP ⊆ BQP | Believed false |

## Key takeaways
- RP and coRP have one-sided error (amplify to 2^−k with k runs); BPP has two-sided error (majority vote, error falls exponentially); ZPP = RP ∩ coRP is zero-error, expected polynomial time.
- Freivalds checks AB = C in O(n²) per trial; Schwartz–Zippel puts polynomial identity testing in coRP, with no deterministic polynomial algorithm known.
- Proven: P ⊆ BPP ⊆ Σ₂ ∩ Π₂ and BPP ⊆ P/poly. Conjectured: P = BPP (implied by plausible circuit lower bounds). Open: BPP ⊆ NP.
- Proven: BPP ⊆ BQP ⊆ PP ⊆ PSPACE; separating BQP from BPP would imply P ≠ PSPACE. Query-model advantages such as Grover's do not require that class separation.
- Shor puts factoring in BQP; Grover gives a proven-optimal quadratic speed-up for black-box search. NP ⊆ BQP is believed false.

## Further reading
- [BPP (complexity) — Wikipedia](https://en.wikipedia.org/wiki/BPP_(complexity))
- [RP (complexity) — Wikipedia](https://en.wikipedia.org/wiki/RP_(complexity))
- [Freivalds' algorithm — Wikipedia](https://en.wikipedia.org/wiki/Freivalds%27_algorithm)
- [Schwartz–Zippel lemma — Wikipedia](https://en.wikipedia.org/wiki/Schwartz%E2%80%93Zippel_lemma)
- [BQP — Wikipedia](https://en.wikipedia.org/wiki/BQP)
- [Shor's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Shor%27s_algorithm)
- [Grover's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Grover%27s_algorithm)
- [Complexity Zoo](https://complexityzoo.net/Complexity_Zoo)
