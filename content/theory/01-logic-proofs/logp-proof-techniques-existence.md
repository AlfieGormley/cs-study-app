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

```formula essential
x = (√(2))^{√(2)}
a = x, b = √(2)
a^b = (√(2))^2 = 2
where
√2: the square root of 2, about 1.41421, which is irrational
x: √2 to the power √2, about 1.63
a, b: the proposed pair of numbers, here a = x and b = √2
a^b: a to the power b
√: the non-negative square root
In words: raising (√(2))^{√(2)} to the power √2 multiplies the exponents, giving √2 squared, which is 2, a rational number.
```

Either way such a and b exist. ∎

The proof is valid without deciding which case holds. Positive bases allow the exponent rule used here; the two exponents multiply to two.

To **disprove** a "for all" claim (written for every x P(x)), a single **counterexample** is enough, as one allowed input producing a composite output is for a prime-producing claim. Checking finitely many examples does not prove a universal claim over an infinite domain. Exhaustively checking every case in a known finite domain can prove it; a counterexample disproves either kind of universal claim.


## How proofs go wrong

| Mistake | What happens |
|---|---|
| Incomplete proof by examples | Leaves unchecked cases unjustified |
| Proving the converse | Shows "if q then p", not "if p then q" |
| Assuming the goal | Circular reasoning |
| Hidden division by 0 | Any "result" follows |
| Missing cases | Gap where the claim may fail |

The classic fake proof that two equals one hides a division by zero:

Cancelling a common factor requires that factor to be nonzero. If both original numbers are one, their difference is zero. Multiplying two different values by zero gives equal products, so equality of those products cannot justify cancelling the zero.

The problem is the operation's missing precondition: cancellation is valid only for a nonzero factor.

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
