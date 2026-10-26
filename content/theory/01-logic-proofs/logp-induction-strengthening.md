---
id: logp-induction-strengthening
title: Making the induction hypothesis stronger
level: intermediate
minutes: 3
sourceLesson: logp-induction
summary: A stronger bound can track the slack needed for the next step.
---

## Why a stronger claim can be easier

An inductive hypothesis is a tool for the next step. If it throws away information that the next step needs, a true claim can be difficult to prove directly.

For example, add the reciprocals of the positive squares: one, then a quarter, then a ninth, and so on. Every finite sum stays below two. But “the current sum is below two” tells us no guaranteed amount of space remains. Adding another positive term cannot be justified from that fact alone.

The repair is to track a specific gap: after a given number of terms, the sum is at least the reciprocal of that count below two. This is a stronger claim. It gives the induction step a budget for the next fraction.

## Check the stronger claim

At one term, the sum is one and the required gap below two is one, so the strengthened base holds.

For the next step, the permitted gap gets slightly smaller. The difference between the old and new bounds is the reciprocal of the product of two consecutive positive integers. The next term has the square of the larger integer in its denominator, so it is no bigger than that available difference. It fits, and the new sum retains the promised gap.

The optional calculation records the precise bound and the comparison used in that argument.

```formula reference
S(n) = 1/1^2 + 1/2^2 + ... + 1/n^2
S(n) ≤ 2 − 1/n
1/n − 1/(n + 1) = 1/(n(n + 1))
1/(n + 1)^2 ≤ 1/(n(n + 1))
where
S(n): the sum of the reciprocals of the first n positive integer squares
n: a positive integer, the number of terms already included
...: every intervening reciprocal-square term
≤: is at most
In words: tracking a guaranteed gap below two gives enough room for the next fraction while preserving the smaller gap promised for the next sum.
```

Because the guaranteed gap is positive at every finite stage, the original “below two” claim follows. The strengthened bound need not equal the true sum; it only needs to be strong enough to carry the step.

This is still ordinary induction: the proof uses the immediately preceding case. **Strong induction** instead changes which earlier cases the step may assume. These are different ways of improving a proof.

The same discipline applies to recursive cost claims. Include the cost of the smallest input in the base case, then account for smaller calls and the current work in the step. Omitting leaf work can make an exact cost formula fail before the recursion even begins.

## Key takeaways
- A stronger claim can retain the slack needed for the inductive step.
- Check the stronger base and show the next addition fits the available gap.
- Strengthening the claim and using strong induction are different choices.

## Further reading
- [MIT Mathematics for Computer Science](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/mit6_042js15_textbook.pdf)
