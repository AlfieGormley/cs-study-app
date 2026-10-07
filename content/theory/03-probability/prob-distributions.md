---
id: prob-distributions
title: "Distributions: binomial, geometric, Poisson, normal"
level: intermediate
minutes: 14
summary: The four distributions engineers meet most, what process each one models, their means and variances, and how to use them for packet loss, retries, request arrivals, capacity planning and quorums.
---

Standard distributions provide useful models for some random quantities in computing. Their formulas apply when the model assumptions fit the process; resemblance alone is not enough.

The trick is to match the **process** to the distribution, and check that model against the data:

| Process | Distribution |
|---|---|
| Successes in n independent trials with the same success probability | Binomial |
| Independent trials with constant success probability until first success | Geometric |
| Events in a window of a homogeneous Poisson process | Poisson |
| Standardised sum of many independent, identically distributed effects with finite nonzero variance (approximately) | Normal |

The binomial and geometric distributions directly use **Bernoulli trials**: experiments with success probability p. Poisson and normal distributions also arise as limits of suitable Bernoulli models, but their uses extend beyond those limits.

## Binomial: how many successes in n trials?

Run n independent Bernoulli trials, each with probability p. The number of successes X is **binomial**, written Bin(n, p):

```
P(X = k) = C(n, k) pᵏ (1 − p)ⁿ⁻ᵏ

mean = np
var  = np(1 − p)
```

C(n, k) = n! / (k! (n − k)!) counts which k of the n trials succeed. The pᵏ(1 − p)ⁿ⁻ᵏ part is the probability of any one particular arrangement.

> [!example] Packet loss
> A link drops each packet independently with probability 1%. You send 100 packets. The number lost is Bin(100, 0.01).
>
> - P(none lost) = 0.99¹⁰⁰ ≈ 0.366
> - P(exactly 1) = 100 × 0.01 × 0.99⁹⁹ ≈ 0.370
> - P(2 or more) ≈ 1 − 0.366 − 0.370 = 0.264
>
> Even at 1% loss, a 100-packet transfer suffers at least one loss nearly two times in three. That is why TCP needs retransmission to be cheap.

### Fleets and quorums

In a hypothetical fleet of 1,000 disks, suppose each independently has a 2% probability of failing during a year. The number of original disks that fail is Bin(1000, 0.02): mean 20, standard deviation √(1000 × 0.02 × 0.98) ≈ 4.4. This does not count failures of replacement disks. A spare-stock policy also needs a tolerated shortage probability and replenishment lead time; the mean alone is insufficient.

A fixed 5-node majority-quorum cluster cannot form a majority when 3 or more nodes are down. If each node is independently down with probability 1% at a sampled instant:

```
P(≥3 down) = C(5,3)p³q² + C(5,4)p⁴q + p⁵
           ≈ 10 × 10⁻⁶ ≈ 1 × 10⁻⁵
```

About 10⁻⁵, equivalent to roughly 5.2 expected minutes per 365-day year if these marginal probabilities remain constant. This estimates quorum loss due to node downtime, not total service unavailability: network partitions, leader elections and recovery also matter. Correlated failures invalidate the product model.

## Geometric: how long until the first success?

Repeat independent Bernoulli(p) trials with constant 0 < p ≤ 1 until the first success. The number of trials T is **geometric**:

```
P(T = k) = (1 − p)ᵏ⁻¹ p     k = 1, 2, ...

mean = 1/p
var  = (1 − p)/p²
P(T > k) = (1 − p)ᵏ
```

Independent retries with constant success probability and independent fair-die rolls until a six fit this model. Open-addressing probes generally are not independent draws with replacement, so geometric waiting time is only a simplified probing model, not an exact law for every table.

### Memorylessness

For nonnegative integers m and k with P(T > m) > 0, the geometric distribution is memoryless:

```
P(T > m + k | T > m) = P(T > k)
```

For 0 < p < 1, if you have already failed 10 times, the expected number of further attempts is still 1/p. The past failures are sunk; they do not make success "due". This is the formal version of the gambler's fallacy, and it holds only when trials really are independent with constant p. Persistent server overload can correlate failures or change the success probability; backoff can reduce retry load in that setting.

## Poisson: counting rare events in a window

Many independent rare opportunities can yield an approximately **Poisson** count. An exact example is the count in a fixed window of a homogeneous Poisson process, with constant intensity and independent increments. Here λ ≥ 0 denotes the expected count in that window, not a rate with unspecified units:

```
P(X = k) = λᵏ e^(−λ) / k!

mean = λ
var  = λ
```

The mean equals the variance, a handy diagnostic. If your measured counts have variance much bigger than the mean ("overdispersion"), a single Poisson model does not match that dispersion. Bursts, changing intensity or heterogeneous populations are possible causes. Mean–variance equality alone does not establish a Poisson distribution.

### Poisson approximates binomial

When n is large and p is small, Bin(n, p) ≈ Poisson(λ = np). For the packet example, Poisson(1) gives P(0) = e⁻¹ ≈ 0.368 and P(≥2) ≈ 0.264, almost identical to the exact binomial.

### Capacity planning

Requests arrive at an average of 5 per second, modelled as Poisson(5). Compare that count with a nominal capacity of 9 requests per second. How often does a one-second arrival count exceed 9?

```python
from math import exp, factorial

def poisson_pmf(k, lam):
    return lam**k * exp(-lam) / factorial(k)

lam = 5
p_ok = sum(poisson_pmf(k, lam)
           for k in range(10))
print(round(1 - p_ok, 4))  # 0.0318
```

The direct PMF calculation is a small-parameter demonstration; large arguments can overflow or lose precision. Use a numerical distribution library for general calculations.

About 3.2% of one-second windows see 10 or more requests: about 1.91 such windows per minute in expectation. A threshold of 12 is exceeded with probability P(X ≥ 13) ≈ 0.202%, still above 0.1%. A threshold of 13 is exceeded with probability P(X ≥ 14) ≈ 0.0698%. These are arrival-count probabilities, not queue-overflow or latency probabilities: buffering, existing backlog and service times also matter.

### Useful properties

- **Superposition**: independent Poisson streams add. Independent counts over the same window with means 2 and 3 sum to Poisson(5).
- **Thinning**: if each request is independently an error with probability q, errors form Poisson(qλ).
- **Inter-arrival times** of a homogeneous Poisson process with positive intensity r events per time unit are **exponential** with mean 1/r time units, the continuous memoryless cousin of the geometric.

## Normal: the bell curve

The **normal** (Gaussian) distribution N(μ, σ²) is continuous, symmetric, and described by its mean μ and positive standard deviation σ. The 68–95–99.7 rule:

```
          ____
        /|    |\
      /  |    |  \
   __/   |    |   \__
 ---+----+----+----+---
  μ−2σ  μ−σ  μ+σ  μ+2σ

within 1σ: ≈ 68.3%
within 2σ: ≈ 95.4%
within 3σ: ≈ 99.7%
```

A **z-score** z = (x − μ)/σ says how many standard deviations x is from the mean. P(Z > 1.96) ≈ 2.5%, which is where the "1.96" in 95% confidence intervals comes from (lesson 6).

### Why it is everywhere: the central limit theorem

One standard **central limit theorem (CLT)** says that the centred and scaled sum of independent, identically distributed variables with finite, nonzero variance converges in distribution to a standard normal as the sample size grows. This motivates a large-sample normal approximation; independence and finite variance alone are not sufficient for arbitrary non-identically distributed sequences, and no universal finite sample size guarantees accurate tails.

Roll 100 independent fair six-sided dice. Each has mean 3.5 and variance 35/12. The sum has mean 350 and variance 100 × 35/12, so σ = √291.7 ≈ 17.1. The sum is close to normal, so about 95% of the time it lands within 350 ± 34 (exact enumeration gives 95.7% between 316 and 384).

The binomial has a useful normal approximation when both np and n(1 − p) are sufficiently large; the Poisson approaches normal as λ grows. Check tail accuracy and use a continuity correction for discrete counts. Bin(1000, 0.02) is roughly N(20, 4.4²).

> [!warning] Check latency tails before choosing a model
> Latency can be right-skewed, multimodal or heavy-tailed, but none of these properties follows merely from being nonnegative. Right skew also does not imply a heavy tail. A normal approximation may misestimate high percentiles; inspect measured distributions and enough tail observations before using it for an SLO. Mean and standard deviation alone do not determine the tail.

## Choosing a distribution

1. **Fixed number of independent tries with the same success probability, count successes?** Binomial.
2. **Independent constant-probability trials until success?** Geometric. Waiting for the next event in a homogeneous Poisson process? Exponential.
3. **Count independent rare events at a stable rate?** Consider a Poisson model and check its assumptions.
4. **A standardised sum or average meeting CLT conditions?** Consider a normal approximation and check finite-sample accuracy.
5. **Check the assumptions.** Independence and constant rates are the usual casualties: retries cluster, traffic is diurnal, failures cascade.

In Python, `scipy.stats` provides all of these (`binom`, `geom`, `poisson`, `norm`) with `cdf` and `sf` (survival function, 1 − cdf) methods. Discrete distributions provide `pmf`; the continuous normal provides `pdf` instead. Use `sf` directly for small upper-tail probabilities to reduce cancellation error. The standard library has `statistics.NormalDist`.

## Key takeaways
- Binomial Bin(n, p): successes in n independent, equal-probability trials; mean np, variance np(1 − p).
- Geometric: independent trials with constant p > 0 to the first success; mean 1/p; memoryless.
- Poisson(λ): a count model with mean = variance = λ; approximates Bin(n, p) for large n, small p and λ = np.
- Normal: 68–95–99.7 rule; a normal approximation for sums needs CLT conditions and adequate sample size.
- Poisson(5) exceeds 9 about 3% of the time; arrival-count thresholds alone do not determine queueing performance.
- Measure latency and traffic distributions rather than assuming a normal model or a heavy tail.

## Further reading
- [Binomial distribution — Wikipedia](https://en.wikipedia.org/wiki/Binomial_distribution)
- [Geometric distribution — Wikipedia](https://en.wikipedia.org/wiki/Geometric_distribution)
- [Poisson distribution — Wikipedia](https://en.wikipedia.org/wiki/Poisson_distribution)
- [Central limit theorem — Wikipedia](https://en.wikipedia.org/wiki/Central_limit_theorem)
- [scipy.stats — SciPy documentation](https://docs.scipy.org/doc/scipy/reference/stats.html)

- [Poisson distribution API — SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.poisson.html)
- [Normal distribution — NIST](https://www.itl.nist.gov/div898/handbook/eda/section3/eda3661.htm)
