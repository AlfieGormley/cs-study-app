---
id: logp-proof-techniques
title: Proof techniques (direct, contrapositive, contradiction)
level: intermediate
minutes: 14
summary: How to prove a claim rather than test it, using direct proof, contrapositive, contradiction and cases, plus existence proofs, counterexamples and the mistakes that make a proof worthless.
---

Tests show that code works on the inputs you tried. A **proof** shows that a claim holds for *every* input, including the ones nobody thought of. Euler's polynomial n² + n + 41 is prime for n = 0 to 39 and then fails at n = 40. Forty passing tests, one false claim.

Engineers need proofs more often than they expect: to convince yourself an algorithm is correct, that a lower bound is real, that an optimisation is safe, or that a distributed protocol cannot lose data. This lesson covers the core techniques. Almost every proof you will meet is built from them.

## Start with definitions

Most proof failures start with a vague definition. A proof can only use what a term precisely means.

| Term | Definition |
|---|---|
| n is even | n = 2k for some integer k |
| n is odd | n = 2k + 1 for some integer k |
| a ∣ b (a divides b) | b = a·k for some integer k |
| r is rational | r = a/b, integers a, b, b ≠ 0 |
| p is prime | integer p > 1, only positive divisors 1 and p |

Every integer is either even or odd, and not both. We will use that fact freely.

## Direct proof

To prove p → q directly: **assume p, then derive q** step by step, using definitions and previously proven facts.

> [!example] Claim: the sum of two odd integers is even
> Assume m and n are odd. By definition, m = 2a + 1 and n = 2b + 1 for some integers a, b.
>
> Then m + n = 2a + 2b + 2 = 2(a + b + 1).
>
> Since a + b + 1 is an integer, m + n is even. ∎

Note what the proof does *not* do: it never picks specific numbers. "3 + 5 = 8 is even" is an example, not a proof. The variables a and b stand for every possible case at once.

A second example, about divisibility, shows the same pattern of unpacking definitions:

```
Claim: if a ∣ b and b ∣ c then a ∣ c.

Assume b = a·j and c = b·k
  for integers j, k.
Then c = (a·j)·k = a·(j·k).
j·k is an integer, so a ∣ c.  ∎
```

The recipe: write down what you are given, using definitions. Write down what you need to reach, using definitions. Then close the gap with algebra.

## Proof by contrapositive

Recall that p → q ≡ ¬q → ¬p. So instead of proving p → q, you may prove ¬q → ¬p directly. This helps when ¬q gives you something concrete to work with and p does not.

> [!example] Claim: if n² is even, then n is even
> A direct attempt starts with n² = 2k and needs a square root, which goes nowhere.
>
> Contrapositive: if n is **odd**, then n² is **odd**.
>
> Assume n = 2k + 1. Then n² = 4k² + 4k + 1 = 2(2k² + 2k) + 1, which is odd. ∎

Another one, where the contrapositive turns an awkward "or" into a clean "and":

```
Claim: if x + y ≥ 100 then
       x ≥ 50 or y ≥ 50.

Contrapositive:
  if x < 50 and y < 50
  then x + y < 100.

Proof: x + y < 50 + 50 = 100.  ∎
```

This is the pigeonhole principle in miniature. The same reasoning appears in capacity planning: if two shards each hold under half the keys, they cannot together hold them all.

## Proof by contradiction

To prove a statement S: **assume ¬S and derive something impossible**, such as a statement and its negation. Since a true assumption cannot lead to a false conclusion, ¬S must be false, so S is true.

The two classic examples are over 2,000 years old.

### √2 is irrational

```
Suppose √2 is rational: √2 = a/b,
with integers a, b, b ≠ 0, and the
fraction in lowest terms.

Square:      2 = a²/b²
so           a² = 2b²
a² is even, so a is even
  (previous example).
Write a = 2k:  4k² = 2b²
so             b² = 2k²
b² is even, so b is even.

a and b are both even, so a/b is not
in lowest terms. Contradiction.   ∎
```

The proof uses the earlier contrapositive result as a **lemma**. Building proofs from smaller proven pieces is like building programs from tested functions.

### There are infinitely many primes (Euclid)

```
Suppose there are finitely many:
  p1, p2, ..., pk.
Let N = p1·p2·...·pk + 1.
N > 1, so N has a prime factor q.
q is one of the pi, so q divides
  p1·p2·...·pk.
q also divides N, so q divides
  N − p1·...·pk = 1.
No prime divides 1. Contradiction. ∎
```

> [!warning] A common misreading
> The proof does **not** say N itself is prime. 2·3·5·7·11·13 + 1 = 30031 = 59 × 509. It says N has a prime factor missing from the list, which is all the contradiction needs.

### Contradiction or contrapositive?

When proving p → q by contradiction, you assume p ∧ ¬q and hunt for any impossibility. A contrapositive proof assumes ¬q and must reach exactly ¬p. If the derivation of ¬p uses only ¬q and background facts, without relying on the additional assumption p, it can be restated as a direct contrapositive proof. Otherwise it remains a contradiction argument.

Contradiction shines when the claim is a negative ("there is no...", "is not rational", "cannot be decided"). In computer science, the proof that the halting problem is undecidable is a proof by contradiction, and contradiction is also useful in many lower-bound arguments.

## Proof by cases

If every possibility falls into one of several cases, prove the claim in each case separately. This is the valid argument p ∨ q, p → r, q → r ⊢ r from the first lesson.

> [!example] Claim: no sum of two squares leaves remainder 3 when divided by 4
> First, squares mod 4. Every integer n is even or odd.
>
> - Case n = 2k: n² = 4k², remainder 0.
> - Case n = 2k + 1: n² = 4k² + 4k + 1, remainder 1.
>
> So any square leaves remainder 0 or 1. A sum a² + b² leaves 0 + 0, 0 + 1 or 1 + 1, i.e. 0, 1 or 2. Never 3. ∎

So 7, 11, 15, 19, ... can never be written as a sum of two squares. A bounded search over many target integers would not prove the universal claim. For one fixed nonnegative target, exhaustive search over bounded candidate squares can prove that target has no representation; the case split handles all targets at once.

The cases must be **exhaustive**. Forgetting a case (zero, negatives, the empty list) is the proof equivalent of a missing branch in code.

## If and only if

To prove p ↔ q, prove both directions: p → q **and** q → p. They often need different techniques.

```
Claim: n is even ↔ n² is even.

(→) n = 2k, so n² = 2(2k²): even.
(←) proved above by contrapositive.
                                  ∎
```

A common slip is proving one direction twice, once forwards and once by its contrapositive, which proves only one implication.

## Existence proofs and counterexamples

To prove ∃x P(x), the most convincing approach is **constructive**: exhibit a specific x and check it.

Sometimes you can prove existence without saying which object works. A famous **non-constructive** proof:

```
Claim: there exist irrational a, b
       with a^b rational.

Let x = √2^√2. Either x is rational
or it is not.
- If rational: take a = b = √2.
- If irrational: take a = x, b = √2:
  a^b = √2^(√2·√2) = √2² = 2.
Either way such a, b exist.       ∎
```

The proof is valid, yet it doesn't tell you which case holds. (x is in fact irrational, by the Gelfond–Schneider theorem, but the proof doesn't need that.)

To **disprove** ∀x P(x), a single **counterexample** is enough, as n = 40 is for Euler's polynomial. Checking finitely many examples does not prove a universal claim over an infinite domain. Exhaustively checking every case in a known finite domain can prove it; a counterexample disproves either kind of universal claim.

## How proofs go wrong

| Mistake | What happens |
|---|---|
| Incomplete proof by examples | Leaves unchecked cases unjustified |
| Proving the converse | Shows q → p, not p → q |
| Assuming the goal | Circular reasoning |
| Hidden division by 0 | Any "result" follows |
| Missing cases | Gap where the claim may fail |

The classic fake proof that 2 = 1 hides a division by zero:

```
Let a = b = 1.
a²         = ab
a² − b²    = ab − b²
(a+b)(a−b) = b(a−b)
a + b      = b      <- divided by a−b
2b         = b
2          = 1
```

Since a = b, the step that cancels (a − b) divides by zero. Every line before it is true; the line after is not.

> [!tip] A template that avoids most errors
> 1. State the claim precisely, with quantifiers.
> 2. Say which technique you are using.
> 3. Write down the assumptions, expanded using definitions.
> 4. Write down the goal, expanded the same way.
> 5. Bridge the gap, justifying each step.
> 6. Say clearly where the proof ends.

## Key takeaways
- A proof covers every case under its assumptions. Partial sampling gives evidence; exhaustive finite checking can prove a finite-domain claim. One counterexample refutes a universal claim.
- Unpack definitions (even = 2k, a ∣ b means b = ak) before doing anything clever.
- Direct: assume p, derive q. Contrapositive: assume ¬q, derive ¬p. Contradiction: assume ¬S, derive something impossible.
- Case splits must be exhaustive; ↔ needs both directions.
- Existence can be shown constructively (give the object) or non-constructively.
- Watch for circular reasoning, proving the converse and hidden division by zero.

## Further reading
- [Mathematical proof — Wikipedia](https://en.wikipedia.org/wiki/Mathematical_proof)
- [Proof by contradiction — Wikipedia](https://en.wikipedia.org/wiki/Proof_by_contradiction)
- [Contraposition — Wikipedia](https://en.wikipedia.org/wiki/Contraposition)
- [Euclid's theorem — Wikipedia](https://en.wikipedia.org/wiki/Euclid%27s_theorem)
- [Square root of 2 — Wikipedia](https://en.wikipedia.org/wiki/Square_root_of_2)
- [Mathematics for Computer Science — MIT OpenCourseWare](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/)
