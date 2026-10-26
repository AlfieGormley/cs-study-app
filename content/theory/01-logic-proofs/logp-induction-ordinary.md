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

> [!analogy] Real-world analogy: A row of dominoes
> Push the first domino and ensure each falling domino knocks over its successor.
>
> **How it maps:** The initial push is the base case; the guaranteed transfer to the next domino is the inductive step. Both are needed to reach any chosen later position.
>
> **Where it stops:** This is a picture of a logical implication chain, not a claim that a physical infinite row can finish falling in finite time.

## Weak (ordinary) induction

To prove P(n) for every integer n at least b:

1. **Base case**: prove P(b).
2. **Inductive step**: for an arbitrary integer n at least b, **assume P(n)** (the **inductive hypothesis**, IH) and prove P(n plus 1).

The base supplies the first true case. The step extends that truth to any specified later integer by finitely many applications.

The inductive step is a direct proof of an implication. You do not assume P(n) is true for all n; you assume it for one arbitrary n and show the next case follows.

### Example: the sum 1 plus 2 plus ... plus n

The claim, for all integers n at least 1, is the formula for adding up the first n whole numbers:

```formula essential
1 + 2 + ... + n = n(n + 1) / 2
where
n: how many whole numbers are being added, n ≥ 1
...: and so on: every whole number between 2 and n
In words: the sum of the first positive integers is half the product of the last integer and its successor.
```

**Base case**, n equals 1: the left-hand side is 1, and the right-hand side is 1 times 2 / 2 equals 1. ✓

**Step**: assume the formula holds for n (the IH). Add the next number, n plus 1, to both sides:

```formula essential
1 + ... + n + (n + 1)
  = n(n + 1) / 2 + (n + 1)
  = (n + 1) × (n + 2) / 2
where
n: an arbitrary whole number at least 1, for which the formula is assumed (the inductive hypothesis)
...: every whole number in between
In words: use the known sum for the current size, add the next integer, then factor to obtain the same claimed form for the next size.
```

That is the formula for n plus 1, so the claim holds for every integer n at least 1. ∎ (The symbol ∎ marks the end of a proof, and ✓ marks a checked step.)

This is why a nested loop where the inner loop runs i times, for i equals 1 to n, does half the product of n and its successor iterations, which grows like n squared: in Big-Theta notation, Θ(n squared).


## Key takeaways
- Induction needs a true starting case and a step for every permitted index.
- The inductive hypothesis is an assumption for an arbitrary current index, used to establish the next case.

## Further reading
- [MIT Mathematics for Computer Science](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/mit6_042js15_textbook.pdf)
- [Mathematical induction — Wikipedia](https://en.wikipedia.org/wiki/Mathematical_induction)
