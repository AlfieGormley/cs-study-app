---
id: prob-distributions
title: "Distributions: binomial, geometric, Poisson, normal"
level: intermediate
minutes: 20
summary: The four distributions engineers meet most, what process each one models, their means and variances, and how to use them for packet loss, retries, request arrivals, capacity planning and quorums.
---

Standard distributions provide useful models for some random quantities in computing. Their formulas apply when the model assumptions fit the process; resemblance alone is not enough.

The trick is to match the **process** to the distribution, and check that model against the data:

| Process | Distribution |
|---|---|
| Successes in a fixed number of independent trials with the same success probability | Binomial |
| Independent trials with constant success probability until first success | Geometric |
| Events in a window of a homogeneous Poisson process | Poisson |
| Standardised sum of many independent, identically distributed effects with finite nonzero variance (approximately) | Normal |

The binomial and geometric distributions directly use **Bernoulli trials**: independent yes/no experiments that each succeed with the same probability. Poisson and normal distributions also arise as limits of suitable Bernoulli models, but their uses extend beyond those limits.

## Binomial: how many successes in n trials?

Run a fixed number of independent Bernoulli trials, each with the same success probability. The number of successes has a **binomial distribution**:

```formula
X ~ Bin(n, p)
P(X = k) = C(n, k) × p^k × (1 − p)^{n − k}
C(n, k) = n! / (k! × (n − k)!)
E[X] = n × p
Var(X) = n × p × (1 − p)
where
X: the number of successes, a whole number from 0 to n
~: "is distributed as", "has the distribution"
Bin(n, p): the binomial distribution with n trials and success probability p
n: the number of trials
p: the probability that one trial succeeds, between 0 and 1
k: a particular number of successes we ask about, 0 to n
P(X = k): the probability of exactly k successes
C(n, k): "n choose k", the number of ways to pick which k of the n trials succeed
!: factorial; n! = n × (n − 1) × … × 2 × 1, and 0! = 1
p^k: p multiplied by itself k times, the chance that k chosen trials all succeed
(1 − p)^{n − k}: the chance that the other n − k trials all fail
E[X]: the expected (mean) number of successes
Var(X): the variance of the number of successes
In words: count the arrangements with exactly k successes, times the probability of any one arrangement; on average you get n × p successes.
```

For example, with 10 fair coin tosses the chance of exactly 3 heads is C(10, 3) × 0.5¹⁰ = 120/1024 ≈ 0.117, and the mean is 5 heads.

> [!example] Packet loss
> A link drops each packet independently with probability 1%. You send 100 packets, so the number lost is binomial with 100 trials and probability 0.01.

```formula
P(L = 0) = 0.99^100 ≈ 0.366
P(L = 1) = 100 × 0.01 × 0.99^99 ≈ 0.370
P(L ≥ 2) ≈ 1 − 0.366 − 0.370 = 0.264
where
L: the number of packets lost out of 100
P(L = 0): the probability that none is lost
0.99: the chance one packet gets through
0.99^100: 0.99 multiplied by itself 100 times, one factor per packet
100: C(100, 1), the number of ways to choose which single packet is lost
0.01: the chance one packet is lost (1%)
≥: greater than or equal to
≈: approximately equal to
In words: a clean transfer happens only about 37% of the time, exactly one loss about 37%, and two or more about 26%.
```

Even at 1% loss, a 100-packet transfer suffers at least one loss nearly two times in three. That is why **TCP** (the Transmission Control Protocol, the internet's reliable-delivery protocol) needs retransmission to be cheap.

### Fleets and quorums

In a hypothetical fleet of 1,000 disks, suppose each independently has a 2% probability of failing during a year. The number of original disks that fail is binomial:

```formula
D ~ Bin(1000, 0.02)
E[D] = 1000 × 0.02 = 20
σ = √(1000 × 0.02 × 0.98) ≈ 4.4
where
D: the number of the original 1,000 disks that fail in the year
~: "is distributed as"
Bin(1000, 0.02): binomial with 1,000 trials (disks) and failure probability 0.02 (2%)
E[D]: the expected number of failures
σ: sigma, the standard deviation of D, the square root of trials × probability × (1 − probability), here 1000 × 0.02 × 0.98
√: the square root
0.98: the chance a disk survives the year, 1 − 0.02
≈: approximately equal to
In words: expect about 20 failures, typically give or take 4 or 5.
```

This does not count failures of replacement disks. A spare-stock policy also needs a tolerated shortage probability and replenishment lead time; the mean alone is insufficient.

A fixed 5-node majority-quorum cluster cannot form a majority when 3 or more nodes are down. If each node is independently down with probability 1% at a sampled instant:

```formula
P(N ≥ 3) = C(5, 3) × p^3 × q^2
  + C(5, 4) × p^4 × q + p^5
P(N ≥ 3) ≈ 10 × 10^{−6} ≈ 1 × 10^{−5}
where
N: the number of the 5 nodes that are down
P: probability
p: the probability one node is down, 0.01
q: the probability one node is up, 1 − p = 0.99
C(5, 3): "5 choose 3", the ways to pick which 3 nodes are down, which is 10
C(5, 4): the ways to pick which 4 are down, which is 5
p^3: p multiplied by itself 3 times; p^4 and p^5 likewise
≥: greater than or equal to
≈: approximately equal to
10^{−6}: one millionth
In words: losing quorum needs 3, 4 or 5 nodes down at once; the "exactly 3" term dominates at about 10 × 0.01³, roughly one chance in 100,000.
```

That is about 1 in 100,000, equivalent to roughly 5.2 expected minutes per 365-day year if these marginal probabilities remain constant. This estimates quorum loss due to node downtime, not total service unavailability: network partitions, leader elections and recovery also matter. Correlated failures invalidate the product model.

## Geometric: how long until the first success?

Repeat independent Bernoulli trials, each succeeding with the same probability, until the first success. The number of trials has a **geometric distribution**:

```formula
P(T = k) = (1 − p)^{k − 1} × p
E[T] = 1 / p
Var(T) = (1 − p) / p^2
P(T > k) = (1 − p)^k
where
T: the number of trials up to and including the first success
k: a particular trial count, 1, 2, 3, …
p: the success probability of each trial; more than 0, at most 1
(1 − p)^{k − 1}: the chance the first k − 1 trials all fail
P(T = k): the probability that the first success is on trial k
E[T]: the expected number of trials
Var(T): the variance of the number of trials
p^2: p multiplied by itself
P(T > k): the probability of still having no success after k trials
In words: fail k − 1 times then succeed once; on average it takes 1/p tries, and the chance of a long wait shrinks by a factor of 1 − p per extra try.
```

For a retry that succeeds 20% of the time, the mean is 5 attempts, and the chance of still failing after 10 attempts is 0.8¹⁰ ≈ 0.107.

Independent retries with constant success probability and independent fair-die rolls until a six fit this model. Open-addressing probes generally are not independent draws with replacement, so geometric waiting time is only a simplified probing model, not an exact law for every table.

### Memorylessness

The geometric distribution is **memoryless**: having already waited tells you nothing about how much longer you will wait.

```formula
P(T > m + k | T > m) = P(T > k)
where
T: the number of trials until the first success
m: the number of trials that have already failed; a whole number 0 or more
k: how many more trials we ask about; a whole number 0 or more
P(T > m): the probability of failing the first m trials; must be above 0
|: read "given"; the left side assumes the first m trials failed
P: probability
In words: after m failures, the chance of needing more than k further trials is exactly what it was at the start.
```

If the success probability p is strictly between 0 and 1 and you have already failed 10 times, the expected number of further attempts is still 1/p. The past failures are sunk; they do not make success "due". This is the formal version of the gambler's fallacy, and it holds only when trials really are independent with constant success probability. Persistent server overload can correlate failures or change the success probability; backoff can reduce retry load in that setting.

## Poisson: counting rare events in a window

Many independent rare opportunities can yield an approximately **Poisson** count. An exact example is the count in a window of fixed length of a homogeneous Poisson process, with constant intensity and independent increments. The Poisson parameter λ is the expected count in that window, not a rate with unspecified units:

```formula
P(X = k) = λ^k × e^{−λ} / k!
E[X] = λ
Var(X) = λ
where
X: the number of events in the window (0, 1, 2, …)
k: a particular count we ask about
λ: lambda, the expected number of events in the window; 0 or more
P(X = k): the probability of exactly k events
e: Euler's number, about 2.718, the base of natural logarithms; e^{−λ} is the chance of no events at all
λ^k: λ multiplied by itself k times
!: factorial; k! = k × (k − 1) × … × 1, and 0! = 1
E[X]: the expected count
Var(X): the variance of the count
In words: the chance of exactly k events depends only on the expected count λ; the mean and the variance are both λ.
```

For example, with 2 errors expected per hour:

```formula
P(X = 0) = e^{−2} ≈ 0.135
P(X = 2) = 2^2 × e^{−2} / 2! ≈ 0.271
where
X: the number of errors in one hour, Poisson with mean λ = 2
λ: lambda, the expected count, 2 errors per hour
P: probability
e: Euler's number, about 2.718
!: factorial; 2! = 2 × 1 = 2
≈: approximately equal to
In words: an hour with no errors happens about 13.5% of the time, and an hour with exactly two errors about 27%.
```

The mean equals the variance, a handy diagnostic. If your measured counts have variance much bigger than the mean ("overdispersion"), a single Poisson model does not match that dispersion. Bursts, changing intensity or heterogeneous populations are possible causes. Mean–variance equality alone does not establish a Poisson distribution.

### Poisson approximates binomial

When there are many trials and each has a small success probability, the binomial count is close to a Poisson count with the same mean.

```formula
Bin(n, p) ≈ Poisson(λ)   if λ = n × p
P(L = 0) ≈ e^{−1} ≈ 0.368
P(L ≥ 2) ≈ 1 − 2 × e^{−1} ≈ 0.264
where
Bin(n, p): binomial with n trials, success probability p
Poisson(λ): the Poisson distribution with mean λ (lambda)
n: the number of trials, large; 100 packets here
p: the per-trial probability, small; 0.01 here
λ: lambda, the matching mean, n × p = 1 for the packets
L: the number of lost packets
e: Euler's number, about 2.718
P: probability
≥: greater than or equal to
≈: approximately equal to
In words: for 100 packets at 1% loss, the Poisson shortcut gives 0.368 for no loss and 0.264 for two or more, almost identical to the exact binomial 0.366 and 0.264.
```

### Capacity planning

Requests arrive at an average of 5 per second, so the count in one second is modelled as Poisson with mean 5. Compare that count with a nominal capacity of 9 requests per second. How often does a one-second arrival count exceed 9? Add the probabilities of 0 to 9 and subtract from 1:

```formula
P(X ≥ 10)
  = 1 − Σ_{k=0}^{9} λ^k × e^{−λ} / k!
P(X ≥ 10) ≈ 0.0318   for λ = 5
where
X: the number of requests arriving in one second
P: probability
λ: lambda, the expected number per second, 5
k: a count from 0 to 9
Σ_{k=0}^{9}: sigma, "add up the term for k = 0, 1, …, 9"
e: Euler's number, about 2.718
!: factorial; k! = k × (k − 1) × … × 1, and 0! = 1
≥: greater than or equal to
≈: approximately equal to
In words: about 3.2% of one-second windows see 10 or more requests when 5 are expected.
```

The same sum in Python:

```python
from math import exp, factorial

def poisson_pmf(k, lam):
    return lam**k * exp(-lam) / factorial(k)

lam = 5
p_ok = sum(poisson_pmf(k, lam)
           for k in range(10))
print(round(1 - p_ok, 4))  # 0.0318
```

The direct PMF calculation is a small-parameter demonstration; large arguments can exceed the floating-point range or lose precision. Use a numerical distribution library for general calculations.

About 3.2% of one-second windows see 10 or more requests: about 0.0318 × 60 ≈ 1.91 such windows per minute in expectation. A threshold of 12 is exceeded (13 or more arrivals) with probability about 0.202%, still above 0.1%. A threshold of 13 is exceeded (14 or more) with probability about 0.0698%. These are arrival-count probabilities, not probabilities that a queue fills up or that latency is high: buffering, existing backlog and service times also matter.

### Useful properties

- **Poisson superposition**: independent Poisson streams add. Independent counts over the same window with means 2 and 3 sum to a Poisson count with mean 5.
- **Poisson thinning**: if each request is independently an error with some fixed probability, the errors also form a Poisson count, with the mean scaled down by that probability.
- **Inter-arrival times** of a homogeneous Poisson process follow an **exponential distribution**, the continuous memoryless cousin of the geometric.

```formula
X_1 + X_2 ~ Poisson(λ_1 + λ_2)
Y ~ Poisson(q × λ)
E[G] = 1 / r
where
X_1, X_2: independent Poisson counts over the same window with means λ_1 and λ_2
λ_1, λ_2: lambda 1 and 2, their expected counts, for example 2 and 3
~: "is distributed as"
Poisson( ): the Poisson distribution with the given mean
Y: the number of error requests when each of a Poisson(λ) stream of requests is independently an error with probability q
λ: lambda, the expected number of requests in the window
q: the probability that one request is an error
G: the gap between consecutive events, in time units
r: the intensity, the average number of events per time unit; greater than 0
E[G]: the expected gap
In words: merging independent streams adds their means; randomly keeping a fraction q of events scales the mean by q; and at 5 events per second the average gap is 1/5 = 0.2 s.
```

## Normal: the bell curve

The **normal** (Gaussian) distribution is continuous (it can take any real value), symmetric, and described by just two numbers, its mean and its standard deviation. The **68–95–99.7 rule** says how much of it lies within one, two and three standard deviations of the mean:

```formula
X ~ N(μ, σ^2)
P(|X − μ| ≤ σ) ≈ 0.683
P(|X − μ| ≤ 2 × σ) ≈ 0.954
P(|X − μ| ≤ 3 × σ) ≈ 0.997
where
X: a normally distributed random variable
~: "is distributed as"
N(μ, σ^2): the normal distribution with mean μ and variance σ^2
μ: mu, the mean, the centre of the bell
σ: sigma, the standard deviation, the width of the bell; greater than 0
σ^2: the variance, σ squared
|X − μ|: the distance of X from the mean, ignoring direction (absolute value)
P: probability
≤: less than or equal to
≈: approximately equal to
In words: about 68% of values lie within one standard deviation of the mean, 95% within two and 99.7% within three.
```

The bell shape, with the mean in the middle and one and two standard deviations either side:

```
          ____
        /|    |\
      /  |    |  \
   __/   |    |   \__
 ---+----+----+----+---
  μ−2σ  μ−σ  μ+σ  μ+2σ

```

A **z-score** says how many standard deviations a value is from the mean:

```formula
z = (x − μ) / σ
P(Z > 1.96) ≈ 0.025
where
z: the z-score of x, with no units
x: one particular value
μ: mu, the mean
σ: sigma, the standard deviation
Z: a **standard normal** variable, a normal with mean 0 and standard deviation 1
P: probability
1.96: the z-score that cuts off the top 2.5%, so 95% lies between −1.96 and +1.96
≈: approximately equal to
In words: a value 1.96 standard deviations above the mean is beaten only 2.5% of the time.
```

This is where the "1.96" in 95% confidence intervals comes from (lesson 6). For example, if response sizes are normal with mean 500 KB and standard deviation 50 KB:

```formula
z = (600 − 500) / 50 = 2
where
z: the z-score of a 600 KB response, in standard deviations
500: the mean size, in kilobytes (KB)
50: the standard deviation, in KB
KB: kilobyte, 1,000 bytes
In words: a 600 KB response is two standard deviations above the mean, so only about 2.3% of responses are larger.
```

### Why it is everywhere: the central limit theorem

One standard **central limit theorem (CLT)** says that the centred and scaled sum of independent, identically distributed variables with finite, nonzero variance converges in distribution to a standard normal as the sample size grows. This motivates a large-sample normal approximation; independence and finite variance alone are not sufficient for arbitrary non-identically distributed sequences, and no universal finite sample size guarantees accurate tails.

Roll 100 independent fair six-sided dice. Each has mean 3.5 and variance 35/12, and means and (for independent variables) variances add:

```formula
E[S] = 100 × 3.5 = 350
Var(S) = 100 × 35/12 ≈ 291.7
σ = √(291.7) ≈ 17.1
1.96 × σ ≈ 34
where
S: the sum of the 100 dice
E[S]: its expected value
Var(S): its variance
σ: sigma, the standard deviation of S
√: the square root
1.96: the z-score for the middle 95% of a normal distribution
≈: approximately equal to
In words: the sum centres on 350 and typically varies by about 17, so about 95% of the time it lands within 34 of 350.
```

The sum is close to normal, so about 95% of the time it lands within 350 ± 34 (exact enumeration gives 95.7% between 316 and 384).

The binomial has a useful normal approximation when both the expected successes and the expected failures are sufficiently large; the Poisson approaches normal as its mean grows. Check tail accuracy and use a **continuity correction** (treating the whole number k as the interval from k − 0.5 to k + 0.5) for discrete counts.

```formula
Bin(n, p) ≈ N(n × p, n × p × (1 − p))
Bin(1000, 0.02) ≈ N(20, 4.4^2)
where
Bin(n, p): binomial with n trials and success probability p
N(μ, σ^2): normal with mean μ and variance σ^2
n: the number of trials; 1,000 disks in the second line
p: the success probability; 0.02 in the second line
4.4: the standard deviation √(1000 × 0.02 × 0.98)
≈: approximately distributed as
In words: the disk-failure count behaves roughly like a bell curve centred on 20 with standard deviation 4.4.
```

> [!warning] Check latency tails before choosing a model
> Latency can be right-skewed, multimodal or heavy-tailed, but none of these properties follows merely from being nonnegative. Right skew also does not imply a heavy tail. A normal approximation may misestimate high percentiles; inspect measured distributions and enough tail observations before using it for an **SLO** (service level objective, a target such as "99% of requests under 200 ms"). Mean and standard deviation alone do not determine the tail.

## Choosing a distribution

1. **Fixed number of independent tries with the same success probability, count successes?** Binomial.
2. **Independent constant-probability trials until success?** Geometric. Waiting for the next event in a homogeneous Poisson process? Exponential distribution.
3. **Count independent rare events at a stable rate?** Consider a Poisson model and check its assumptions.
4. **A standardised sum or average meeting CLT conditions?** Consider a normal approximation and check finite-sample accuracy.
5. **Check the assumptions.** Independence and constant rates are the usual casualties: retries cluster, traffic is diurnal, failures cascade.

In Python, `scipy.stats` provides all of these (`binom`, `geom`, `poisson`, `norm`) with `cdf` and `sf` (survival function, 1 − cdf) methods. Discrete distributions provide `pmf`; the continuous normal provides `pdf` instead. Use `sf` directly for small upper-tail probabilities to reduce cancellation error. The standard library has `statistics.NormalDist`.

## Key takeaways
- Binomial: successes in a fixed number of independent, equal-probability trials; mean is trials times probability.
- Geometric: independent trials with a constant positive success probability, up to the first success; mean is one over that probability; memoryless.
- Poisson: a count model whose mean equals its variance; approximates the binomial for many trials with a small probability, using the same mean.
- Normal: 68–95–99.7 rule; a normal approximation for sums needs CLT conditions and adequate sample size.
- A Poisson count with mean 5 exceeds 9 about 3% of the time; arrival-count thresholds alone do not determine queueing performance.
- Measure latency and traffic distributions rather than assuming a normal model or a heavy tail.

## Further reading
- [Binomial distribution — Wikipedia](https://en.wikipedia.org/wiki/Binomial_distribution)
- [Geometric distribution — Wikipedia](https://en.wikipedia.org/wiki/Geometric_distribution)
- [Poisson distribution — Wikipedia](https://en.wikipedia.org/wiki/Poisson_distribution)
- [Central limit theorem — Wikipedia](https://en.wikipedia.org/wiki/Central_limit_theorem)
- [scipy.stats — SciPy documentation](https://docs.scipy.org/doc/scipy/reference/stats.html)

- [Poisson distribution API — SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.poisson.html)
- [Normal distribution — NIST](https://www.itl.nist.gov/div898/handbook/eda/section3/eda3661.htm)
