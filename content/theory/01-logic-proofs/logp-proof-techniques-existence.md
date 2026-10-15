---
id: logp-proof-techniques-existence
title: Existence, counterexamples and faulty proofs
level: intermediate
minutes: 4
sourceLesson: logp-proof-techniques
summary: An existence proof may construct a witness or prove that one of several cases supplies one.
---

## Existence proofs and counterexamples

To prove "there exists an x with property P" (written there exists x P(x)), the most convincing approach is **constructive**: exhibit a specific x and check it.

Sometimes you can prove existence without saying which object works. A famous **non-constructive** proof. **Claim: there exist irrational numbers a and b with a to the power b rational.** Let x equals the square root of 2 to the power the square root of 2. Either x is rational or it is not.

- If x is rational, take a equals b equals the square root of 2: both irrational, and a to the power b equals x is rational.
- If x is irrational, take a equals x and b equals the square root of 2, and compute:

```formula
x = (√(2))^{√(2)}
a^b = ((√(2))^{√(2)})^{√(2)}
    = (√(2))^{√(2) × √(2)}
    = (√(2))^2 = 2
where
√2: the square root of 2, about 1.41421, which is irrational
x: √2 to the power √2, about 1.63
a, b: the proposed pair of numbers, here a = x and b = √2
a^b: a to the power b
√: the non-negative square root
In words: raising (√(2))^{√(2)} to the power √2 multiplies the exponents, giving √2 squared, which is 2, a rational number.
```

Either way such a and b exist. ∎

The proof is valid, yet it doesn't tell you which case holds. (x is in fact irrational, by the Gelfond–Schneider theorem, but the proof doesn't need that.)

To **disprove** a "for all" claim (written for every x P(x)), a single **counterexample** is enough, as n equals 40 is for Euler's polynomial. Checking finitely many examples does not prove a universal claim over an infinite domain. Exhaustively checking every case in a known finite domain can prove it; a counterexample disproves either kind of universal claim.


## How proofs go wrong

| Mistake | What happens |
|---|---|
| Incomplete proof by examples | Leaves unchecked cases unjustified |
| Proving the converse | Shows "if q then p", not "if p then q" |
| Assuming the goal | Circular reasoning |
| Hidden division by 0 | Any "result" follows |
| Missing cases | Gap where the claim may fail |

The classic fake proof that 2 equals 1 hides a division by zero. Start with a equals b equals 1:

```formula
a^2 = a × b
a^2 − b^2 = a × b − b^2
(a + b) × (a − b) = b × (a − b)
a + b = b
2b = b
2 = 1
where
a, b: two numbers, both set to 1
a^2, b^2: a and b squared
In words: every line up to the third is true. The fourth line cancels the factor (a − b) from both sides, which is dividing by a − b = 0, and from there on every line is false.
```

Since a equals b, the step that cancels (a minus b) divides by zero. Every line before it is true; the line after is not.

> [!tip] A template that avoids most errors
> 1. State the claim precisely, with quantifiers.
> 2. Say which technique you are using.
> 3. Write down the assumptions, expanded using definitions.
> 4. Write down the goal, expanded the same way.
> 5. Bridge the gap, justifying each step.
> 6. Say clearly where the proof ends.


## Key takeaways
- An existence proof may construct a witness or prove that one of several cases supplies one.
- One counterexample refutes a universal claim; dividing by zero and assuming the goal invalidate proofs.

## Further reading
- [MIT Mathematics for Computer Science](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/mit6_042js15_textbook.pdf)
- [Square root of 2 — Wikipedia](https://en.wikipedia.org/wiki/Square_root_of_2)
