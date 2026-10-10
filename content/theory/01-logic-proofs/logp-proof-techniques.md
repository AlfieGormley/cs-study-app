---
id: logp-proof-techniques
title: Proof techniques (direct, contrapositive, contradiction)
level: intermediate
minutes: 18
summary: How to prove a claim rather than test it, using direct proof, contrapositive, contradiction and cases, plus existence proofs, counterexamples and the mistakes that make a proof worthless.
---

Tests show that code works on the inputs you tried. A **mathematical proof** shows that a claim holds for *every* input, including the ones nobody thought of. Euler's polynomial is the classic warning:

```formula
E(n) = n^2 + n + 41
E(39) = 1521 + 39 + 41 = 1601
E(40) = 1600 + 40 + 41 = 1681 = 41 × 41
where
E(n): Euler's polynomial evaluated at n
n: a natural number (0, 1, 2, …)
n^2: n multiplied by itself
In words: E(n) is prime for every n from 0 to 39 (1601 is prime), but at n = 40 it is 41 × 41, which is not prime.
```

Forty passing tests, one false claim.

Engineers need proofs more often than they expect: to convince yourself an algorithm is correct, that a lower bound is real, that an optimisation is safe, or that a distributed protocol cannot lose data. This lesson covers the main techniques. Almost every proof you will meet is built from them.

## Start with definitions

Most proof failures start with a vague definition. A proof can only use what a term precisely means. Here are the definitions this lesson relies on, written as equations:

```formula
n = 2 × k
n = 2 × k + 1
b = a × k
r = a / b,   b ≠ 0
where
n: a whole number (an integer) being described
k: some integer, which the definition says exists. The first line says n is even, the second that n is odd
a, b: integers. In the third line "b = a × k for some integer k" is what "a divides b" means, written a ∣ b
∣: "divides": a ∣ b means b is a whole-number multiple of a (3 ∣ 12 because 12 = 3 × 4)
r: a number. The fourth line, with integers a and b, says r is rational (a fraction of whole numbers)
≠: is not equal to
In words: even means "twice some integer", odd means "twice some integer, plus one", a divides b means "b is a times some integer", and rational means "an integer over a non-zero integer".
```

| Term | Definition |
|---|---|
| n is even | n = 2k for some integer k |
| n is odd | n = 2k + 1 for some integer k |
| a ∣ b (a divides b) | b = a·k for some integer k |
| r is rational | r = a/b, integers a, b, b ≠ 0 |
| p is prime | integer p > 1, only positive divisors 1 and p |

(In the table, 2k and a·k mean 2 × k and a × k.) Every integer is either even or odd, and not both. We will use that fact freely.

## Direct proof

To prove an implication "if p then q" (written p → q) directly: **assume p, then derive q** step by step, using definitions and previously proven facts.

**Claim: the sum of two odd integers is even.** Assume m and n are odd. Write each one using the definition of odd, then add them:

```formula
m = 2 × a + 1
n = 2 × b + 1
m + n = (2 × a + 1) + (2 × b + 1)
      = 2 × a + 2 × b + 2
      = 2 × (a + b + 1)
where
m, n: the two odd integers
a, b: integers with m = 2 × a + 1 and n = 2 × b + 1 (they exist because m and n are odd)
In words: the sum is 2 times the integer a + b + 1, which is exactly the definition of even.
```

Since a + b + 1 is an integer, m + n is even. ∎ (The symbol ∎ marks the end of a proof.)

Note what the proof does *not* do: it never picks specific numbers. "3 + 5 = 8 is even" is an example, not a proof. The variables a and b stand for every possible case at once.

A second example, about divisibility, shows the same pattern of unpacking definitions. **Claim: if a divides b and b divides c, then a divides c.** Write both assumptions using the definition of divides, then substitute the first into the second:

```formula
b = a × j
c = b × k
  = (a × j) × k
  = a × (j × k)
where
a, b, c: integers, with a ∣ b and b ∣ c assumed
∣: divides: x ∣ y means y = x × (some integer)
j: the integer with b = a × j (it exists because a ∣ b)
k: the integer with c = b × k (it exists because b ∣ c)
In words: c is a times the integer j × k, so by definition a divides c. For example 2 ∣ 6 and 6 ∣ 18 give 18 = 2 × 9.
```

Since j·k is an integer, a ∣ c. ∎

The recipe: write down what you are given, using definitions. Write down what you need to reach, using definitions. Then close the gap with algebra.

## Proof by contrapositive

Recall from the first lesson that an implication and its contrapositive are logically equivalent:

```formula
p → q ≡ ¬q → ¬p
where
p, q: propositions (statements that are true or false)
→: implies: "if ... then ...", false only when the left side is true and the right side false
¬: NOT: ¬q is true exactly when q is false
≡: is logically equivalent to: true in exactly the same situations
In words: "if p then q" says the same as "if not q then not p", so proving either one proves the other.
```

So instead of proving p → q, you may prove ¬q → ¬p directly. This helps when ¬q gives you something concrete to work with and p does not.

**Claim: if n² (n squared) is even, then n is even.** A direct attempt starts with "n² is twice some integer" and needs a square root, which goes nowhere. The contrapositive is: if n is **odd**, then n² is **odd**. So write n using the definition of odd and square it:

```formula
n = 2 × k + 1
n^2 = (2 × k + 1)^2
    = 4 × k^2 + 4 × k + 1
    = 2 × (2 × k^2 + 2 × k) + 1
where
n: an odd integer
k: the integer with n = 2 × k + 1
n^2: n multiplied by itself (n squared)
In words: n² is 2 times an integer, plus 1, so it is odd. With n = 7 (k = 3): 49 = 2 × 24 + 1.
```

So n odd forces n² odd, which proves the claim. ∎

Another one, where the contrapositive turns an awkward "or" into a clean "and". **Claim: if two numbers add up to at least 100, at least one of them is at least 50.** In symbols, with the contrapositive below it:

```formula
x + y ≥ 100  →  x ≥ 50 or y ≥ 50
x < 50 and y < 50  →  x + y < 100
x + y < 50 + 50 = 100
where
→: implies: "if the left side holds, then the right side holds"
x, y: real numbers
≥: is greater than or equal to
<: is less than
In words: the first line is the claim and the second its contrapositive. The third line proves the contrapositive: two numbers that are each under 50 add up to less than 100. So if the sum reaches 100, at least one of them must be 50 or more.
```

This is the pigeonhole principle in miniature. The same reasoning appears in capacity planning: if two shards each hold under half the keys, they cannot together hold them all.

## Proof by contradiction

To prove a statement S: **assume ¬S (not S) and derive something impossible**, such as a statement and its negation. Since a true assumption cannot lead to a false conclusion, ¬S must be false, so S is true.

The two classic examples are over 2,000 years old.

### √2 is irrational

Suppose the square root of 2 is rational. Then it is a fraction a/b of integers with b ≠ 0, and we may take the fraction in lowest terms (a and b share no factor, as any fraction can be reduced). Square both sides and rearrange:

```formula
√2 = a / b
2 = a^2 / b^2
a^2 = 2 × b^2
where
√2: the square root of 2, the positive number whose square is 2 (about 1.41421)
a, b: integers with no common factor, b ≠ 0, assumed to satisfy √2 = a / b
a^2, b^2: a and b squared
≠: is not equal to
In words: if √2 were a fraction a/b, then a² would be exactly twice b², so a² would be even.
```

So a² is even, which means a is even (that is the contrapositive result above). Write a = 2k and substitute:

```formula
(2 × k)^2 = 2 × b^2
4 × k^2 = 2 × b^2
b^2 = 2 × k^2
where
k: the integer with a = 2 × k
b: the denominator from before
In words: b² is twice an integer, so b² is even, and so b is even too.
```

Now a and b are both even, so a/b is not in lowest terms. Contradiction. ∎

The proof uses the earlier contrapositive result as a **lemma**. Building proofs from smaller proven pieces is like building programs from tested functions.

### There are infinitely many primes (Euclid)

Suppose there are only finitely many primes, and list them all as p₁, p₂, …, pₖ. Build a new number N from them:

```formula
N = p_1 × p_2 × ... × p_k + 1
N − p_1 × p_2 × ... × p_k = 1
where
N: the product of every listed prime, plus 1
p_1, p_2, ..., p_k: the supposedly complete list of primes
k: how many primes are on the list
...: and so on, through every prime on the list
In words: N is one more than the product of all the primes, so subtracting that product from N leaves exactly 1.
```

N > 1, so N has a prime factor q. Since the list is supposed to be complete, q is one of the pᵢ, so q divides the product p₁·p₂·…·pₖ. q also divides N, so q divides their difference, which is 1. No prime divides 1. Contradiction. ∎

> [!warning] A common misreading
> The proof does **not** say N itself is prime. 2·3·5·7·11·13 + 1 = 30031 = 59 × 509. It says N has a prime factor missing from the list, which is all the contradiction needs.

### Contradiction or contrapositive?

When proving p → q by contradiction, you assume "p and not q" (written p ∧ ¬q, where ∧ is AND) and hunt for any impossibility. A contrapositive proof assumes ¬q and must reach exactly ¬p. If the derivation of ¬p uses only ¬q and background facts, without relying on the additional assumption p, it can be restated as a direct contrapositive proof. Otherwise it remains a contradiction argument.

Contradiction shines when the claim is a negative ("there is no...", "is not rational", "cannot be decided"). In computer science, the proof that the halting problem is undecidable is a proof by contradiction, and contradiction is also useful in many lower-bound arguments.

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
n = 2 × k:      n^2 = 4 × k^2
n = 2 × k + 1:  n^2 = 4 × (k^2 + k) + 1
where
n: any integer
k: the integer from the definition of even (first line) or odd (second line)
n^2: n squared
In words: an even number's square is a multiple of 4 (remainder 0), and an odd number's square is a multiple of 4 plus 1 (remainder 1).
```

So any square leaves remainder 0 or 1. A sum a² + b² of two squares leaves 0 + 0, 0 + 1 or 1 + 1, that is 0, 1 or 2. Never 3. ∎

So 7, 11, 15, 19, ... can never be written as a sum of two squares. A bounded search over many target integers would not prove the universal claim. For one fixed nonnegative target, exhaustive search over bounded candidate squares can prove that target has no representation; the case split handles all targets at once.

The cases must be **exhaustive**. Forgetting a case (zero, negatives, the empty list) is the proof equivalent of a missing branch in code.

## If and only if

To prove "p if and only if q" (written p ↔ q), prove both directions: p → q **and** q → p. They often need different techniques.

**Claim: n is even if and only if n² is even.** Forwards (→): if n = 2k, then n² is twice an integer:

```formula
n^2 = (2 × k)^2 = 4 × k^2 = 2 × (2 × k^2)
where
n: an even integer, n = 2 × k
k: an integer
n^2: n squared
In words: the square of an even number is 2 times an integer, so it is even.
```

Backwards (←): if n² is even then n is even, which we proved above by contrapositive. Both directions hold. ∎

A common slip is proving one direction twice, once forwards and once by its contrapositive, which proves only one implication.

## Existence proofs and counterexamples

To prove "there exists an x with property P" (written ∃x P(x)), the most convincing approach is **constructive**: exhibit a specific x and check it.

Sometimes you can prove existence without saying which object works. A famous **non-constructive** proof. **Claim: there exist irrational numbers a and b with aᵇ rational.** Let x = √2 raised to the power √2. Either x is rational or it is not.

- If x is rational, take a = b = √2: both irrational, and aᵇ = x is rational.
- If x is irrational, take a = x and b = √2, and compute:

```formula
x = √2^√2
a^b = (√2^√2)^√2
    = √2^(√2 × √2)
    = √2^2 = 2
where
√2: the square root of 2, about 1.41421, which is irrational
x: √2 raised to the power √2, about 1.63
a, b: the candidate pair, here a = x and b = √2
a^b: a raised to the power b
In words: raising √2^√2 to the power √2 multiplies the exponents, giving √2 squared, which is 2, a rational number.
```

Either way such a and b exist. ∎

The proof is valid, yet it doesn't tell you which case holds. (x is in fact irrational, by the Gelfond–Schneider theorem, but the proof doesn't need that.)

To **disprove** a "for all" claim (written ∀x P(x)), a single **counterexample** is enough, as n = 40 is for Euler's polynomial. Checking finitely many examples does not prove a universal claim over an infinite domain. Exhaustively checking every case in a known finite domain can prove it; a counterexample disproves either kind of universal claim.

## How proofs go wrong

| Mistake | What happens |
|---|---|
| Incomplete proof by examples | Leaves unchecked cases unjustified |
| Proving the converse | Shows "if q then p", not "if p then q" |
| Assuming the goal | Circular reasoning |
| Hidden division by 0 | Any "result" follows |
| Missing cases | Gap where the claim may fail |

The classic fake proof that 2 = 1 hides a division by zero. Start with a = b = 1:

```formula
a^2 = a × b
a^2 − b^2 = a × b − b^2
(a + b) × (a − b) = b × (a − b)
a + b = b
2 × b = b
2 = 1
where
a, b: two numbers, both set to 1
a^2, b^2: a and b squared
In words: every line up to the third is true. The fourth line cancels the factor (a − b) from both sides, which is dividing by a − b = 0, and from there on every line is false.
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
- Case splits must be exhaustive; "if and only if" needs both directions.
- Existence can be shown constructively (give the object) or non-constructively.
- Watch for circular reasoning, proving the converse and hidden division by zero.

## Further reading
- [Mathematical proof — Wikipedia](https://en.wikipedia.org/wiki/Mathematical_proof)
- [Proof by contradiction — Wikipedia](https://en.wikipedia.org/wiki/Proof_by_contradiction)
- [Contraposition — Wikipedia](https://en.wikipedia.org/wiki/Contraposition)
- [Euclid's theorem — Wikipedia](https://en.wikipedia.org/wiki/Euclid%27s_theorem)
- [Square root of 2 — Wikipedia](https://en.wikipedia.org/wiki/Square_root_of_2)
- [Mathematics for Computer Science — MIT OpenCourseWare](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/)
