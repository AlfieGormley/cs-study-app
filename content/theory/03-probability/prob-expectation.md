---
id: prob-expectation
title: Random variables, expectation and linearity
level: intermediate
minutes: 18
summary: Random variables, expected value and variance, and linearity of expectation with indicator variables, the trick behind most average-case analyses in algorithms.
---

Average-case analysis asks questions like: how many comparisons does randomised quicksort make on average? How many swaps does insertion sort do on a random input? How many servers sit idle if jobs are assigned at random?

Each answer is an **expected value**, and nearly all of them are found with one remarkably powerful tool: **linearity of expectation**. This lesson builds up to it.

## Random variables

A **random variable** is a function that assigns a number to each outcome of an experiment. Despite the name, it is neither random nor a variable: it is a rule.

- Roll two dice; X = their sum. X maps (3, 5) to 8.
- Hash n keys into a table; Y = the number of collisions.
- Run quicksort on a random permutation; C = the number of comparisons.

The **probability distribution** (or **probability mass function**, PMF) of a discrete random variable lists, for each value it can take, the probability that it takes that value.

```formula
p_X(x) = P(X = x)
where
X: a discrete random variable, for example the sum of two dice
x: one particular value X might take, for example 8
P(X = x): the probability that X comes out equal to x, from 0 to 1
p_X(x): the probability mass function (PMF) of X evaluated at x; it is the same number, written as a function of x
In words: the PMF is a table giving the chance of every possible value; over all values the chances add up to 1.
```

For the sum of two fair dice, the PMF at 8 is 5/36, because 5 of the 36 ordered pairs sum to 8.

## Expected value

The **expectation** (expected value, or mean) of a random variable is the probability-weighted average of its values: each value counts in proportion to how likely it is. For a discrete variable it is a sum over every value; we need the sum of the absolute values to be finite, so the answer does not depend on the order of adding.

```formula
E[X] = Σ_x x × P(X = x)
where
E[X]: the expected value of X, the long-run average if the experiment were repeated many times
X: a discrete random variable
x: one of the values X can take
Σ_x: sigma, "add up the following term over every value x"
P(X = x): the probability that X equals x
In words: multiply each value by its probability and add the results; likely values pull the average towards themselves.
```

For one fair die, each face has probability 1/6:

```formula
E[X] = (1 + 2 + 3 + 4 + 5 + 6) × 1/6
E[X] = 21/6 = 3.5
where
X: the number shown by one fair six-sided die
E[X]: its expected value
1/6: the probability of each face
In words: the average roll of a fair die is 3.5.
```

The expected value need not be a possible outcome: you never roll 3.5. For independent, identically distributed repetitions with finite absolute expectation, sample averages converge to it by the **law of large numbers**. Some distributions have no finite expectation.

### Waiting for success: the geometric case

A request succeeds with the same probability p (more than 0, at most 1) on each independent attempt. How many attempts does it take on average? The number of attempts T has a **geometric distribution**, and:

```formula
E[T] = 1 / p
E[T] = 1 / 0.2 = 5
where
T: the number of attempts up to and including the first success
E[T]: the expected (long-run average) number of attempts
p: the probability that one attempt succeeds; 0.2 (20%) in the second line
In words: if each try succeeds one time in five, you need five tries on average.
```

A neat derivation: with probability p you finish after 1 attempt; otherwise you have used 1 attempt and are back where you started, because independent attempts have no memory.

```formula
E[T] = 1 + (1 − p) × E[T]
p × E[T] = 1
E[T] = 1 / p
where
E[T]: the expected number of attempts
1: the attempt you always make
p: the chance that attempt succeeds
1 − p: the chance it fails, after which you face the same problem again
In words: one attempt, plus (if it failed) a fresh copy of the whole wait; solving for the expected wait gives 1/p.
```

## Variance

For a variable with a finite **second moment** (finite expected square), the mean says where values centre; **variance** says how spread out they are. It is the average squared distance from the mean, and the **standard deviation** is its square root, which is back in the original units.

```formula
Var(X) = E[(X − μ)^2]
Var(X) = E[X^2] − μ^2
σ = √(Var(X))
where
X: a random variable
μ: mu, the mean of X, the same as E[X]
E[ ]: expected value, the probability-weighted average of whatever is inside the brackets
E[X^2]: the expected value of X squared (X multiplied by itself)
Var(X): the variance of X, in the units of X squared
σ: sigma, the standard deviation of X, in the same units as X
√: the square root
In words: variance is the average squared distance from the mean, which also equals the mean of the square minus the square of the mean; its square root is the standard deviation.
```

For one fair die:

```formula
E[X^2] = (1 + 4 + 9 + 16 + 25 + 36) / 6
E[X^2] = 91/6
Var(X) = 91/6 − 3.5^2 = 91/6 − 49/4
Var(X) = 35/12 ≈ 2.92
σ = √(35/12) ≈ 1.71
where
X: the number shown by one fair die
E[X^2]: the average of the squared face values
3.5: the mean roll, E[X]
Var(X): the variance of the roll
σ: sigma, the standard deviation of the roll
√: the square root
≈: approximately equal to
In words: a die roll typically lands about 1.7 away from its mean of 3.5.
```

Two systems with the same mean latency can feel completely different if one has much higher variance. Engineers care about the spread as much as the centre (lesson 6 returns to this with percentiles).

## Linearity of expectation

For random variables X and Y with finite absolute expectations, and constants a and b:

```formula
E[X + Y] = E[X] + E[Y]
E[a × X + b] = a × E[X] + b
where
X, Y: any two random variables, dependent or not
E[ ]: expected value
a, b: fixed numbers (constants), not random
In words: the average of a sum is the sum of the averages, and scaling or shifting a variable scales or shifts its average the same way.
```

The crucial point: **this holds even when X and Y are dependent.** No independence assumption is needed. That is what makes it so powerful: you can break a complicated count into simple pieces, find each piece's expectation separately, and add, without ever working out how the pieces interact.

For example, the sum of two dice has expectation 3.5 + 3.5 = 7, and twice one die plus 1 has expectation 2 × 3.5 + 1 = 8.

> [!warning] What does NOT hold in general
> Products, sums of variances and non-linear functions do not behave like linearity. The three rules below are the true versions.

```formula
E[X × Y] = E[X] × E[Y]   if Cov(X, Y) = 0
Var(X + Y) = Var(X) + Var(Y)
  + 2 × Cov(X, Y)
E[X^2] ≥ (E[X])^2
where
X, Y: random variables with finite second moments
E[ ]: expected value
Var( ): variance, the average squared distance from the mean
Cov(X, Y): the **covariance** of X and Y, E[X × Y] − E[X] × E[Y]; positive when they tend to move together, 0 when **uncorrelated**
≥: greater than or equal to
In words: the mean of a product splits only when the covariance is zero (independence is enough but not necessary); variances add only when the covariance is zero; and the mean of a square is at least the square of the mean, which is why variance is never negative.
```

More generally, the expectation of a non-linear function of X need not equal that function of the expectation, though it can in particular cases. The pitfall section at the end shows the cost.

## Indicator variables

An **indicator variable** for an event A is 1 if A happens and 0 otherwise. Its expectation is just a probability:

```formula
E[I_A] = 1 × P(A) + 0 × P(¬A)
E[I_A] = P(A)
where
A: an event
I_A: the indicator of A: 1 if A happens, 0 if not
E[I_A]: its expected value
P(A): the probability of A
¬A: "not A", the event that A does not happen (¬ is "not")
In words: the average of a 0-or-1 switch is just the chance it is on.
```

The recipe for "expected number of things that happen" is:

1. Write the count as a sum of indicators, one per thing.
2. Find each indicator's probability.
3. Add them up, by linearity.

### Example: fixed points of a random permutation

At least one person (n of them) checks their hat; the hats are handed back in a uniformly random order. How many people expect to get their own hat? A person who gets their own hat back is a **fixed point** of the shuffle.

Each person's hat is equally likely to be any of the n hats, so each person gets their own with probability 1/n.

```formula
F = I_1 + I_2 + … + I_n
E[F] = Σ_i E[I_i] = n × (1/n) = 1
where
F: the number of people who get their own hat back (fixed points)
n: the number of people, at least 1
I_i: the indicator that person i gets their own hat: 1 if so, 0 if not
I_1, I_2, I_n: the indicators for person 1, person 2 and the last person, n
i: a counter running over the people, 1 to n
E[ ]: expected value
Σ_i: sigma, "add up over every person i"
…: and so on, one indicator per person
1/n: the chance a given person gets their own hat
In words: n people each with a 1-in-n chance gives an expected total of exactly 1.
```

The answer is 1 for every positive n, whether 3 people or 3 million. With two or more people the indicators are dependent (if all but one have their own hats, the last must too), but linearity does not care.

### Example: idle servers

A load balancer assigns n jobs to n servers (at least one of each), each job independently to a uniformly random server. How many servers get no job?

Each job misses a given server with probability 1 − 1/n, and the n jobs choose independently, so the server is idle with probability (1 − 1/n)^n. Add one indicator per server:

```formula
E[Z] = n × (1 − 1/n)^n
E[Z] ≈ n / e ≈ 0.368 × n
E[Z] = 100 × 0.99^100 ≈ 36.6
where
Z: the number of idle servers (servers that receive no job)
E[Z]: the expected (long-run average) number of idle servers
n: the number of jobs and of servers; 100 in the last line
(1 − 1/n)^n: the chance one server is missed by all n jobs
e: Euler's number, about 2.718, the base of natural logarithms; (1 − 1/n)^n gets closer to 1/e as n grows
≈: approximately equal to
In words: about 37% of servers sit idle when jobs are thrown at them uniformly at random.
```

With 100 jobs and 100 servers, the expected number of idle servers is about 36.6; other servers may receive one or several jobs. Random assignment is far from balanced, which motivates the **power of two choices** technique: in the sequential model with n unit jobs, n initially empty servers, independent uniform candidate choices and current load information, picking the less loaded of two candidates dramatically reduces the maximum load with high probability as n grows. Real scheduling systems need their own workload and measurement assumptions.

### Example: inversions and insertion sort

An **inversion** (array inversion) in an array is a pair of positions where the earlier element is bigger than the later one. The adjacent-swap version of insertion sort performs exactly one swap per inversion; the usual shifting version instead performs one rightward shift per inversion. For a uniformly random permutation of distinct values, each pair is equally likely to be in either order, so each is inverted with probability 1/2.

```formula
E[N_inv] = C(n, 2) × 1/2
E[N_inv] = n × (n − 1) / 4
E[N_inv] = 100 × 99 / 4 = 2,475
where
N_inv: the number of inversions, pairs of positions i < j with a[i] > a[j]
n: the length of the array; 100 in the last line
a[i]: the element at position i
C(n, 2): "n choose 2", the number of pairs of positions, n × (n − 1) / 2
E[ ]: expected value
1/2: the chance a given pair is out of order
In words: half of all pairs are out of order on average, so insertion sort does about n²/4 swaps on a random input.
```

For n = 100 that is 2,475 swaps on average. Using **Θ** (big-Theta, "grows exactly as fast as, up to constant factors") with n the array length, that is Θ(n²) even in the average case, only half the worst case.

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

For a uniformly random permutation of distinct finite numbers, the i-th element is the largest of the first i with probability 1/i (each of the first i is equally likely to be the biggest). Adding one indicator per position:

```formula
E[U] = 1 + 1/2 + 1/3 + … + 1/n
E[U] = H_n ≈ ln(n) + 0.577
H_1000 ≈ 6.908 + 0.577 ≈ 7.5
where
U: the number of times the running maximum is updated
n: the number of elements; 1,000 in the last line
E[U]: the expected number of updates
H_n: the n-th **harmonic number**, the sum 1 + 1/2 + … + 1/n
H_1000: the harmonic number for n = 1,000
ln(n): the natural logarithm of n (log to base e ≈ 2.718); ln(1000) ≈ 6.908
0.577: the Euler–Mascheroni constant γ ≈ 0.5772, the limiting gap between H_n and ln(n)
…: and so on, one term per position
≈: approximately equal to
In words: the i-th element sets a new record with chance 1/i, so records get rarer as you go and only about 7.5 happen in 1,000 elements.
```

The harmonic number H_n turns up all over algorithm analysis, because it grows like the logarithm of n.

### Example: coupon collector

You independently choose a shard uniformly from n shards (at least one) on each request, with replacement, until every shard has been hit one or more times. When you have seen k shards, a new one turns up with probability (n − k)/n, so the wait for it is geometric with mean n/(n − k). By linearity, add the waits:

```formula
E[W] = n/n + n/(n − 1) + … + n/1
E[W] = n × H_n ≈ n × ln(n)
E[W] = 50 × H_50 ≈ 50 × 4.50 ≈ 225
where
W: the total number of requests until every shard has been seen
n: the number of shards; 50 in the last line
k: the number of distinct shards seen so far (0 up to n − 1)
n/(n − k): the expected wait for a new shard when k have been seen
H_n: the n-th harmonic number, 1 + 1/2 + … + 1/n
H_50: the harmonic number for n = 50, about 4.50
E[W]: the expected total number of requests
ln(n): the natural logarithm of n
…: and so on, one term for each new shard
≈: approximately equal to
In words: the last few unseen shards take the longest to hit, so covering all 50 takes about 225 requests, not 50.
```

This also tells you how long random testing takes to cover every case, or how many random probes find every node. (The shortcut n ln(n) leaves out about 0.577 × n requests, so it undercounts noticeably for modest n: 50 × ln(50) ≈ 196, about 13% below the exact 225.)

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

Expectation alone gives a crude but guaranteed bound on the **tail probability**, the chance of a large value.

```formula
P(X ≥ a) ≤ E[X] / a
P(L ≥ 100) ≤ 20 / 100 = 0.2
where
X: a random variable that is never negative, with a finite mean
a: any threshold greater than 0
P(X ≥ a): the probability that X is at least a
E[X]: the expected value (mean) of X
L: a request's latency in milliseconds (ms), with mean 20 ms
≥: greater than or equal to
≤: less than or equal to
In words: a non-negative quantity can be at least a only a fraction E[X]/a of the time, otherwise its average would be too high.
```

If mean request latency is 20 ms, at most 20% of requests can take 100 ms or more. The true tail can be smaller or attain this bound. For a useful finite bound, Markov needs a nonnegative variable and a known finite mean. It is used to turn expected running time into a "with probability at least 1/2" statement.

**Chebyshev's inequality** bounds deviations in both directions using the variance:

```formula
P(|X − μ| ≥ k × σ) ≤ 1 / k^2
where
X: a random variable with finite, non-zero variance
μ: mu, the mean of X
σ: sigma, the standard deviation of X (the square root of its variance)
k: how many standard deviations away from the mean; any number greater than 0
|X − μ|: the absolute value of X − μ, the distance from the mean ignoring direction
P: probability
≥: greater than or equal to
≤: less than or equal to
In words: X is at least k standard deviations from its mean at most 1/k² of the time; for k = 3, at most 1/9, about 11%.
```

It need not improve every Markov bound at every threshold.

## Pitfall: the mean of a ratio

The fact that the expectation of a function need not equal the function of the expectation matters in practice. Each download independently selects a speed of 10 MB/s or 90 MB/s with equal probability and keeps that speed for the entire transfer. The average speed is 50 MB/s, so you might predict a 100 MB download takes 2 s. But the expected time is:

```formula
E[T] = 0.5 × 100/10 + 0.5 × 100/90
E[T] = 5 + 0.556 ≈ 5.6 s
where
T: the transfer time, in seconds (s)
E[T]: the expected transfer time
0.5: the probability of each speed
100: the file size, in megabytes (MB)
10, 90: the two possible speeds, in megabytes per second (MB/s)
MB: megabyte, one million bytes
s: seconds
≈: approximately equal to
In words: half the downloads take 10 s and half take about 1.1 s, so the average time is about 5.6 s, nearly three times the 2 s you get by dividing by the average speed.
```

The slower transfers contribute more to the mean duration. This model differs from a single transfer whose speed fluctuates rapidly with equal time spent at each rate. When you average rates, decide whether you mean per unit time or per unit of work.

## Key takeaways
- A random variable assigns a number to each outcome; its expected value is the probability-weighted average of its values, and iid sample averages converge to it.
- Variance (mean of the square minus the square of the mean) measures spread; finite variances add over pairwise uncorrelated variables; independence is sufficient.
- Linearity (the expectation of a sum is the sum of the expectations) holds even for dependent variables.
- Count with indicators: the expected number of events that happen is the sum of their probabilities.
- Classic results: expected fixed points 1; idle bins about n/e; inversions n(n − 1)/4; record updates the harmonic number; coupon collector n times the harmonic number; geometric wait 1/p.
- Markov's inequality gives a tail bound from the mean alone; never assume the expectation of a non-linear function equals the function of the expectation.

## Further reading
- [Expected value — Wikipedia](https://en.wikipedia.org/wiki/Expected_value)
- [Indicator function — Wikipedia](https://en.wikipedia.org/wiki/Indicator_function)
- [Coupon collector's problem — Wikipedia](https://en.wikipedia.org/wiki/Coupon_collector%27s_problem)
- [Markov's inequality — Wikipedia](https://en.wikipedia.org/wiki/Markov%27s_inequality)
- [Mathematics for Computer Science (MIT OCW 6.042J)](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-fall-2010/)

- [Balanced Allocations — Azar, Broder, Karlin and Upfal](https://www.cs.tau.ac.il/~azar/box.pdf)
