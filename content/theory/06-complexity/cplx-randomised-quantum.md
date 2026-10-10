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

- **Las Vegas**: always correct, running time is random. Randomised quicksort with distinct keys and uniform random pivots: always sorts, in an expected O(n log n) comparisons, where n is the number of keys.
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

The same definitions in symbols, where Pr[...] is the probability over the algorithm's own coin flips:

```formula
x ∈ L  gives  Pr[A(x) = 1] ≥ 1/2
x ∉ L  gives  Pr[A(x) = 1] = 0
x ∈ L  gives  Pr[B(x) = 1] ≥ 2/3
x ∉ L  gives  Pr[B(x) = 0] ≥ 2/3
where
L: the decision problem, viewed as the set of its yes-instances
x: any input (problem instance)
∈, ∉: "is a member of", "is not a member of": x ∈ L means x is a yes-instance, x ∉ L a no-instance
A(x), B(x): the algorithm's output on x: 1 means accept (answer yes), 0 means reject (answer no)
A: an RP algorithm: polynomial-time, randomised, with one-sided error (it can miss a yes, but never wrongly says yes)
B: a BPP algorithm: polynomial-time, randomised, with two-sided error (it can be wrong either way, at most 1/3 of the time)
Pr[...]: the probability of the event in brackets, taken over the algorithm's random coin flips, for this fixed input x
≥: is at least
In words: an RP algorithm catches each yes-instance at least half the time and never accepts a no-instance; a BPP algorithm is right at least two-thirds of the time on every input, whichever the answer.
```

coRP swaps the roles (never wrongly rejects a yes-instance; rejects each no-instance with probability at least 1/2). ZPP sits exactly where the one-sided classes overlap:

```formula
ZPP = RP ∩ coRP
where
ZPP: zero-error probabilistic polynomial time: decision problems a randomised algorithm always answers correctly, in expected polynomial time
RP: randomised polynomial time: polynomial-time randomised algorithms that never accept a no-instance and accept each yes-instance with probability at least 1/2
coRP: the complements of RP problems: never reject a yes-instance, and reject each no-instance with probability at least 1/2
∩: intersection: the problems that belong to both classes
In words: a problem has a zero-error, expected-polynomial-time algorithm exactly when it has both kinds of one-sided-error algorithm. Run both repeatedly until one of them gives an answer that is certain.
```

The constants 1/2 and 2/3 don't matter, thanks to amplification.

## Amplification

**One-sided error (RP).** Run the algorithm several times and accept if any run accepts. A no-instance is never accepted; a yes-instance is missed only if every run misses:

```formula
ε_k ≤ (1/2)^k = 2^{−k}
ε_20 ≤ 2^{−20} ≈ 9.5 × 10^{−7}
where
ε_k, ε_20: the probability that all k (or 20) independent runs miss a yes-instance (the error after k runs)
k: the number of independent runs; 20 in the second line
(1/2)^k: k copies of one-half multiplied together: each run misses with probability at most 1/2, and independent probabilities multiply
≤: is at most
≈: approximately equal to
In words: every extra run halves the chance of missing a yes-instance. Twenty runs bring it below one in a million, and no-instances are never wrongly accepted.
```

**Two-sided error (BPP).** Run the algorithm an odd number of times and take the **majority** answer. The majority is wrong only when at least half of the runs are wrong:

```formula
ε_r = Σ C(r, i) × p^i × (1 − p)^{r−i}
  for (r + 1)/2 ≤ i ≤ r
ε_3 = 3 × (1/3)^2 × (2/3) + (1/3)^3
ε_3 = 6/27 + 1/27 = 7/27 ≈ 0.26
ε_r ≤ e^{−c × r}
where
ε_r, ε_3: the probability that the majority of r (or 3) runs is wrong
r: the number of independent runs, an odd whole number; 3 in the worked lines
i: the number of runs that are wrong; the sum covers every i from (r + 1)/2 up to r
Σ: sum: add up the term after it for every value of i in the stated range
C(r, i): "r choose i", the number of ways to pick which i of the r runs are wrong
p: the error probability of one run; here 1/3
e: Euler's number, about 2.718, the base of natural exponentials
c: a positive constant that depends on p (the Chernoff bound gives one)
≈: approximately equal to
≤: is at most
In words: add up the chances of every outcome where wrong runs form a majority. With error 1/3, three runs give 7/27, about 0.26; the Chernoff bound guarantees the error then shrinks exponentially as r grows.
```

The code below evaluates the same sum, starting from error 1/3:

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

So BPP with error 2 to the power −100 is the same class as BPP with error 1/3. The mathematical error bound assumes independent random choices and correct execution; it is not a hardware-reliability estimate.

## Randomness in action

### Freivalds: checking a matrix product

Multiplying two n × n matrices naively costs about n³ multiplications; subcubic algorithms also exist. The comparison below is with naive multiplication, not a claim about the current best exponent. Checking a claimed product is cheaper: using exact integer or field arithmetic, pick a random vector of 0s and 1s and multiply it through both sides.

```formula
A × (B × r) = C × r
cost = 3 × n^2
cost = 3 × 1000^2 = 3 × 10^6
where
A, B: the two n × n input matrices
C: the claimed product of A and B, an n × n matrix
r: a random column vector of n entries, each 0 or 1 with probability 1/2
B × r: a matrix–vector product: n^2 multiplications, giving a vector of n numbers
n: the number of rows (and columns) of each matrix; 1000 in the last line
cost: the number of multiplications in one trial (three matrix–vector products)
In words: if C really is A times B, both sides agree for every r. Each trial costs three matrix–vector products, about 3 million multiplications for 1000 × 1000 matrices, against about 10^9 to redo the product naively.
```

If C is wrong, a single trial exposes it with probability at least 1/2, so the chance that t independent trials all miss is at most 2 to the power −t (about one in a million for t = 20).

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

For `bad`, the only wrong entry is at row 1, column 1 (0-indexed), so a trial catches it exactly when the random vector's entry `r[1]` is 1, with probability exactly 1/2.

> [!note] Content gap: empirical measurement
> The previous measured detection-rate claim has been omitted because no reproducible run record was available to verify it. The probability calculation above follows directly from the two equally likely values of `r[1]`. With 20 trials, `bad` slips through with probability 2 to the power −20, about one in a million.

### Polynomial identity testing

Given an arithmetic circuit (a network of additions and multiplications) computing a polynomial in many variables, is that polynomial identically zero, meaning every coefficient cancels? Expanding it can produce exponentially many terms.

The **Schwartz–Zippel lemma** says a random evaluation almost never lands on a root of a nonzero polynomial:

```formula
Pr[p(x_1, ..., x_n) = 0] ≤ d / |S|
Pr ≤ 10 / 1000 = 0.01   for d = 10
where
p: the polynomial computed by the circuit, assumed not to be the zero polynomial
x_1, ..., x_n: its n variables, each chosen independently and uniformly at random from S
n: the number of variables
d: the total degree of p (the largest sum of exponents in any term); 10 in the example
S: a finite set of values from the coefficient field; in the example {1, ..., 1000}
|S|: the number of values in S; 1000 in the example
Pr[...]: the probability, over the random choice of the variables, of the event in brackets
≤: is at most
In words: a nonzero polynomial of degree d is zero at a random point with probability at most d divided by the number of values each variable can take. Degree 10 with 1000 choices per variable gives at most a 1 % chance.
```

So evaluate at one random point: if the result is nonzero, the polynomial is certainly nonzero. Repeating with independent points multiplies the bounds. The lemma needs S chosen from a coefficient field (or an integral domain) and the degree known in advance.

So polynomial identity testing is in **coRP**, and **no deterministic polynomial-time algorithm is known**. Kabanets and Impagliazzo (2004) showed that derandomising it would imply circuit lower bounds that nobody can currently prove.

### Primality: a derandomisation story

Miller–Rabin declares a composite "probably prime" with probability at most 1/4 per random base, and independent bases multiply:

```formula
ε_k ≤ (1/4)^k = 2^{−2 × k}
ε_20 ≤ 4^{−20} = 2^{−40} ≈ 9.1 × 10^{−13}
where
ε_k, ε_20: the probability that a composite number passes all k (or 20) rounds and is wrongly called prime
k: the number of independent rounds, each with a fresh random base; 20 in the second line
(1/4)^k: k copies of one-quarter multiplied together
≤: is at most
≈: approximately equal to
In words: each round at least quarters the chance of being fooled, so 20 rounds leave about one chance in a trillion. A real prime is never rejected: the error is one-sided.
```

This put PRIMES in coRP (composites are detected with one-sided error) decades ago. In 2002 the AKS algorithm put PRIMES in **P**. Practice still uses Miller–Rabin: it's much faster.

## How BPP relates to the rest

The proven containments:

```formula
P ⊆ ZPP ⊆ RP ⊆ BPP
RP ⊆ NP
BPP ⊆ PSPACE
BPP ⊆ Σ₂ ∩ Π₂
BPP ⊆ P/poly
where
P: the complexity class P: decision problems a deterministic algorithm solves in polynomial time (at most about n^k steps on an n-bit input, for some fixed k)
ZPP: zero-error probabilistic polynomial time: always correct, expected polynomial time
RP: randomised polynomial time with one-sided error: never accepts a no-instance, accepts each yes-instance with probability at least 1/2
BPP: bounded-error probabilistic polynomial time: decision problems a randomised polynomial-time algorithm answers correctly with probability at least 2/3 on every input
NP: the class NP (nondeterministic polynomial time): decision problems whose yes-answers have a short certificate checkable in polynomial time
PSPACE: decision problems solvable with a polynomial amount of memory, however long it takes
Σ₂: the second level of the polynomial hierarchy: problems of the form "there exists y such that for all z, a polynomial-time check R(x, y, z) holds", with y and z of polynomial length
Π₂: the mirror image of Σ₂: "for all y there exists z" (the complements of Σ₂ problems)
∩: intersection: the problems in both classes
P/poly: problems solvable by polynomial-size circuits, one circuit per input length (equivalently, polynomial time with a polynomial-length advice string that depends only on the input length)
⊆: "is contained in": every problem in the left class is also in the right class (the two may turn out to be equal)
In words: zero-error and one-sided randomness sit inside two-sided randomness; one-sided randomness is inside NP; and BPP fits inside polynomial space, inside the second level of the polynomial hierarchy, and inside polynomial-size circuits.
```

Why each holds:

- **The chain and RP inside NP.** A zero-error algorithm can be cut off and made one-sided; one-sided error is a special case of two-sided. For RP, an accepting coin sequence is a certificate, since no coin sequence makes it accept a no-instance.
- **BPP inside PSPACE.** Try every coin sequence one after another, count acceptances and reuse the space.
- **BPP inside Σ₂ ∩ Π₂** (Sipser, Gács and Lautemann, 1983). So if P equals NP, the whole polynomial hierarchy collapses to P and P equals BPP.
- **BPP inside P/poly**, counted below. Adleman (1978) proved it for one-sided error (RP); Bennett and Gill (1981) extended it to BPP, and the result is often called Adleman's theorem. The coin string it finds is non-uniform advice, not a known efficient way to find it.

Adleman's argument first amplifies the error below 2 to the power −n for inputs of n bits, then applies a **union bound** (the chance that at least one of several events happens is at most the sum of their chances):

```formula
Pr[some x fails] ≤ 2^n × ε
Pr[some x fails] < 2^n × 2^{−n} = 1
where
x: one of the possible inputs of length n
n: the input length, in bits
2^n: the number of different inputs of length n
ε: the error probability for each single input after amplification, below 2^{−n}
Pr[some x fails]: the probability that a random coin string gives a wrong answer on at least one input of length n
≤, <: is at most, is less than
In words: if every input fails on less than a 2 to the power −n share of coin strings, then fewer than all coin strings fail on any input, so at least one coin string is right on every input of that length. That string becomes the advice.
```

Open, and surprising: whether BPP is contained in NP. Nobody has proved that randomised algorithms can be simulated by short certificates.

Conjectured: P equals BPP. Impagliazzo and Wigderson (1997) proved a conditional version:

```formula
L ∈ E  and  size(L) = 2^{Ω(n)}
  gives  P = BPP
where
L: some decision problem
E: the class of problems solvable in time 2^{O(n)}, exponential with a linear exponent
∈: "is a member of"
size(L): the smallest number of gates in Boolean circuits deciding L on inputs of n bits
n: the input length, in bits
O(n): Big O: at most a constant times n, for large n
Ω(n): Big Omega: at least a constant times n, for large n
P: the complexity class P: decision problems a deterministic algorithm solves in polynomial time (at most about n^k steps on an n-bit input, for some fixed k)
BPP: bounded-error probabilistic polynomial time: decision problems a randomised polynomial-time algorithm answers correctly with probability at least 2/3 on every input
In words: if some exponential-time problem needs exponentially large circuits, then every randomised polynomial-time algorithm can be replaced by a deterministic one: P equals BPP.
```

The hypothesis is an unproven circuit lower bound, so the result is conditional. Under widely believed hardness assumptions, randomness gives at most a polynomial speed-up for decision problems. The primality story fits that pattern.

> [!note] What "P = BPP" would and wouldn't mean
> It wouldn't make randomness useless: randomised algorithms are often simpler or faster by a polynomial factor, and randomness is essential in cryptography, distributed protocols and sampling. It would mean randomness can't turn exponential into polynomial for decision problems.

## Quantum: BQP

A quantum computer on a register of qubits has a state described by complex **amplitudes**, one per possible bit string. Quantum gates update all of them at once, and measurement returns a single outcome:

```formula
N_amp = 2^n
N_amp = 2^50 ≈ 1.1 × 10^15   for n = 50
Pr[x] = |α_x|^2
where
N_amp: the number of complex amplitudes needed to describe the state
n: the number of qubits; 50 in the second line
2^n: n copies of 2 multiplied together: one amplitude per n-bit string
x: one possible measurement outcome, an n-bit string
α_x: alpha sub x, the amplitude (a complex number) attached to outcome x
|α_x|: the magnitude (size) of that complex number
Pr[x]: the probability that measuring the register gives outcome x; these probabilities add up to 1
≈: approximately equal to
In words: 50 qubits need about a million billion amplitudes to describe classically, but measuring them gives just one 50-bit outcome, chosen with probability equal to the squared size of its amplitude.
```

The power isn't "trying everything in parallel"; measurement gives you one outcome. It is **interference**: arranging for amplitudes of wrong answers to cancel and right answers to reinforce.

**BQP** is the set of decision problems solvable by a polynomial-time-uniform family of polynomial-size quantum circuits with error at most 1/3 (amplifiable, as for BPP).

What's proven:

```formula
P ⊆ BPP ⊆ BQP ⊆ PP ⊆ PSPACE
where
P: the complexity class P: decision problems a deterministic algorithm solves in polynomial time (at most about n^k steps on an n-bit input, for some fixed k)
BPP: bounded-error probabilistic polynomial time: decision problems a randomised polynomial-time algorithm answers correctly with probability at least 2/3 on every input
BQP: bounded-error quantum polynomial time: decision problems a quantum computer solves in polynomial time with error at most 1/3 on every input
PP: probabilistic polynomial time: a randomised polynomial-time algorithm is right with probability strictly more than 1/2, possibly by a vanishingly small margin, so the answer cannot be amplified efficiently
PSPACE: decision problems solvable with a polynomial amount of memory, however long it takes
⊆: "is contained in": every problem in the left class is also in the right class (the two may turn out to be equal)
In words: everything a classical randomised computer can do efficiently, a quantum computer can too, and everything a quantum computer can do efficiently fits inside PP and inside polynomial space.
```

- BQP inside PSPACE (Bernstein and Vazirani, 1993): sum the amplitudes path by path, reusing space.
- BQP inside PP (Adleman, DeMarrais and Huang, 1997).

That last containment is why a classical-versus-quantum separation is so hard to prove:

```formula
BPP ≠ BQP  gives  BPP ≠ PSPACE
BPP ≠ PSPACE  gives  P ≠ PSPACE
where
BPP: bounded-error probabilistic polynomial time: decision problems a randomised polynomial-time algorithm answers correctly with probability at least 2/3 on every input
BQP: bounded-error quantum polynomial time: decision problems a quantum computer solves in polynomial time with error at most 1/3
PSPACE: decision problems solvable with a polynomial amount of memory
P: the complexity class P: decision problems a deterministic algorithm solves in polynomial time (at most about n^k steps on an n-bit input, for some fixed k)
≠: "is not equal to": the two classes contain different problems
In words: BPP sits inside BQP, which sits inside PSPACE. If BQP were strictly bigger than BPP, PSPACE would be too; and since P sits inside BPP, P would then differ from PSPACE, an open problem nobody can currently touch.
```

So proving BQP and BPP different would prove P and PSPACE different, which is far beyond current techniques. This rules out claiming a proven separation of BQP from BPP. It does not rule out proven query-complexity advantages or smaller speed-ups within polynomial time.

### Shor and Grover

- **Shor (1994)** factors integers and computes discrete logarithms in polynomial time on a quantum computer. The associated factoring decision problem is in BQP; Shor also recovers the factors. It is **not known** to be outside BPP; the best known classical algorithm (the number field sieve) is sub-exponential. This breaks RSA and elliptic-curve cryptography once large fault-tolerant machines exist, which is why NIST standardised post-quantum schemes such as ML-KEM (FIPS 203) in 2024. Published resource estimates for RSA-2048 have fallen over time (Gidney's 2025 estimate is under a million noisy qubits running for under a week). This is a dated resource estimate under stated hardware assumptions, not a measurement of currently available machines.
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

- **Oracle separations**: Raz and Tal (2018) found an oracle relative to which BQP is not contained in the polynomial hierarchy. This is evidence, not proof, about the real world (recall relativisation from lesson 1).
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

## Key takeaways
- RP and coRP have one-sided error (each extra run halves the error); BPP has two-sided error (majority vote, error falls exponentially); ZPP, the overlap of RP and coRP, is zero-error, expected polynomial time.
- Freivalds checks a claimed matrix product with three matrix–vector products per trial; Schwartz–Zippel puts polynomial identity testing in coRP, with no deterministic polynomial algorithm known.
- Proven: P inside BPP, BPP inside Σ₂ ∩ Π₂ and inside P/poly. Conjectured: P equals BPP (implied by plausible circuit lower bounds). Open: whether BPP is inside NP.
- Proven: BPP inside BQP inside PP inside PSPACE; separating BQP from BPP would separate P from PSPACE. Query-model advantages such as Grover's do not require that class separation.
- Shor puts factoring in BQP; Grover gives a proven-optimal quadratic speed-up for black-box search. NP inside BQP is believed false.

## Further reading
- [BPP (complexity) — Wikipedia](https://en.wikipedia.org/wiki/BPP_(complexity))
- [RP (complexity) — Wikipedia](https://en.wikipedia.org/wiki/RP_(complexity))
- [Freivalds' algorithm — Wikipedia](https://en.wikipedia.org/wiki/Freivalds%27_algorithm)
- [Schwartz–Zippel lemma — Wikipedia](https://en.wikipedia.org/wiki/Schwartz%E2%80%93Zippel_lemma)
- [BQP — Wikipedia](https://en.wikipedia.org/wiki/BQP)
- [Shor's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Shor%27s_algorithm)
- [Grover's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Grover%27s_algorithm)
- [Complexity Zoo](https://complexityzoo.net/Complexity_Zoo)
