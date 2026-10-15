---
id: cplx-np-certificates
title: "Checking certificates in NP"
level: basic
minutes: 4
summary: "NP requires polynomial-size certificates and a polynomial-time verifier."
sourceLesson: cplx-p-np
---

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
In words: x is a yes-instance exactly when some certificate, of length bounded by a fixed polynomial in the length of x, makes the fast checker V say yes. For a no-instance, every certificate is rejected.
```

For subset sum, the certificate is the subset itself. Checking it is one addition per chosen element; additions on binary integers cost polynomially many bit operations:

```python
def verify_subset_sum(S, T, idx):
    # idx is decoded as a set of positions.
    # Reject indices outside the input list.
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

The Python demonstration expects its certificate argument to have been decoded as a set of distinct integer positions, with an encoded size bounded polynomially in the input. A full verifier first rejects malformed encodings; a list containing repeated positions is not that certificate format. The examples use sets, so an input element cannot be counted twice.

## Key takeaways

- NP requires polynomial-size certificates and a polynomial-time verifier.
- A verifier checks a supplied candidate; it need not find one.
- Every P problem is in NP because the verifier can solve it directly.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
