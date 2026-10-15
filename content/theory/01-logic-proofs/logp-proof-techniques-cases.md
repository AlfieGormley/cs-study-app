---
id: logp-proof-techniques-cases
title: Exhaustive cases and both directions
level: intermediate
minutes: 3
sourceLesson: logp-proof-techniques
summary: Cases must cover every allowed input.
---

## Proof by cases

If every possibility falls into one of several cases, prove the claim in each case separately. This is the valid argument form called **proof by cases** (or disjunction elimination):

```formula
p ∨ q, p → r, q → r ⊢ r
where
p, q: the cases, propositions that are true or false
r: the claim being proved
∨: OR (inclusive): at least one case holds
→: implies: "if this case, then the claim"
,: separates the premises
⊢: "therefore": the conclusion on the right follows from the premises on the left
In words: if one of the cases must hold, and each case leads to r, then r holds.
```

**Claim: no sum of two squares leaves remainder 3 when divided by 4.** First, squares mod 4 (the remainder after dividing by 4). Every integer n is even or odd, which gives two cases:

```formula
n = 2k:      n^2 = 4k^2
n = 2k + 1:  n^2 = 4 × (k^2 + k) + 1
where
n: any integer
k: the integer from the definition of even (first line) or odd (second line)
n^2: n squared
In words: an even number's square is a multiple of 4 (remainder 0), and an odd number's square is a multiple of 4 plus 1 (remainder 1).
```

So any square leaves remainder 0 or 1. A sum a² + b² of two squares leaves 0 plus 0, 0 plus 1 or 1 plus 1, that is 0, 1 or 2. Never 3. ∎

So 7, 11, 15, 19, ... can never be written as a sum of two squares. A bounded search over many target integers would not prove the universal claim. For one fixed nonnegative target, exhaustive search over bounded candidate squares can prove that target has no representation; the case split handles all targets at once.

The cases must be **exhaustive**. Forgetting a case (zero, negatives, the empty list) is the proof equivalent of a missing branch in code.


## If and only if

To prove "p if and only if q" (written p if and only if q), prove both directions: p implies q **and** q implies p. They often need different techniques.

**Claim: n is even if and only if n squared is even.** Forwards ( implies ): if n equals 2k, then n squared is twice an integer:

```formula
n^2 = (2k)^2 = 4k^2 = 2 × (2k^2)
where
n: an even integer, n = 2 × k
k: an integer
n^2: n squared
In words: the square of an even number is 2 times an integer, so it is even.
```

Backwards (←): if n squared is even then n is even, which we proved above by contrapositive. Both directions hold. ∎

A common slip is proving one direction twice, once forwards and once by its contrapositive, which proves only one implication.


## Key takeaways
- Cases must cover every allowed input.
- An if-and-only-if proof needs both directions; proving an implication and its contrapositive gives only one direction.

## Further reading
- [MIT Mathematics for Computer Science](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/mit6_042js15_textbook.pdf)
- [Euclid's theorem — Wikipedia](https://en.wikipedia.org/wiki/Euclid%27s_theorem)
