---
id: logp-induction-strong
title: Strong induction and several starting cases
level: intermediate
minutes: 4
sourceLesson: logp-induction
summary: Strong induction may use every earlier case down to the base.
---

## Strong induction

Sometimes P(n plus 1) depends not on P(n) but on some earlier case. **Strong induction** lets you assume P holds for *every* value from the base up to n.

1. **Base case(s)**: prove P(b), and any others the step can't reach.
2. **Step**: assume P(b), P(b plus 1), ..., P(n) all hold; prove P(n plus 1).

### Example: every integer n at least 2 is a product of primes

**Step**: assume every k with 2 is at most k is at most n is a product of primes, and consider n plus 1. There are two cases.

- If n plus 1 is prime, it is a product of one prime. ✓
- If n plus 1 is composite, split it into two smaller factors, Each factor is covered by the hypothesis, so combining their prime decompositions gives a decomposition of the original. ✓ ∎

A composite integer splits into two integer factors, each at least two and strictly smaller than the original. The hypothesis covers both factors, so combining their prime decompositions covers the original integer.

Weak induction would only let you assume the claim for n, which says nothing directly about those smaller factors. (Base n equals 2: 2 is prime. The case analysis actually covers it, but stating it is good practice.)

### Example: postage with 4p and 5p stamps

Claim: every amount n is at least 12 (in pence, p) can be made with 4p and 5p stamps.

**Bases**: the four amounts 12 to 15.

The starting amounts are 12p from three 4p stamps, 13p from two 4p stamps and one 5p stamp, 14p from one 4p stamp and two 5p stamps, and 15p from three 5p stamps.

**Step**: for n plus 1 is at least 16, the amount four pence lower is at least 12, so by the IH it can be made. Add one 4p stamp:

For any target of at least 16p, subtracting 4p leaves a previously covered amount of at least 12p. Make that amount and add one 4p stamp.

This particular step reaches back four places, so it needs four consecutive base cases. Leave one out and 15 (say) is never covered. Note 11 is impossible, which is why the claim starts at 12.

Strong and weak induction prove exactly the same things: you can always turn strong into weak by making the hypothesis "P holds for all values up to n". Use whichever makes the proof clearer. Both rest on the **well-ordering principle**: every non-empty set of natural numbers has a smallest element. If P failed somewhere there would be a *smallest* failure, and the step shows it cannot be one.


## Key takeaways
- Strong induction may use every earlier case down to the base.
- A step that reaches back several places needs enough initial cases to start every chain.

## Further reading
- [MIT Mathematics for Computer Science](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/mit6_042js15_textbook.pdf)
- [Structural induction — Wikipedia](https://en.wikipedia.org/wiki/Structural_induction)
