---
id: prob-records-coupons
title: Find harmonic expectations for records and coverage
level: intermediate
minutes: 3
sourceLesson: prob-expectation
summary: A record at a given position has reciprocal-position probability.
---

## Example: how often does the running maximum change?

```python
def scan(a):
    best = float("-inf")
    updates = 0
    for x in a:
        # Count only new record values.
        if x > best:
            best = x
            updates += 1
    return updates
```

For a uniformly random permutation of distinct finite numbers, the i-th element is the largest of the first i with probability 1/i (each of the first i is equally likely to be the biggest). Adding one indicator per position:

```formula
E[U] = 1 + 1/2 + 1/3 + … + 1/n
E[U] = H_n ≈ ln(n) + 0.577
H_1000 ≈ 6.908 + 0.577 ≈ 7.5
where
U: the number of times the running maximum is updated
n: the positive integer number of distinct finite elements in a uniform random permutation; 1,000 in the last line
E[U]: the expected number of updates
H_n: the n-th **harmonic number**, the sum 1 + 1/2 + … + 1/n
H_1000: the harmonic number for n = 1,000
ln(n): the natural logarithm of n (log to base e ≈ 2.718); ln(1000) ≈ 6.908
0.577: the Euler–Mascheroni constant γ ≈ 0.5772, the limiting gap between H_n and ln(n)
…: and so on, one term per position
≈: approximately equal to
Expectations: all displayed expectations are finite; an expectation has the units of the quantity averaged
In words: the i-th element sets a new record with chance 1/i, so records get rarer as you go and only about 7.5 happen in 1,000 elements.
```

The harmonic number H_n turns up all over algorithm analysis, because it grows like the logarithm of n.

## Example: coupon collector

You independently choose a shard uniformly from n shards (at least one) on each request, with replacement, until every shard has been hit one or more times. At each stage, the chance of a new shard is the fraction still unseen. The wait is geometric with mean equal to the reciprocal of that fraction. By linearity, add the waits:

```formula
E[W] = n/n + n/(n − 1) + … + n/1
E[W] = n × H_n ≈ n × ln(n)
E[W] = 50 × H_50 ≈ 50 × 4.50 ≈ 225
where
W: the total number of requests until every shard has been seen
n: the positive integer number of shards, chosen independently and uniformly with replacement; 50 in the last line
k: the number of distinct shards seen so far (0 up to n − 1)
n/(n − k): the expected wait for a new shard when k have been seen
H_n: the n-th harmonic number, 1 + 1/2 + … + 1/n
H_50: the harmonic number for n = 50, about 4.50
E[W]: the expected total number of requests
ln(n): the natural logarithm of n
…: and so on, one term for each new shard
≈: approximately equal to
Expectations: all displayed expectations are finite; an expectation has the units of the quantity averaged
In words: the last few unseen shards take the longest to hit, so covering all 50 takes about 225 requests, not 50.
```

This also tells you how long random testing takes to cover every case, or how many random probes find every node. The leading logarithmic shortcut leaves out about 0.577 requests per shard. For 50 shards it gives about 196 requests, around 13% below the exact expectation of about 225.

## Key takeaways
- A record at a given position has reciprocal-position probability.
- Coupon collection slows as the unseen set shrinks.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
