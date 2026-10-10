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
3. **Worst case, asymptotically.** We count the steps an algorithm takes on its *worst* input of a given size, and only care how that count grows as the size grows.

Convention 2 in symbols: the number of bits needed to write a whole number grows with its logarithm, not with its value.

```formula
b ≈ log_2(N)
b ≈ log_2(1000) ≈ 10 bits   for N = 1000
where
b: the number of bits (binary digits) needed to write the number down
N: the number itself, a positive whole number
log_2: logarithm base 2: log_2(N) is the power you must raise 2 to in order to get N, so log_2(1024) = 10
≈: approximately equal to (the exact count is log_2(N) rounded down, plus 1)
bits: the unit of the result: binary digits, each 0 or 1
In words: a number about a thousand needs only about 10 bits. Doubling N adds just one bit, so an input's size in bits can be tiny compared with the values written in it.
```

Convention 3 in symbols is **Big O** notation. It is how the rest of this module states running times.

```formula
T(n) = O(f(n))   means
T(n) ≤ c × f(n)   for all n ≥ n_0
where
T(n): the worst-case number of steps the algorithm takes on any input of n bits
n: the input size, in bits
f(n): the comparison function, such as n^2 or 2^n
O(f(n)): Big O of f(n): "grows at most as fast as a constant times f(n), once n is large enough"
c: a fixed positive constant that does not depend on n
n_0: a threshold size; the bound only has to hold for inputs at least this big
≤: is less than or equal to
≥: is greater than or equal to
In words: the running time is O(f(n)) when, beyond some input size, it never exceeds a fixed constant times f(n). An algorithm that takes 3 × n^2 + 5 × n steps is O(n^2), because with c = 4 the bound holds for every n ≥ 5.
```

Big O ignores constant factors and small inputs on purpose: it describes the shape of the growth, not the exact time on a particular machine.

Optimisation and decision versions are usually equally hard up to a polynomial factor: if you can answer "is there a route of cost at most k?" you can binary-search on k to find the optimum cost.

## P: the problems we can solve efficiently

**P** (polynomial time) is the set of decision problems solvable by a deterministic algorithm (one with no randomness or guessing) whose worst-case running time is bounded by a polynomial in the input size.

```formula
T(n) = O(n^k)   for some k
where
T(n): the worst-case number of steps the algorithm takes on an input of n bits
n: the input size, in bits
k: a constant exponent that does not grow with n, such as 1, 2 or 3
n^k: k copies of n multiplied together (n to the power k)
O(...): Big O: "at most a constant times this, for large n"
In words: a problem is in P when some deterministic algorithm solves every input in at most about n to the power k steps, for one fixed k. Sorting-style O(n^2) and shortest-path-style O(n^3) bounds qualify; 2 to the power n does not.
```

Why draw the line at polynomials?

- **Closure.** A polynomial-time algorithm that calls a polynomial-time subroutine a polynomial number of times is still polynomial. Compose efficient pieces and you stay efficient.
- **Robustness.** Standard classical models, such as Turing machines and RAM machines with suitably bounded word operations, simulate each other with polynomial overhead. The broader claim that classical computation efficiently simulates every physically realisable computation is an extended Church–Turing thesis, not a theorem; quantum computation challenges it.
- **The gap is enormous.** At an input size of 100, a cubic algorithm takes a million steps while an exponential one takes about 10³⁰, far beyond any computer (worked out below).

The calculation behind the last point:

```formula
n^3 = 100^3 = 10^6 steps
2^n = 2^100 ≈ 1.3 × 10^30 steps
where
n: the input size; here n = 100
n^3: n to the power 3 (n × n × n), the step count of a cubic, polynomial-time algorithm
2^n: n copies of 2 multiplied together, the step count of an exponential-time algorithm
≈: approximately equal to
steps: the unit of running time: one basic operation of the machine
In words: at size 100 the cubic algorithm needs a million steps, a fraction of a second; the exponential one needs about 1.3 million million million million million steps. At a billion steps per second that is around 4 × 10^13 years.
```

Problems known to be in P include shortest paths, maximum matching, 2-SAT, linear programming (proven in 1979 with the ellipsoid method) and primality testing (the AKS algorithm, 2002).

> [!warning] Polynomial is not the same as fast
> An O(n¹⁰⁰) algorithm is in P but useless. In practice, natural problems in P tend to have small exponents, which is part of why the definition has stuck. Treat "in P" as "not hopelessly exponential", not as "fast".

### The unary trap: pseudo-polynomial time

**Subset sum** asks: given a list S of nonnegative integers and a target T, does some subset of S add up to exactly T? A textbook dynamic program fills a table with one row per number and one column per possible total, so its running time grows with the *value* of T. That looks polynomial, but T is written in only about log₂ T bits:

```formula
t = O(n × T)
T < 2^b
T < 2^64 ≈ 1.8 × 10^19   for b = 64
where
t: the running time of the dynamic program, in steps
n: how many numbers are in the list S
T: the target total (a value, not a length)
b: the number of bits used to write T in the input
2^b: 2 to the power b; a b-bit number is always smaller than this
O(...): Big O: "at most a constant times this, for large inputs"
≈: approximately equal to
In words: the running time is proportional to n times the target's value, and the value can be exponential in its length b. Adding one bit to T doubles the possible work, so the algorithm is exponential in the input size.
```

With a 64-bit target the table can need about 1.8 × 10¹⁹ columns, even though the target takes only 8 bytes to write down.

Such algorithms are **pseudo-polynomial**: polynomial in the *value* of the numbers, not their length. Subset sum is not known to be in P.

## NP: the problems whose answers we can check

A problem is in **NP** if every yes-instance has a short **certificate** (a witness) that a fast algorithm can check.

Formally, a problem L is in NP if there is a polynomial-time **verifier** V (a checking algorithm) and a polynomial p such that:

```formula
x ∈ L   iff   ∃ c with
  |c| ≤ p(|x|)   and   V(x, c) = 1
where
L: the problem, viewed as the set of inputs whose answer is yes (its language)
x: an input (a problem instance), written as a string of bits
∈: "is a member of"; x ∈ L means x is a yes-instance
∃: "there exists": at least one such c can be found
c: a certificate (witness): extra information offered as evidence that x is a yes-instance
|c|, |x|: the length of c or x, in bits
p: a fixed polynomial, such as p(m) = m^2, that caps how long a certificate may be
V(x, c): the verifier, a polynomial-time algorithm that reads x and c and outputs 1 (accept) or 0 (reject)
≤: is less than or equal to
In words: x is a yes-instance exactly when some certificate, not much longer than x itself, makes the fast checker V say yes. For a no-instance, every certificate is rejected.
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

The verifier never searches. It only checks. Finding a good certificate by brute force means trying subsets, and the number of subsets explodes:

```formula
N_sub = 2^n
N_sub = 2^6 = 64   for n = 6
where
N_sub: the number of different subsets of the list (including the empty subset)
n: how many numbers are in the list; the example S above has n = 6
2^n: n copies of 2 multiplied together: each number is either in or out of a subset
In words: every extra number doubles the subsets to search. Six numbers give 64 subsets; 60 numbers give about 10^18. Checking any one subset still takes only one addition per element.
```

> [!note] NP does not stand for "not polynomial"
> NP means **nondeterministic polynomial time**. The equivalent original definition: a nondeterministic Turing machine (one that can "guess" at each step) accepts in polynomial time. Guess the certificate, then run the verifier. Every problem in P is also in NP, so "NP" is not a label for hard problems.

Other NP problems and their certificates:

| Problem | Certificate |
|---|---|
| SAT | A satisfying assignment |
| Hamiltonian cycle | The cycle's vertex order |
| 3-colouring | A colour per vertex |
| Composite number | A factor other than 1 and itself |

For the last row the check is a single division:

```formula
1 < d < N   and   N mod d = 0
91 mod 7 = 0   for N = 91, d = 7
where
N: the whole number being tested for compositeness (having a factor other than 1 and itself)
d: the certificate: a proposed factor of N
mod: the remainder after division, so N mod d = 0 means d divides N exactly
<: is less than
In words: to prove N is composite, hand over a factor strictly between 1 and N; anyone can confirm it by one division. 91 = 7 × 13, so the certificate 7 proves 91 is composite.
```

## coNP: short proofs of "no"

**coNP** contains the complements of NP problems: problems where every *no*-instance has a short certificate. UNSAT ("this formula has no satisfying assignment") and TAUTOLOGY are the standard examples.

The asymmetry is real. To convince you a formula is satisfiable, I hand you an assignment. To convince you it is *unsatisfiable*, nobody knows a short certificate in general; SAT solvers emit resolution proofs, but for some formulas (like the pigeonhole principle) every resolution proof is exponentially long.

Some problems are in both classes at once, where both answers have short certificates:

```formula
L ∈ NP ∩ coNP
where
L: a decision problem
∈: "is a member of"
NP: the class NP (nondeterministic polynomial time): decision problems whose yes-answers have a short certificate checkable in polynomial time
coNP: the class coNP: decision problems whose no-answers have a short certificate checkable in polynomial time (the complements of NP problems)
∩: intersection: the problems that belong to both classes
In words: L has short, quickly checkable proofs for its yes-answers and for its no-answers.
```

"Does N have a prime factor below k?" is one. A yes-certificate is the factor; a no-certificate is the full prime factorisation (each prime can itself be checked in polynomial time, by AKS). Problems in both NP and coNP are widely believed not to be NP-complete, since that would force NP and coNP to be equal.

## What is proven, and what isn't

The proven facts fit in one chain of classes, plus one separation:

```formula
P ⊆ NP ⊆ PSPACE ⊆ EXPTIME
P ≠ EXPTIME
P = NP   gives   NP = coNP
where
P: the complexity class P: decision problems a deterministic algorithm solves in polynomial time (at most about n^k steps for some fixed k)
NP: the class NP: decision problems whose yes-answers have a short certificate checkable in polynomial time
coNP: the class coNP: decision problems whose no-answers have a short certificate checkable in polynomial time
PSPACE: decision problems solvable using a polynomial amount of memory (at most about n^k bits), however long it takes
EXPTIME: decision problems solvable in exponential time: at most about 2 to the power n^k steps for some fixed k
⊆: "is contained in": every problem in the left class is also in the right class (the two may turn out to be equal)
≠: "is not equal to": here, some problem is in EXPTIME but not in P
n: the input size, in bits
k: a fixed constant exponent
In words: each class in the chain sits inside the next; P is definitely smaller than EXPTIME; and if P were equal to NP, then NP would also equal coNP.
```

Why each piece holds:

- **P is inside NP.** If you can solve the problem, the verifier can ignore the certificate and solve it.
- **NP is inside EXPTIME.** Try every possible certificate (counted below).
- **P is not all of EXPTIME.** The *time hierarchy theorem* (Hartmanis and Stearns, 1965) shows that more time solves strictly more problems.
- So in the chain, **at least one** inclusion is strict. Nobody knows which.
- **If P equals NP, NP equals coNP**, because P is closed under complement: flip the answer of a polynomial-time algorithm and it is still polynomial-time.

The brute-force argument for NP inside EXPTIME counts certificates:

```formula
N_cert = 2^{p(n)}
t ≤ 2^{p(n)} × q(n)
where
N_cert: the number of possible certificates of length p(n) bits
p(n): the polynomial limit on certificate length, in bits, for an input of n bits
n: the input size, in bits
t: the total running time of the brute-force search, in steps
q(n): the polynomial running time of the verifier on one certificate
2^{p(n)}: 2 to the power p(n): each of the p(n) bits can be 0 or 1
≤: is at most
In words: try every possible certificate and run the checker on each. That is exponentially many polynomial-time checks, which is still exponential time.
```

Open problems:

- **P vs NP.** Almost all experts conjecture P ≠ NP. It is one of the Clay Millennium Prize problems ($1 million).
- **NP vs coNP.** Conjectured different.
- Whether graph isomorphism or factoring is in P. Neither is known to be NP-complete; Babai (2015, with a fix in 2017) put graph isomorphism in quasi-polynomial time (below).

**Quasi-polynomial time** sits between polynomial and exponential:

```formula
t = 2^{O((log n)^c)}
where
t: the running time, in steps
n: the input size, in bits
log: the logarithm (base 2 here; the base only changes the constant)
c: a fixed constant; for c = 1 this is just a polynomial
O(...): Big O: "at most a constant times this, for large n"
2^{...}: 2 raised to that power
In words: two to the power of a polylogarithm. It grows faster than any polynomial (for c > 1) but far slower than 2 to the power n.
```

At an input size of a million, (log₂ n)² is about 400, so 2 to that power is huge but nothing like 2 to the power one million.

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

- **Relativisation** (Baker, Gill and Solovay, 1975): there are oracles (imaginary black-box subroutines) relative to which P equals NP, and others where they differ, so simulation-and-diagonalisation arguments like the halting proof cannot settle it.
- **Natural proofs** (Razborov and Rudich, 1994): a broad class of circuit lower-bound arguments would, if they worked, break pseudorandom functions that are believed secure.
- **Algebrisation** (Aaronson and Wigderson, 2008) extends the relativisation barrier.

## Why practitioners care

- **Recognising the wall.** If your scheduling problem is NP-complete (lesson 2), stop hunting for a fast exact algorithm for all inputs and reach for approximations, heuristics or solvers (lesson 4).
- **Cryptography.** Secure encryption needs one-way functions, and if one-way functions exist then P and NP are different. The converse is not known: P ≠ NP alone would not guarantee secure cryptography, because NP-hardness is about the worst case and crypto needs problems hard on *average*.
- **Worst case is not typical case.** Modern SAT solvers routinely handle industrial instances with millions of variables. If P and NP differ, NP-hardness rules out a polynomial-time exact algorithm for all inputs; it does not say this particular instance is hard.

## Key takeaways
- P: solvable in polynomial time. NP: yes-answers have polynomial-size certificates checkable in polynomial time. coNP: the same for no-answers.
- NP means nondeterministic polynomial, not "not polynomial"; every problem in P is in NP (proven).
- Input size is in bits: subset sum's dynamic program, linear in the target's value, is pseudo-polynomial, not polynomial.
- Proven: P is inside NP, inside PSPACE, inside EXPTIME, and P is strictly smaller than EXPTIME. Open: P vs NP and NP vs coNP, both conjectured to be different.
- Relativisation, natural proofs and algebrisation explain why standard techniques can't resolve P vs NP.

## Further reading
- [P versus NP problem — Wikipedia](https://en.wikipedia.org/wiki/P_versus_NP_problem)
- [P vs NP — Clay Mathematics Institute](https://www.claymath.org/millennium/p-vs-np/)
- [NP (complexity) — Wikipedia](https://en.wikipedia.org/wiki/NP_(complexity))
- [Co-NP — Wikipedia](https://en.wikipedia.org/wiki/Co-NP)
- [Pseudo-polynomial time — Wikipedia](https://en.wikipedia.org/wiki/Pseudo-polynomial_time)
- [Computational Complexity: A Modern Approach (Arora and Barak, draft)](https://www.cs.princeton.edu/theory/complexity/)
