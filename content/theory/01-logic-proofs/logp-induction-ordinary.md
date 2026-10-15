---
id: logp-induction-ordinary
title: Ordinary induction and the sum formula
level: intermediate
minutes: 4
sourceLesson: logp-induction
summary: Induction needs a true starting case and a step for every permitted index.
---


Many claims in computer science are about *every* size of input: every n, every list, every tree. You cannot check infinitely many cases, and the techniques from the last lesson often don't get a grip on "every n".

**Mathematical induction** is the tool for this. It turns an infinite claim into two finite pieces of work. It is also exactly how you should think about recursive code: if the base case is right, and each call is right assuming the smaller calls are right, the function is right.

## The domino picture

Imagine an infinite row of dominoes. To know they all fall, you need two facts:

1. The first domino falls.
2. Whenever a domino falls, it knocks over the next one.

Neither fact alone is enough. With both, every domino falls. In the sketch below, P(n) is the claim about the number n (domino n falls), and each arrow means "leads to":

```
P(0)  ->  P(1)  ->  P(2)  ->  P(3) ...
 ^base     \_ step: P(n) -> P(n+1) _/
```


## Weak (ordinary) induction

To prove P(n) for every integer n at least b:

1. **Base case**: prove P(b).
2. **Inductive step**: for an arbitrary integer n at least b, **assume P(n)** (the **inductive hypothesis**, IH) and prove P(n plus 1).

Written as a single formula, the principle of induction says:

```formula
P(b) ∧ ∀n ≥ b (P(n) → P(n + 1))
  → ∀n ≥ b P(n)
where
P(n): the statement being proved about the integer n, which is either true or false for each n
b: the base value, the first n the claim is about (often 0 or 1)
n: an integer at least b
∧: AND: both parts must be proved
∀: "for all"; ∀n ≥ b means "for every integer n from b upwards"
→: implies: "if ... then ..."
≥: is greater than or equal to
In words: if the claim holds at b, and whenever it holds for some n it also holds for n + 1, then it holds for every n from b upwards.
```

The inductive step is a direct proof of an implication. You do not assume P(n) is true for all n; you assume it for one arbitrary n and show the next case follows.

### Example: the sum 1 plus 2 plus ... plus n

The claim, for all integers n at least 1, is the formula for adding up the first n whole numbers:

```formula
1 + 2 + ... + n = n(n + 1) / 2
where
n: how many whole numbers are being added, n ≥ 1
...: and so on: every whole number between 2 and n
In words: the sum of 1 to n is n times n + 1, halved. For n = 4: 1 + 2 + 3 + 4 = 10 = 4 × 5 / 2.
```

**Base case**, n equals 1: the left-hand side is 1, and the right-hand side is 1 times 2 / 2 equals 1. ✓

**Step**: assume the formula holds for n (the IH). Add the next number, n plus 1, to both sides:

```formula
1 + ... + n + (n + 1)
  = n(n + 1) / 2 + (n + 1)
  = (n + 1) × (n / 2 + 1)
  = (n + 1) × (n + 2) / 2
where
n: an arbitrary whole number at least 1, for which the formula is assumed (the inductive hypothesis)
...: every whole number in between
In words: the second line uses the IH to replace 1 + ... + n; taking out the common factor n + 1 then gives exactly the formula with n + 1 in place of n.
```

That is the formula for n plus 1, so the claim holds for every integer n at least 1. ∎ (The symbol ∎ marks the end of a proof, and ✓ marks a checked step.)

This is why a nested loop where the inner loop runs i times, for i equals 1 to n, does half the product of n and its successor iterations, which grows like n squared: in Big-Theta notation, Θ(n squared).


## Key takeaways
- Induction needs a true starting case and a step for every permitted index.
- The inductive hypothesis is an assumption for an arbitrary current index, used to establish the next case.

## Further reading
- [MIT Mathematics for Computer Science](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/mit6_042js15_textbook.pdf)
- [Mathematical induction — Wikipedia](https://en.wikipedia.org/wiki/Mathematical_induction)
