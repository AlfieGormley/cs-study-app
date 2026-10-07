---
id: cplx-p-np
title: P and NP
level: basic
minutes: 13
summary: What "efficient" means, the classes P, NP and coNP defined by solving versus checking, what is proven about them and why P vs NP is still open.
---

Computability asks whether a problem can be solved by an algorithm at all. **Complexity theory** asks a sharper question: how much time or memory does it take, as the input grows?

The headline result of the field is a question nobody has answered. Is every problem whose solutions are easy to **check** also easy to **solve**? That is the **P vs NP** problem, and this lesson sets up exactly what it means.

## Measuring cost

Three conventions make the theory work.

1. **Decision problems.** We mostly study yes/no questions: "does this graph have a route of length at most 100?" rather than "find the shortest route". A yes/no problem is just a set of inputs (a **language**) whose answer is yes.
2. **Input size n is measured in bits.** A number N takes about log₂ N bits to write down, not N.
3. **Worst case, asymptotically.** An algorithm runs in time O(f(n)) if, for every input of n bits, it takes at most about c·f(n) steps for large n.

Optimisation and decision versions are usually equally hard up to a polynomial factor: if you can answer "is there a route of cost at most k?" you can binary-search on k to find the optimum cost.

## P: the problems we can solve efficiently

**P** is the set of decision problems solvable by a deterministic algorithm in time O(n^k) for some constant k.

Why draw the line at polynomials?

- **Closure.** A polynomial-time algorithm that calls a polynomial-time subroutine a polynomial number of times is still polynomial. Compose efficient pieces and you stay efficient.
- **Robustness.** Standard classical models, such as Turing machines and RAM machines with suitably bounded word operations, simulate each other with polynomial overhead. The broader claim that classical computation efficiently simulates every physically realisable computation is an extended Church–Turing thesis, not a theorem; quantum computation challenges it.
- **The gap is enormous.** At n = 100, n³ is a million steps. 2ⁿ is about 1.3 × 10³⁰, far beyond any computer.

Problems known to be in P include shortest paths, maximum matching, 2-SAT, linear programming (proven in 1979 with the ellipsoid method) and primality testing (the AKS algorithm, 2002).

> [!warning] Polynomial is not the same as fast
> An O(n¹⁰⁰) algorithm is in P but useless. In practice, natural problems in P tend to have small exponents, which is part of why the definition has stuck. Treat "in P" as "not hopelessly exponential", not as "fast".

### The unary trap: pseudo-polynomial time

**Subset sum** asks: given nonnegative integers S and target T, does some subset of S add up to exactly T? A textbook dynamic program runs in O(n·T) time. That looks polynomial, but T is written in about log₂ T bits. A 64-bit target makes T up to about 1.8 × 10¹⁹, so O(n·T) is exponential in the input size.

Such algorithms are **pseudo-polynomial**: polynomial in the *value* of the numbers, not their length. Subset sum is not known to be in P.

## NP: the problems whose answers we can check

A problem is in **NP** if every yes-instance has a short **certificate** (a witness) that a fast algorithm can check.

Formally, L is in NP if there is a polynomial-time **verifier** V and a polynomial p such that:

```
x in L  <=>  there exists c with
             |c| <= p(|x|) and V(x, c) = 1
```

For subset sum, the certificate is the subset itself. Checking it is one addition per element:

```python
def verify_subset_sum(S, T, idx):
    # idx: certificate, a set of positions
    n = len(S)
    if not all(0 <= i < n for i in idx):
        return False
    return sum(S[i] for i in idx) == T

S, T = [3, 34, 4, 12, 5, 2], 9
print(verify_subset_sum(S, T, {2, 4}))
# True: 4 + 5 = 9
print(verify_subset_sum(S, T, {0, 1}))
# False: 3 + 34 = 37
```

The verifier never searches. It only checks. Finding a good certificate might need trying up to 2ⁿ subsets; checking one takes linear time.

> [!note] NP does not stand for "not polynomial"
> NP means **nondeterministic polynomial time**. The equivalent original definition: a nondeterministic Turing machine (one that can "guess" at each step) accepts in polynomial time. Guess the certificate, then run the verifier. Every problem in P is also in NP, so "NP" is not a label for hard problems.

Other NP problems and their certificates:

| Problem | Certificate |
|---|---|
| SAT | A satisfying assignment |
| Hamiltonian cycle | The cycle's vertex order |
| 3-colouring | A colour per vertex |
| Composite N | A factor 1 < d < N |

## coNP: short proofs of "no"

**coNP** contains the complements of NP problems: problems where every *no*-instance has a short certificate. UNSAT ("this formula has no satisfying assignment") and TAUTOLOGY are the standard examples.

The asymmetry is real. To convince you a formula is satisfiable, I hand you an assignment. To convince you it is *unsatisfiable*, nobody knows a short certificate in general; SAT solvers emit resolution proofs, but for some formulas (like the pigeonhole principle) every resolution proof is exponentially long.

Some problems are in **NP ∩ coNP**: both answers have short certificates. "Does N have a prime factor below k?" is one. A yes-certificate is the factor; a no-certificate is the full prime factorisation (each prime can itself be checked in polynomial time, by AKS). Problems in NP ∩ coNP are widely believed not to be NP-complete, since that would imply NP = coNP.

## What is proven, and what isn't

Proven facts:

- **P ⊆ NP.** If you can solve it, the verifier can ignore the certificate and solve it.
- **NP ⊆ EXPTIME.** Try all 2^p(n) certificates.
- **P ≠ EXPTIME.** The *time hierarchy theorem* (Hartmanis and Stearns, 1965) shows that more time solves strictly more problems.
- So in the chain P ⊆ NP ⊆ PSPACE ⊆ EXPTIME, **at least one** inclusion is strict. Nobody knows which.
- **If P = NP then NP = coNP** (P is closed under complement).

Open problems:

- **P vs NP.** Almost all experts conjecture P ≠ NP. It is one of the Clay Millennium Prize problems ($1 million).
- **NP vs coNP.** Conjectured different.
- Whether graph isomorphism or factoring is in P. Neither is known to be NP-complete; Babai (2015, with a fix in 2017) put graph isomorphism in quasi-polynomial time, 2^O((log n)^c).

```
+-------------- EXPTIME -------------+
| +------------ PSPACE ------------+ |
| | +---- NP -----+                | |
| | |        +----+---- coNP --+   | |
| | |        | P  |            |   | |
| | |        +----+------------+   | |
| | +-------------+                | |
| +--------------------------------+ |
+------------------------------------+
 P sits inside NP ∩ coNP. The picture
 assumes P != NP != coNP; of the
 separations, only P != EXPTIME is
 proven.
```

### Why it is so hard to prove

Three known **barriers** rule out whole families of proof techniques:

- **Relativisation** (Baker, Gill and Solovay, 1975): there are oracles relative to which P = NP and others where P ≠ NP, so simulation-and-diagonalisation arguments like the halting proof cannot settle it.
- **Natural proofs** (Razborov and Rudich, 1994): a broad class of circuit lower-bound arguments would, if they worked, break pseudorandom functions that are believed secure.
- **Algebrisation** (Aaronson and Wigderson, 2008) extends the relativisation barrier.

## Why practitioners care

- **Recognising the wall.** If your scheduling problem is NP-complete (lesson 2), stop hunting for a fast exact algorithm for all inputs and reach for approximations, heuristics or solvers (lesson 4).
- **Cryptography.** Secure encryption needs one-way functions, and if one-way functions exist then P ≠ NP. The converse is not known: P ≠ NP alone would not guarantee secure cryptography, because NP-hardness is about the worst case and crypto needs problems hard on *average*.
- **Worst case is not typical case.** Modern SAT solvers routinely handle industrial instances with millions of variables. Under P ≠ NP, NP-hardness rules out a polynomial-time exact algorithm for all inputs; it does not say this particular instance is hard.

## Key takeaways
- P: solvable in polynomial time. NP: yes-answers have polynomial-size certificates checkable in polynomial time. coNP: the same for no-answers.
- NP means nondeterministic polynomial, not "not polynomial"; P ⊆ NP is proven.
- Input size is in bits: an O(n·T) algorithm for subset sum is pseudo-polynomial, not polynomial.
- Proven: P ⊆ NP ⊆ PSPACE ⊆ EXPTIME and P ≠ EXPTIME. Open: P vs NP and NP vs coNP, both conjectured to be different.
- Relativisation, natural proofs and algebrisation explain why standard techniques can't resolve P vs NP.

## Further reading
- [P versus NP problem — Wikipedia](https://en.wikipedia.org/wiki/P_versus_NP_problem)
- [P vs NP — Clay Mathematics Institute](https://www.claymath.org/millennium/p-vs-np/)
- [NP (complexity) — Wikipedia](https://en.wikipedia.org/wiki/NP_(complexity))
- [Co-NP — Wikipedia](https://en.wikipedia.org/wiki/Co-NP)
- [Pseudo-polynomial time — Wikipedia](https://en.wikipedia.org/wiki/Pseudo-polynomial_time)
- [Computational Complexity: A Modern Approach (Arora and Barak, draft)](https://www.cs.princeton.edu/theory/complexity/)
