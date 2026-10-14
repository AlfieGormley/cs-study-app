---
id: cx-hardware-scaling
sourceLesson: cx-growth-rates
title: What faster hardware buys
level: basic
minutes: 3
summary: Translate a hardware speedup into the input size each growth rate can handle.
---

Keep the time budget fixed and ask how much larger the input can become. The growth rate decides how much value a faster machine provides.

## Faster hardware does not save you

It is tempting to think faster hardware fixes a slow algorithm. Here N is the old input limit and N_new the new one, with the same time budget. The table compares growth shapes for a **10-times-faster** machine.

| Growth | Original limit | New limit |
|---|---|---|
| Linear | original | ten times original |
| Quadratic | original | about 3.16 times original |
| Cubic | original | about 2.15 times original |
| Exponential | original | about 3.3 extra items |

Where do these numbers come from? Set the work the new machine can do in the same time equal to 10 times the old work, and solve for the new input size:

```formula
N_new^2 = 10N^2
N_new = √(10) × N ≈ 3.16N
2^{N_new} = 10 × 2^N
N_new = N + log_2(10) ≈ N + 3.3
N_new = 10N
N_new^3 = 10N^3
N_new = 10^{1/3}N ≈ 2.15N
where
N: the largest input the old machine can handle in the time budget
N_new: the largest input the 10-times-faster machine can handle in the same time
√(10): the square root of 10, the number that multiplied by itself gives 10, about 3.16
log_2(10): the base-2 logarithm of 10, the power you raise 2 to in order to get 10, about 3.32
≈: approximately equal to (rounded)
In words: for quadratic work, 10 times the speed buys only √10 ≈ 3.16 times the input; for exponential work, it buys only about 3 more items.
```

For a cubic algorithm the same steps give the cube root of 10, about 2.15. Better algorithms routinely give improvements of thousands or millions of times; hardware gives you a constant factor.

## Key takeaways
- A hardware speedup changes a constant factor in runtime.
- For quadratic work, the input gain follows the square root of the speed gain.
- Exponential search gains only a few extra items from a large constant speedup.

## Further reading
- [Analysis of algorithms — Wikipedia](https://en.wikipedia.org/wiki/Analysis_of_algorithms)
- [Algorithms by Jeff Erickson (free textbook)](https://jeffe.cs.illinois.edu/teaching/algorithms/)
