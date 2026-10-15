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
- If n plus 1 is composite, split it into two smaller factors, as below. By the IH, a and b are products of primes, so a times b is too. ✓ ∎

```formula
n + 1 = a × b
2 ≤ a ≤ n
2 ≤ b ≤ n
where
n: an integer at least 2; every k from 2 to n is assumed to be a product of primes (the strong inductive hypothesis)
a, b: whole-number factors of n + 1, neither equal to 1 nor to n + 1 itself (they exist because n + 1 is composite)
≤: is less than or equal to
In words: a composite number splits into two factors that are both at least 2 and both smaller than itself, so the hypothesis covers both. For example 12 = 3 × 4.
```

Weak induction would only let you assume the claim for n, which says nothing about a and b. (Base n equals 2: 2 is prime. The case analysis actually covers it, but stating it is good practice.)

### Example: postage with 4p and 5p stamps

Claim: every amount n is at least 12 (in pence, p) can be made with 4p and 5p stamps.

**Bases**: the four amounts 12 to 15.

```formula
12 = 4 + 4 + 4
13 = 4 + 4 + 5
14 = 4 + 5 + 5
15 = 5 + 5 + 5
where
4, 5: the stamp values, in pence (p), the hundredth part of a pound sterling
In words: each of the amounts 12p, 13p, 14p and 15p can be made from 4p and 5p stamps.
```

**Step**: for n plus 1 is at least 16, the amount four pence lower is at least 12, so by the IH it can be made. Add one 4p stamp:

```formula
(n + 1) − 4 ≥ 12   for n + 1 ≥ 16
where
n + 1: the amount being made, in pence, at least 16
≥: is greater than or equal to
In words: taking a 4p stamp off any amount of 16p or more leaves an amount of at least 12p, which the hypothesis already covers. ∎
```

The step reaches back 4 places, so it needs four base cases. Leave one out and 15 (say) is never covered. Note 11 is impossible, which is why the claim starts at 12.

Strong and weak induction prove exactly the same things: you can always turn strong into weak by making the hypothesis "P holds for all values up to n". Use whichever makes the proof clearer. Both rest on the **well-ordering principle**: every non-empty set of natural numbers has a smallest element. If P failed somewhere there would be a *smallest* failure, and the step shows it cannot be one.


## Key takeaways
- Strong induction may use every earlier case down to the base.
- A step that reaches back several places needs enough initial cases to start every chain.

## Further reading
- [MIT Mathematics for Computer Science](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/mit6_042js15_textbook.pdf)
- [Structural induction — Wikipedia](https://en.wikipedia.org/wiki/Structural_induction)
