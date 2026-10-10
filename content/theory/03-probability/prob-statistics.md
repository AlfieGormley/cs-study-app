---
id: prob-statistics
title: Statistics for engineers
level: advanced
minutes: 22
summary: Mean versus median, latency percentiles and the tail at scale, standard errors and confidence intervals, and how to run an A/B test without fooling yourself through peeking, multiple comparisons or too small a sample.
---

Probability goes from a model to predictions. **Statistics** goes the other way: from data back to conclusions about the world. Engineers do this constantly, often without noticing. Is the new build slower? Did the checkout redesign raise conversion? Is the 99th-percentile (p99) latency within the SLO (service level objective)?

This lesson covers the handful of statistical ideas that come up most in engineering, and the traps that catch experienced teams.

## Mean versus median

The **mean** (arithmetic mean) is the sum divided by the count. The **median** is the middle sorted value, conventionally the average of the two middle values for an even-sized numeric sample. For a finite symmetric sample the mean and this median agree; for skewed data they can be wildly different.

In symbols, the mean of a sample of values is:

```formula
x̄ = (x_1 + x_2 + … + x_n) / n
where
x̄: "x-bar", the sample mean
x_1, x_2, x_n: the first, second and last values in the sample
n: the number of values
…: and so on, every value in between
In words: add every value and divide by how many there are.
```

> [!example] One slow request
> 99 requests take 10 ms (milliseconds) and one takes 5,000 ms (a timeout).

```formula
x̄ = (99 × 10 + 5,000) / 100
x̄ = 5,990 / 100 = 59.9 ms
M = 10 ms
where
x̄: the mean latency, in milliseconds (ms)
M: the median latency, the middle value when sorted (both middle values are 10 ms)
ms: milliseconds, thousandths of a second
In words: one timeout drags the mean to about 60 ms even though 99 of the 100 requests took 10 ms; the median stays at 10 ms.
```

The mean describes no actual request. The median ignores the timeout entirely.

Neither is "right"; they answer different questions.

- The **mean** matters for totals: total resource use is the request count times mean resource use per request. Wall-clock latency includes waiting and is not automatically CPU service time; capacity also depends on concurrency, utilisation and variability.
- The **median** describes the typical experience and is robust to outliers.
- Neither tells you about the slow tail that users complain about.

## Percentiles

A **p-th percentile** is a distribution threshold defined by a chosen quantile convention; "p99" is shorthand for the 99th percentile, "p50" for the 50th. Under the empirical **nearest-rank** convention, at least p% of observations are at or below the threshold; ties mean fewer than (100 − p)% may be strictly above it. The population p50 is a median; sample conventions can differ from the usual averaged-middle median.

```formula
r = ⌈p × n / 100⌉
Q_p = x_(r)
r = ⌈90 × 10 / 100⌉ = 9
where
p: the percentile wanted, from 0 to 100 (90 in the last line)
n: the number of observations (10 in the last line)
r: the rank, the position in the sorted list to read off
⌈ ⌉: ceiling, round up to the next whole number; ⌈8.1⌉ = 9
x_(r): the r-th smallest observation (the list sorted ascending)
Q_p: the nearest-rank p-th percentile
In words: sort the values, go p% of the way along the list rounding up, and read the value there; for 10 latencies the p90 is the 9th smallest.
```

The code below implements the same rule (with p = 0 returning the minimum):

```python
import math
from fractions import Fraction

def percentile(xs, p):
    # Nearest rank; p=0 returns minimum.
    s = sorted(xs)
    if not s or not 0 <= p <= 100:
        raise ValueError("invalid input")
    k = math.ceil(
        Fraction(str(p)) * len(s) / 100
    )
    return s[max(k - 1, 0)]

lat = [12, 15, 11, 240, 14,
       13, 16, 12, 900, 14]
print(percentile(lat, 50))  # 14
print(percentile(lat, 90))  # 240
```

There are several percentile definitions (nearest rank, linear interpolation); they differ on small samples, so be consistent. Python's `statistics.quantiles` and NumPy's `percentile` both interpolate by default.

Latency SLOs can be expressed using percentile thresholds or the fraction of requests below a threshold, for example "p99 under 300 ms over 28 days". Percentiles need enough data: a p99.9 from 500 requests is the single slowest request or close to it, which is a very uncertain estimate of a population tail.

> [!warning] You cannot average percentiles
> If server A's p99 is 100 ms and server B's is 300 ms, you cannot infer that the combined p99 is 200 ms. It depends on both full distributions. Store compatible **histograms** or mergeable quantile sketches, merge them over the same time window, then estimate the combined percentile. Prometheus histograms and HdrHistogram retain bucket counts; t-digest is a quantile sketch. Their estimates have representation error; raw observations permit an exact sample quantile under a specified convention.

### The tail at scale

Why care about p99 when 99% of requests are fine? Because one user action often fans out to many backends and must wait for the slowest.

Suppose each backend call is slow (beyond its p99) with probability 0.01, independently. A page that needs 100 backend calls is slow if any of them is:

```formula
P(S) = 1 − (1 − q)^N
P(S) = 1 − 0.99^100 ≈ 0.63
where
S: the event "the page is slow" (at least one of its backend calls is slow)
q: the chance one backend call is slow, 0.01
N: the number of backend calls the page needs, 100
0.99^100: the chance all 100 calls are fast, 100 copies of 0.99 multiplied together
P: probability
≈: approximately equal to
In words: if each call is slow 1% of the time, a page that waits for 100 calls is slow about 63% of the time.
```

A backend's 1-in-100 event becomes the experience of nearly two-thirds of users. Jeff Dean and Luiz Barroso's paper *The Tail at Scale* (2013) made this argument from Google's systems and described mitigations such as **hedged requests**: send a backup request after a chosen delay and use the first acceptable answer. A delay near a measured p95 is one possible policy, not a universal threshold; extra load and request semantics matter.

## Sampling and the standard error

You rarely measure everything; you measure a **sample** and estimate. The sample mean estimates the true (population) mean. How far off is it likely to be?

For independent, identically distributed observations with a finite standard deviation, the **standard error** of the mean is:

```formula
SE = σ / √(n)
where
SE: the standard error, the typical distance between the sample mean x̄ and the true mean μ (mu)
σ: sigma, the standard deviation of a single observation, in the same units as the data
n: the number of observations in the sample
√: the square root
In words: averaging n independent observations shrinks the typical error by a factor of the square root of n.
```

For example, with a single-request standard deviation of 80 ms, 100 requests give a standard error of 8 ms and 400 requests give 4 ms.

Quadrupling the sample halves the standard error; the realised estimation error is still random. That square root is the central fact of measurement: precision gets expensive fast.

### Confidence intervals

Under suitable **central limit theorem (CLT)** conditions and a large enough sample for the approximation, the sample mean is approximately normal. An approximate **95% confidence interval** is:

```formula
x̄ ± 1.96 × SE
where
x̄: "x-bar", the sample mean
±: plus or minus; the interval runs from x̄ − 1.96 × SE to x̄ + 1.96 × SE
SE: the standard error of the mean
1.96: the number of standard errors that captures the middle 95% of a normal distribution (2.5% is cut off in each tail)
In words: take the estimate and go about two standard errors either side.
```

> [!example] Latency benchmark
> 400 requests, mean 250 ms, sample **standard deviation (SD)** 80 ms.

```formula
SE = 80 / √(400) = 80 / 20 = 4 ms
1.96 × SE = 1.96 × 4 ≈ 7.8 ms
CI = 250 ± 7.8 ms ≈ 242 to 258 ms
where
SE: the standard error of the mean latency, in milliseconds (ms)
80: the sample standard deviation of one request's latency, in ms
400: the number of requests measured
√: the square root
1.96: the 95% multiplier for a normal distribution
CI: the 95% confidence interval
±: plus or minus
ms: milliseconds
≈: approximately equal to
In words: 400 requests pin the mean latency down to about ±8 ms.
```

For an **independent and identically distributed (iid)** Bernoulli **proportion**, the estimated standard error is:

```formula
SE = √(p̂ × (1 − p̂) / n)
SE = √(0.05 × 0.95 / 10,000) ≈ 0.0022
CI ≈ 0.05 ± 1.96 × 0.0022
CI ≈ 0.046 to 0.054
where
p̂: "p-hat", the observed proportion, for example the fraction of visitors who converted; 0.05 (5%) here
n: the number of trials (visitors), 10,000 here
SE: the standard error of the proportion
CI: the approximate 95% confidence interval
√: the square root
±: plus or minus
1.96: the 95% normal multiplier
≈: approximately equal to
In words: a 5% rate measured on 10,000 visitors is uncertain by about 0.22 percentage points, so the 95% interval is roughly 4.6% to 5.4%.
```

The resulting **Wald interval** can be inaccurate near 0 or 1 or with small success/failure counts; Wilson or exact binomial intervals are alternatives. For a mean with an estimated standard deviation, a **Student-t interval** is exact under normal iid sampling and approaches the displayed normal interval for large samples.

> [!note] What "95% confidence" means
> It is a statement about the procedure: if you repeated the experiment many times, about 95% of the intervals you computed would contain the true value. It does **not** mean "there is a 95% probability the true value is in this particular interval" (a Bayesian credible interval can make a posterior-probability statement under its prior and likelihood model).

These formulas assume independent observations. Requests from the same user, or latencies during the same **garbage collection (GC)** pause, can be positively correlated, making an independence-based standard error too small. Correlation does not invariably increase uncertainty; its sign and structure matter. Benchmarks also suffer from warm-up effects and noisy neighbours, so run them repeatedly and interleave A and B rather than running all of A first.

## A/B testing

An A/B test randomly splits users between a control (A) and a variant (B) and compares a metric. Randomisation is what makes it work: it balances every other factor, known or unknown, between the groups in expectation.

### Hypothesis testing in one page

1. **Null hypothesis**: the variant has no effect.
2. Compute a **test statistic** measuring how far the observed difference is from zero, in standard errors.
3. The **p-value** is the probability, under the null hypothesis and the assumed sampling model, of a test statistic at least as extreme as observed in the pre-specified direction or directions.
4. If the p-value is below a threshold chosen in advance (the **significance level**, usually 0.05), call the result **statistically significant**.

Two kinds of error:

| | No real effect | Real effect |
|---|---|---|
| Significant | **Type I error** (false positive) | correct (power) |
| Not significant | correct | **Type II error** (false negative) |

The error rates have standard symbols:

```formula
α = P(R | H_0)
β = P(¬R | H_1)
Pow = 1 − β
where
H_0: "H-nought", the null hypothesis that the variant has no effect
H_1: the alternative, a real effect of a stated size
R: the event "the test declares the result significant" (rejects H_0)
¬R: "not R", the test does not declare significance
|: read "given"; P(R | H_0) is the chance of rejecting when there is no effect
P: probability
α: alpha, the significance level, the Type I (false positive) rate, usually 0.05
β: beta, the Type II (false negative) rate for an effect of the stated size
Pow: the **statistical power**, the chance of detecting a real effect of that size
In words: α is how often you cry wolf when nothing changed; β is how often you miss a real change; power is one minus β.
```

An 80% power target is a common design choice, not a universal requirement.

> [!example] Two-proportion z-test
> Control: 1,000 conversions from 10,000 (10.0%). Variant: 1,100 from 10,000 (11.0%).

```formula
p̄ = (c_1 + c_2) / (n_1 + n_2)
p̄ = 2,100 / 20,000 = 0.105
SE_d = √(p̄ × (1 − p̄) × (1/n_1 + 1/n_2))
SE_d = √(0.105 × 0.895 × 0.0002)
SE_d ≈ 0.00434
z = (p̂_2 − p̂_1) / SE_d
z = 0.010 / 0.00434 ≈ 2.31
where
c_1, c_2: conversions in control and variant, 1,000 and 1,100
n_1, n_2: users in each arm, 10,000 each
p̂_1, p̂_2: the observed conversion rates, 0.100 and 0.110
p̄: "p-bar", the pooled rate, both arms combined, used because the null hypothesis says they share one rate
SE_d: the standard error of the difference between the two rates under the null hypothesis
z: the test statistic, the observed difference measured in standard errors
√: the square root
≈: approximately equal to
In words: the variant's 1-point lift is about 2.3 standard errors from zero.
```

A z of 2.31 has a two-sided p-value of about 0.021 (the chance a standard normal lands more than 2.31 from 0 in either direction), so the result is significant at the 0.05 level.

```python
from math import sqrt

def ab_test(c1, n1, c2, n2):
    # Independent Bernoulli samples.
    # Large-count normal approximation.
    counts = (c1, n1, c2, n2)
    if not all(type(x) is int
               for x in counts):
        raise ValueError("integer counts")
    if not (n1 > 0 and n2 > 0
            and 0 <= c1 <= n1
            and 0 <= c2 <= n2):
        raise ValueError("invalid counts")
    p1, p2 = c1 / n1, c2 / n2
    pool = (c1 + c2) / (n1 + n2)
    se = sqrt(pool * (1 - pool)
              * (1/n1 + 1/n2))
    if se == 0:
        raise ValueError("zero variance")
    z = (p2 - p1) / se
    # Avoid tail-probability cancellation.
    from math import erfc
    p = erfc(abs(z) / sqrt(2))
    return z, p

print(ab_test(1000, 10000, 1100, 10000))
# z ≈ 2.31, p ≈ 0.021
```

A p-value of 0.021 does **not** mean "there is a 2.1% chance B is no better". It is the chance of data this extreme given no effect, not the chance of no effect given the data. That is the Bayes inversion from lesson 2 again.

### Sample size: decide before you start

To detect a change from 10% to 11% conversion with a two-sided significance level of 0.05 and 80% power, the standard normal-approximation planning formula gives the users needed in each arm:

```formula
n ≈ (z_{0.975} + z_{0.8})^2
  × (p_1 × q_1 + p_2 × q_2) / δ^2
n ≈ (1.96 + 0.84)^2
  × (0.09 + 0.0979) / 0.01^2
n ≈ 7.84 × 0.1879 / 0.0001 ≈ 14,732
where
n: the number of users needed in each arm
z_{0.975}: 1.96, the standard normal value with 97.5% below it; it sets the two-sided 5% significance level
z_{0.8}: about 0.84, the standard normal value with 80% below it; it sets 80% power
p_1, p_2: the baseline and target conversion rates, 0.10 and 0.11
q_1, q_2: one minus each rate, 0.90 and 0.89; so p_1 × q_1 = 0.09 and p_2 × q_2 = 0.0979
δ: delta, the difference to detect, 0.11 − 0.10 = 0.01
≈: approximately equal to; 14,731.4 is rounded up because users come in whole numbers (unrounded z values give about 14,750)
In words: detecting a 1-point lift on a 10% base needs roughly 15,000 users per arm.
```

Using approximately equal arm variances gives a handy planning rule:

```formula
n ≈ 16 × p × (1 − p) / δ^2
n ≈ 16 × 0.1 × 0.9 / 0.01^2 = 14,400
where
n: users per arm
p: the baseline rate, 0.10
δ: delta, the difference to detect, 0.01
16: about 2 × (1.96 + 0.84)^2 = 15.7, rounded up; it bakes in 5% significance and 80% power
≈: approximately equal to
In words: sixteen times the per-user variance divided by the squared effect gives a quick sample-size estimate.
```

Notice the effect size is squared in the denominator: **halving the effect you want to detect quadruples the sample size**. Low traffic may make the required sample impractical within a stable experiment window; looking for a trend does not replace adequate sample size. This is an approximate planning formula, not an exact power guarantee.

## How A/B tests go wrong

### Peeking

Checking the p-value every day and stopping as soon as it dips below 0.05 can inflate the false positive rate above the stated 5%. Each look is another chance for noise to cross the line. The amount of inflation depends on the test, sample sizes, look schedule and stopping rule.

> [!note] Evidence gap
> The previous 19% false-positive figure and claimed simulation run are omitted because no reproducible simulation or adequately specified design supported them. Ten looks do not determine one universal error rate.

Fixes: fix the sample size in advance and look once; or use methods designed for continuous monitoring (sequential testing, always-valid p-values), with error control appropriate to the sampling and stopping rules.

### Multiple comparisons

For 20 independent tests, each with exact null rejection probability 0.05, the chance of at least one false rejection is:

```formula
P(F) = 1 − (1 − α)^k
P(F) = 1 − 0.95^20 ≈ 0.64
where
F: the event "at least one test is falsely declared significant"
α: alpha, each test's false positive rate, 0.05
k: the number of independent tests, 20
0.95^20: the chance all 20 correctly come out non-significant
P: probability
≈: approximately equal to
In words: twenty independent 5% chances add up to about a 64% chance of at least one false alarm.
```

A false rejection is likely in this independent example, but not certain. Correlated metrics need not have this 64% probability. Declare one primary metric in advance, and correct for multiple tests (the **Bonferroni correction** tests each of the k metrics at the significance level divided by k, so 0.05 / 20 = 0.0025; or control a different quantity, the false discovery rate, with Benjamini–Hochberg under its independence or appropriate positive-dependence assumptions). Bonferroni controls family-wise error without requiring independence.

### Other traps

- **Sample ratio mismatch (SRM).** You planned a 50/50 split but got 50.8/49.2 on a million users. A **chi-squared test** shows this is wildly unlikely by chance, so investigate assignment and logging (for example redirects, bot filters or crashes) before interpreting the treatment comparison; this is strong evidence of a mismatch, not logical proof of a particular defect.
- **Novelty and learning effects.** Users click a new button because it is new. Use a pre-planned duration that covers relevant cycles; full weeks can address weekly seasonality but do not guarantee novelty or learning effects have settled.
- **Simpson's paradox.** A variant can win in every segment yet lose overall (or vice versa) if the segments are unevenly mixed between arms. Randomisation balances pre-treatment groups in expectation, but finite-sample imbalance, attrition or post-treatment conditioning can still produce this pattern. The issue also affects observational comparisons such as "users who enabled feature X convert more".
- **Statistical versus practical significance.** With enough data, a small effect can be statistically significant and still not justify the implementation cost. Whether a particular lift is detectable depends on its units, baseline variance and design. Always report the effect size with a confidence interval, not just p.

## Key takeaways
- Means are pulled by outliers and matter for capacity; medians describe the typical case; neither shows the tail.
- Use percentiles for latency; merge histograms, never average percentiles.
- With fan-out, rare backend slowness becomes common user slowness: 1% per call becomes about 63% for a page of 100 calls.
- The standard error is the standard deviation divided by the square root of the sample size; a normal-approximation 95% confidence interval is roughly the estimate plus or minus 1.96 standard errors when iid, finite-variance and sample-size conditions justify it.
- A p-value is a tail probability of a test statistic under the null sampling model, not the probability that the null is true.
- Fix sample size in advance (it scales with one over the squared effect size), don't peek, pick one primary metric and check for sample ratio mismatch.

## Further reading
- [The Tail at Scale — Dean and Barroso, CACM 2013](https://research.google/pubs/the-tail-at-scale/)
- [Percentile — Wikipedia](https://en.wikipedia.org/wiki/Percentile)
- [Confidence interval — Wikipedia](https://en.wikipedia.org/wiki/Confidence_interval)
- [A/B testing — Wikipedia](https://en.wikipedia.org/wiki/A/B_testing)
- [How Not To Run an A/B Test — Evan Miller](https://www.evanmiller.org/how-not-to-run-an-ab-test.html)
- [Multiple comparisons problem — Wikipedia](https://en.wikipedia.org/wiki/Multiple_comparisons_problem)

- [Statement on p-values — American Statistical Association](https://www.amstat.org/asa/files/pdfs/p-valuestatement.pdf)
- [Confidence intervals for proportions — NIST](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm)
- [Histograms and summaries — Prometheus](https://prometheus.io/docs/practices/histograms/)
