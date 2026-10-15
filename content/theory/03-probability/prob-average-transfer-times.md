---
id: prob-average-transfer-times
title: Average transfer times rather than rates
level: intermediate
minutes: 3
sourceLesson: prob-expectation
summary: Compute the duration in each outcome before averaging.
---

## Pitfall: the mean of a ratio

The fact that the expectation of a function need not equal the function of the expectation matters in practice. Each download independently selects a speed of 10 MB/s or 90 MB/s with equal probability and keeps that speed for the entire transfer. The average speed is 50 MB/s, so you might predict a 100 MB download takes 2 s. But the mean duration is:

```formula
T = D / S
E[T] = 0.5 × (100 MB / (10 MB/s))
  + 0.5 × (100 MB / (90 MB/s))
E[T] = 0.5 × 10 s + 0.5 × (10/9) s
E[T] ≈ (5 + 0.556) s ≈ 5.56 s
D / E[S] = 100 MB / (50 MB/s)
D / E[S] = 2 s
where
T: the download duration, in seconds (s)
D: the fixed download size, 100 megabytes (MB)
S: the speed chosen for an entire transfer, either 10 or 90 megabytes per second (MB/s), each with probability 0.5
E[ ]: expected value, in the units of the quantity averaged
MB: megabyte, one million bytes
s: second, the time unit
≈: approximately equal to, from rounding
Expectations: all displayed expectations are finite; an expectation has the units of the quantity averaged
In words: half the downloads take ten seconds and half take ten-ninths of a second, giving about 5.56 seconds on average; dividing by the mean speed incorrectly predicts two seconds.
```

The slower transfers contribute more to the mean duration. This model differs from a single transfer whose speed fluctuates rapidly with equal time spent at each rate. When you average rates, decide whether you mean per unit time or per unit of work.

## Key takeaways
- Compute the duration in each outcome before averaging.
- Specify whether a speed is sampled per transfer or averaged over time.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
