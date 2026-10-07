---
id: prob-expectation
title: Random variables, expectation and linearity
level: intermediate
minutes: 14
summary: Random variables, expected value and variance, and linearity of expectation with indicator variables, the trick behind most average-case analyses in algorithms.
---

Average-case analysis asks questions like: how many comparisons does randomised quicksort make on average? How many swaps does insertion sort do on a random input? How many servers sit idle if jobs are assigned at random?

Each answer is an **expected value**, and nearly all of them are found with one remarkably powerful tool: **linearity of expectation**. This lesson builds up to it.

## Random variables

A **random variable** is a function that assigns a number to each outcome of an experiment. Despite the name, it is neither random nor a variable: it is a rule.

- Roll two dice; X = their sum. X maps (3, 5) to 8.
- Hash n keys into a table; Y = the number of collisions.
- Run quicksort on a random permutation; C = the number of comparisons.

The **distribution** (or probability mass function, PMF) of a discrete random variable lists P(X = x) for each value x.

## Expected value

For a discrete variable with finite E[|X|], the **expectation** E[X] is the probability-weighted average of its values:

```
E[X] = Σ x × P(X = x)
```

For one fair die:

```
E[X] = (1+2+3+4+5+6) / 6 = 21/6 = 3.5
```

The expected value need not be a possible outcome: you never roll 3.5. For independent, identically distributed repetitions with finite absolute expectation, sample averages converge to it by the law of large numbers. Some distributions have no finite expectation.

### Waiting for success: the geometric case

A request succeeds with the same probability 0 < p ≤ 1 on each independent attempt. How many attempts does it take on average? The number of attempts T is **geometric**, and:

```
E[T] = 1 / p
```

With p = 0.2, you expect 5 attempts. A neat derivation: with probability p you finish after 1 attempt; otherwise you have used 1 attempt and are back where you started. So E[T] = 1 + (1 − p) E[T], which solves to 1/p.

## Variance

For a variable with finite second moment, the mean says where values centre; **variance** says how spread out they are:

```
Var(X) = E[(X − E[X])²]
       = E[X²] − (E[X])²
SD(X)  = √Var(X)
```

For a die, E[X²] = (1 + 4 + 9 + 16 + 25 + 36) / 6 = 91/6, so Var(X) = 91/6 − 3.5² = 91/6 − 49/4 = 35/12 ≈ 2.92, and the standard deviation is about 1.71.

Two systems with the same mean latency can feel completely different if one has much higher variance. Engineers care about the spread as much as the centre (lesson 6 returns to this with percentiles).

## Linearity of expectation

For random variables X and Y with finite absolute expectations, and constants a and b:

```
E[X + Y]  = E[X] + E[Y]
E[aX + b] = a E[X] + b
```

The crucial point: **this holds even when X and Y are dependent.** No independence assumption is needed. That is what makes it so powerful: you can break a complicated count into simple pieces, find each piece's expectation separately, and add, without ever working out how the pieces interact.

> [!warning] What does NOT hold in general
> - For finite-second-moment variables, E[XY] = E[X] E[Y] holds exactly when covariance is zero. Independence is sufficient but not necessary.
> - Var(X + Y) = Var(X) + Var(Y) + 2 Cov(X,Y), so uncorrelatedness suffices for variances to add.
> - E[f(X)] = f(E[X]) does not hold in general for non-linear f, though it can hold in particular cases. For example E[X²] ≥ (E[X])², which is why variance is never negative.

## Indicator variables

An **indicator** Iₐ is 1 if event A happens and 0 otherwise. Its expectation is just a probability:

```
E[Iₐ] = 1 × P(A) + 0 × P(not A) = P(A)
```

The recipe for "expected number of things that happen" is:

1. Write the count as a sum of indicators, one per thing.
2. Find each indicator's probability.
3. Add them up, by linearity.

### Example: fixed points of a random permutation

n ≥ 1 people check their hats; the hats are handed back in a uniformly random order. How many people expect to get their own hat?

Let Iᵢ = 1 if person i gets their own hat. Each person's hat is equally likely to be any of n, so P(Iᵢ = 1) = 1/n. Then:

```
E[fixed points] = Σ E[Iᵢ]
                = n × (1/n) = 1
```

The answer is 1 for every positive n, whether 3 people or 3 million. For n ≥ 2 the indicators are dependent (if n − 1 people have their own hats, the last must too), but linearity does not care.

### Example: idle servers

A load balancer assigns n jobs to n servers (n ≥ 1), each job independently to a uniformly random server. How many servers get no job?

Let Iⱼ = 1 if server j is idle. Each job misses server j with probability 1 − 1/n, so P(Iⱼ = 1) = (1 − 1/n)ⁿ. Hence:

```
E[idle] = n (1 − 1/n)ⁿ ≈ n / e
        ≈ 0.368 n
```

With 100 jobs and 100 servers, the expected number of idle servers is about 36.6; other servers may receive one or several jobs. Random assignment is far from balanced, which motivates the "power of two choices" technique: in the sequential model with n unit jobs, n initially empty servers, independent uniform candidate choices and current load information, picking the less loaded of two candidates dramatically reduces the maximum load with high probability as n grows. Real scheduling systems need their own workload and measurement assumptions.

### Example: inversions and insertion sort

An **inversion** in an array is a pair of positions i < j with a[i] > a[j]. The adjacent-swap version of insertion sort performs exactly one swap per inversion; the usual shifting version instead performs one rightward shift per inversion. For a uniformly random permutation of distinct values, each of the C(n, 2) pairs is inverted with probability 1/2, so:

```
E[inversions] = C(n,2) / 2
              = n(n − 1) / 4
```

For n = 100 that is 2,475 swaps on average: Θ(n²) even in the average case, only half the worst case.

### Example: how often does the running maximum change?

```python
def scan(a):
    best = float("-inf")
    updates = 0
    for x in a:
        if x > best:   # how often true?
            best = x
            updates += 1
    return updates
```

For a uniformly random permutation of distinct finite numbers, the i-th element is the largest of the first i with probability 1/i (each of the first i is equally likely to be the biggest). So:

```
E[updates] = 1 + 1/2 + 1/3 + ... + 1/n
           = Hₙ ≈ ln n + 0.577
```

For n = 1,000 that is about 7.5 updates. The **harmonic number** Hₙ turns up all over algorithm analysis.

### Example: coupon collector

You independently choose a shard uniformly from n ≥ 1 shards on each request, with replacement, until every shard has been hit at least once. When you have seen k shards, a new one turns up with probability (n − k)/n, so the wait for it is geometric with mean n/(n − k). By linearity:

```
E[total] = n/n + n/(n−1) + ... + n/1
         = n × Hₙ ≈ n ln n
```

For 50 shards, about 225 requests, not 50. This also tells you how long random testing takes to cover every case, or how many random probes find every node.

## Checking by simulation

```python
import random

def fixed_points(n):
    p = list(range(n))
    random.shuffle(p)
    return sum(p[i] == i for i in range(n))

t = 100_000
print(sum(fixed_points(50)
          for _ in range(t)) / t)  # ~1.0
```

## Markov's inequality: a free tail bound

Expectation alone gives a crude but guaranteed bound. For a non-negative X and any a > 0:

```
P(X ≥ a) ≤ E[X] / a
```

If mean request latency is 20 ms, at most 20% of requests can take 100 ms or more. The true tail can be smaller or attain this bound. For a useful finite bound, Markov needs a nonnegative variable and a known finite mean. It is used to turn expected running time into a "with probability at least 1/2" statement. Chebyshev's inequality, P(|X − μ| ≥ kσ) ≤ 1/k² for k > 0 and finite σ > 0, bounds deviations using the variance. It need not improve every Markov bound at every threshold.

## Pitfall: the mean of a ratio

The fact that E[f(X)] need not equal f(E[X]) matters in practice. Each download independently selects a speed of 10 MB/s or 90 MB/s with equal probability and keeps that speed for the entire transfer. The average speed is 50 MB/s, so you might predict a 100 MB download takes 2 s. But the expected time is:

```
0.5 × 100/10 + 0.5 × 100/90
= 5 + 0.556 ≈ 5.6 s
```

The slower transfers contribute more to the mean duration. This model differs from a single transfer whose speed fluctuates rapidly with equal time spent at each rate. When you average rates, decide whether you mean per unit time or per unit of work.

## Key takeaways
- A random variable assigns a number to each outcome; for a discrete integrable variable E[X] = Σ x P(X = x), and iid sample averages converge to it.
- Var(X) = E[X²] − E[X]² measures spread; finite variances add over pairwise uncorrelated variables; independence is sufficient.
- Linearity, E[X + Y] = E[X] + E[Y], holds even for dependent variables.
- Count with indicators: E[number of events] = sum of their probabilities.
- Classic results: expected fixed points 1; idle bins ≈ n/e; inversions n(n − 1)/4; max updates Hₙ; coupon collector n Hₙ; geometric wait 1/p.
- Markov's inequality gives a tail bound from the mean alone; never assume E[f(X)] = f(E[X]).

## Further reading
- [Expected value — Wikipedia](https://en.wikipedia.org/wiki/Expected_value)
- [Indicator function — Wikipedia](https://en.wikipedia.org/wiki/Indicator_function)
- [Coupon collector's problem — Wikipedia](https://en.wikipedia.org/wiki/Coupon_collector%27s_problem)
- [Markov's inequality — Wikipedia](https://en.wikipedia.org/wiki/Markov%27s_inequality)
- [Mathematics for Computer Science (MIT OCW 6.042J)](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-fall-2010/)

- [Balanced Allocations — Azar, Broder, Karlin and Upfal](https://www.cs.tau.ac.il/~azar/box.pdf)
