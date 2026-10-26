---
id: prob-geometric-mean
title: Understand the expected wait for success
level: intermediate
minutes: 3
sourceLesson: prob-expectation
summary: Independent constant-probability attempts restart after a failure.
---

An expected retry count describes average load, not a deadline. Even when success has a finite expected wait, a particular request can need many more attempts.

## A fresh chance after every failure

Assume attempts are independent and each has the same positive success probability. Count all attempts up to and including the first success. This is the **geometric distribution**.

After a failed attempt, the future process has the same distribution as it had initially. You have spent one attempt, but have made no progress towards a success being “due”. A larger success probability shortens the expected wait; halving it doubles the mean attempt count.

```formula reference
E[T] = 1 / p
where
T: the number of attempts up to and including the first success
E[T]: the expected (long-run average) number of attempts
p: the fixed success probability for an independent attempt, greater than zero and at most one
Expectations: all displayed expectations are finite; an expectation has the units of the quantity averaged
In words: With independent attempts and a constant positive success chance, the mean total attempts through success is the reciprocal of that chance.
```

For a success chance of one in five, the mean is five total attempts. That includes the successful attempt, so failures-only counts are one smaller. A run can still end on its first attempt or continue far beyond five.

## Why the mean is finite

Each extra failure multiplies the probability of still waiting by the same factor below one. The resulting geometric tail has a finite sum, which justifies the finite mean. At success probability one, the first attempt always succeeds; at zero, this proper finite-mean model does not apply.

In a real overloaded service, attempts may share a persistent cause and retries may worsen the overload. The constant independent chance is an assumption to test, not a reason to retry without a limit or delay.

## Key takeaways
- Count the successful attempt when interpreting geometric waiting time.
- A finite expectation does not impose a maximum wait.
- Retry-load estimates depend on constant independent success chances.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
