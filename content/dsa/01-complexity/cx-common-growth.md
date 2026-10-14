---
id: cx-common-growth
sourceLesson: cx-growth-rates
title: Comparing growth rates
level: basic
minutes: 5
summary: Compare logarithmic, linear, quadratic and exponential operation counts.
---

## Growth rates

The function that describes how the operation count grows is the algorithm's **growth rate**. Before comparing them, two pieces of notation need decoding: the logarithm and the power.

A **logarithm** answers "how many times do I multiply 2 by itself to reach n?", or equivalently "how many times can I halve n before I get down to 1?". It is the reverse of raising 2 to a power:

```formula
2^10 = 1024
log_2(1024) = 10
log_2(2^k) = k
where
2^k: 2 raised to the power k: k copies of 2 multiplied together, so 2^3 = 2 × 2 × 2 = 8
log_2(n): the base-2 logarithm of n: the power you raise 2 to in order to get n; it grows very slowly (log_2 of a million is about 20)
k: any number used as a power
n: here, any positive number
In words: the base-2 logarithm undoes "2 to the power": since ten 2s multiplied together make 1,024, the base-2 log of 1,024 is 10.
```

Logarithms appear whenever an algorithm repeatedly halves its problem, as binary search does. In this module "log n" means log_2(n) unless another base is stated; later lessons show why the base rarely matters.

Here are the common growth rates side by side:

```formula
f(n) = n × log_2(n)
f(1000) ≈ 1000 × 10 = 10^4
f(n) = n^2 = n × n
f(n) = 2^n
where
f(n): the number of operations an algorithm with this growth rate does on an input of n items
n: the input size, a whole number of items
log_2(n): the base-2 logarithm of n: the power you raise 2 to in order to get n (log_2(1000) ≈ 9.97)
n^2: n squared, n multiplied by itself
2^n: n copies of 2 multiplied together
10^4: ten to the power 4, which is 10,000
≈: approximately equal to (rounded)
In words: each row of the table below is one choice of f; the table shows how many operations each one needs at three input sizes.
```

Values are rounded and logs are base 2:

| f(n) | n = 10 | n = 1,000 | n = 10^6 |
|---|---|---|---|
| log n | 3 | 10 | 20 |
| n | 10 | 1,000 | 10^6 |
| n log n | 33 | 10^4 | 2 x 10^7 |
| n^2 | 100 | 10^6 | 10^12 |
| 2^n | 1,024 | 10^301 | absurd |

Two things jump out.

First, **for small n, nothing matters much.** At n = 10, even 2^n is only about a thousand steps (1,024). This is why a naive algorithm often works fine in testing.

Second, **for large n, the growth rate is everything.** Suppose a machine does about 10^8 simple operations per second (an illustrative assumed rate, not a general hardware benchmark). Turning an operation count into a time is a division:

```formula
t = W / r
t = 10^12 / 10^8 = 10^4 s
t = 10^4 s / 3600 ≈ 2.8 h
where
t: the running time, in seconds (s)
W: the number of operations the algorithm does; here n^2 = 10^12 for n = 10^6 items
r: the machine's speed, assumed to be 10^8 (100 million) simple operations per second
n: the input size, here a million items
s: seconds
h: hours; 1 h = 3,600 s
≈: approximately equal to (rounded)
In words: a trillion operations at a hundred million per second takes ten thousand seconds, nearly three hours.
```

The same division for the other rows gives, at n = 10^6:

| Growth | Operations | Time |
|---|---|---|
| n | 10^6 | 0.01 s |
| n log n | 2 x 10^7 | 0.2 s |
| n^2 | 10^12 | ~2.8 hours |

The quadratic algorithm is not "a bit slower". It is the difference between instant and unusable.

> [!example] The production surprise
> A team writes the pairwise `has_dup` check for a feature that validates uploaded CSV files. In testing, files have 200 rows: 19,900 comparisons, unnoticeable. A customer uploads 2 million rows: about 2 x 10^12 comparisons. The request times out, retries, and takes the worker pool with it. Nothing was "wrong" with the code except its growth rate.

## Key takeaways
- Repeated halving produces logarithmic growth.
- Large inputs separate linear, linearithmic, quadratic and exponential work.
- The example timings use an illustrative operation rate; actual runtime requires measurement.

## Further reading
- [Analysis of algorithms — Wikipedia](https://en.wikipedia.org/wiki/Analysis_of_algorithms)
- [Time complexity — Wikipedia](https://en.wikipedia.org/wiki/Time_complexity)
