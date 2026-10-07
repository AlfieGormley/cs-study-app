---
id: prob-statistics
title: Statistics for engineers
level: advanced
minutes: 16
summary: Mean versus median, latency percentiles and the tail at scale, standard errors and confidence intervals, and how to run an A/B test without fooling yourself through peeking, multiple comparisons or too small a sample.
---

Probability goes from a model to predictions. **Statistics** goes the other way: from data back to conclusions about the world. Engineers do this constantly, often without noticing. Is the new build slower? Did the checkout redesign raise conversion? Is p99 latency within the SLO?

This lesson covers the handful of statistical ideas that come up most in engineering, and the traps that catch experienced teams.

## Mean versus median

The **mean** is the sum divided by the count. The **median** is the middle sorted value, conventionally the average of the two middle values for an even-sized numeric sample. For a finite symmetric sample the mean and this median agree; for skewed data they can be wildly different.

> [!example] One slow request
> 99 requests take 10 ms and one takes 5,000 ms (a timeout).
>
> - Mean: (99 × 10 + 5,000) / 100 = 59.9 ms
> - Median: 10 ms
>
> The mean describes no actual request. The median ignores the timeout entirely.

Neither is "right"; they answer different questions.

- The **mean** matters for totals: total resource use is the request count times mean resource use per request. Wall-clock latency includes waiting and is not automatically CPU service time; capacity also depends on concurrency, utilisation and variability.
- The **median** describes the typical experience and is robust to outliers.
- Neither tells you about the slow tail that users complain about.

## Percentiles

A **p-th percentile** is a distribution threshold defined by a chosen quantile convention. Under the empirical nearest-rank convention, at least p% of observations are at or below the threshold; ties mean fewer than 100 − p% may be strictly above it. The population p50 is a median; sample conventions can differ from the usual averaged-middle median.

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

```
P(page slow) = 1 − 0.99^100 ≈ 0.63
```

A backend's 1-in-100 event becomes the experience of nearly two-thirds of users. Jeff Dean and Luiz Barroso's paper *The Tail at Scale* (2013) made this argument from Google's systems and described mitigations such as **hedged requests**: send a backup request after a chosen delay and use the first acceptable answer. A delay near a measured p95 is one possible policy, not a universal threshold; extra load and request semantics matter.

## Sampling and the standard error

You rarely measure everything; you measure a **sample** and estimate. The sample mean x̄ estimates the true mean μ. How far off is it likely to be?

For independent, identically distributed observations with finite standard deviation σ, the **standard error** of the mean is:

```
SE = σ / √n
```

Quadrupling the sample halves the standard error; the realised estimation error is still random. That √n is the central fact of measurement: precision gets expensive fast.

### Confidence intervals

Under suitable CLT conditions and a large enough sample for the approximation, x̄ is approximately normal. An approximate **95% confidence interval** is:

```
x̄ ± 1.96 × SE
```

> [!example] Latency benchmark
> 400 requests, mean 250 ms, sample SD 80 ms.
>
> SE = 80 / √400 = 4 ms. 95% CI = 250 ± 7.8 ms, i.e. about 242 to 258 ms.

For an iid Bernoulli **proportion** with p̂ observed in n trials, the plug-in standard error is:

```
SE = √(p̂(1 − p̂) / n)
```

The resulting Wald interval can be inaccurate near 0 or 1 or with small success/failure counts; Wilson or exact binomial intervals are alternatives. For a mean with estimated σ, a Student-t interval is exact under normal iid sampling and approaches the displayed normal interval for large samples.

A 5% conversion rate measured on 10,000 independent visitors has SE ≈ 0.22 percentage points, so the 95% CI is about 4.6% to 5.4%.

> [!note] What "95% confidence" means
> It is a statement about the procedure: if you repeated the experiment many times, about 95% of the intervals you computed would contain the true value. It does **not** mean "there is a 95% probability the true value is in this particular interval" (a Bayesian credible interval can make a posterior-probability statement under its prior and likelihood model).

These formulas assume independent observations. Requests from the same user, or latencies during the same GC pause, can be positively correlated, making an independence-based standard error too small. Correlation does not invariably increase uncertainty; its sign and structure matter. Benchmarks also suffer from warm-up effects and noisy neighbours, so run them repeatedly and interleave A and B rather than running all of A first.

## A/B testing

An A/B test randomly splits users between a control (A) and a variant (B) and compares a metric. Randomisation is what makes it work: it balances every other factor, known or unknown, between the groups in expectation.

### Hypothesis testing in one page

1. **Null hypothesis** H₀: the variant has no effect.
2. Compute a **test statistic** measuring how far the observed difference is from zero, in standard errors.
3. The **p-value** is the probability, under H₀ and the assumed sampling model, of a test statistic at least as extreme as observed in the pre-specified direction or directions.
4. If p < α (usually 0.05), call the result **statistically significant**.

Two kinds of error:

| | H₀ true | H₀ false |
|---|---|---|
| Significant | Type I (false positive), rate α | correct (power) |
| Not significant | correct | Type II (false negative), rate β |

**Power** = 1 − β, the chance of detecting a real effect of a given size. An 80% target is a common design choice, not a universal requirement.

> [!example] Two-proportion z-test
> Control: 1,000 conversions from 10,000 (10.0%). Variant: 1,100 from 10,000 (11.0%).
>
> Pooled rate 0.105. SE of the difference = √(0.105 × 0.895 × (1/10,000 + 1/10,000)) ≈ 0.00434. z = 0.010 / 0.00434 ≈ 2.31, two-sided p ≈ 0.021. Significant at α = 0.05.

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

A p-value of 0.021 does **not** mean "there is a 2.1% chance B is no better". It is P(data this extreme | no effect), not P(no effect | data). That is the Bayes inversion from lesson 2 again.

### Sample size: decide before you start

To detect a change from 10% to 11% conversion with α = 0.05 (two-sided) and 80% power:

```
n per arm ≈ (z₀.₉₇₅ + z₀.₈)² ×
            (p₁q₁ + p₂q₂) / δ²
          = (1.96 + 0.84)² ×
            (0.09 + 0.0979) / 0.01²
          ≈ 14,732 (roughly 14,750)
```

Using approximately equal arm variances gives the handy planning rule n ≈ 16 p(1 − p) / δ² per arm, here 16 × 0.09 / 0.0001 = 14,400. Notice δ² in the denominator: **halving the effect you want to detect quadruples the sample size**. Low traffic may make the required sample impractical within a stable experiment window; looking for a trend does not replace adequate sample size. This is an approximate planning formula, not an exact power guarantee.

## How A/B tests go wrong

### Peeking

Checking the p-value every day and stopping as soon as it dips below 0.05 can inflate the false positive rate above the nominal level. Each look is another chance for noise to cross the line. The amount of inflation depends on the test, sample sizes, look schedule and stopping rule.

> [!note] Evidence gap
> The previous 19% false-positive figure and claimed simulation run are omitted because no reproducible simulation or adequately specified design supported them. Ten looks do not determine one universal error rate.

Fixes: fix the sample size in advance and look once; or use methods designed for continuous monitoring (sequential testing, always-valid p-values), with error control appropriate to the sampling and stopping rules.

### Multiple comparisons

For 20 independent tests, each with exact null rejection probability 0.05, the chance of at least one false rejection is:

```
P(at least one 'significant')
  = 1 − 0.95^20 ≈ 0.64
```

A false rejection is likely in this independent example, but not certain. Correlated metrics need not have this 64% probability. Declare one primary metric in advance, and correct for multiple tests (Bonferroni: use α / k; or control a different quantity, the false discovery rate, with Benjamini–Hochberg under its independence or appropriate positive-dependence assumptions). Bonferroni controls family-wise error without requiring independence.

### Other traps

- **Sample ratio mismatch.** You planned a 50/50 split but got 50.8/49.2 on a million users. A chi-squared test shows this is wildly unlikely by chance, so investigate assignment and logging (for example redirects, bot filters or crashes) before interpreting the treatment comparison; this is strong evidence of a mismatch, not logical proof of a particular defect.
- **Novelty and learning effects.** Users click a new button because it is new. Use a pre-planned duration that covers relevant cycles; full weeks can address weekly seasonality but do not guarantee novelty or learning effects have settled.
- **Simpson's paradox.** A variant can win in every segment yet lose overall (or vice versa) if the segments are unevenly mixed between arms. Randomisation balances pre-treatment groups in expectation, but finite-sample imbalance, attrition or post-treatment conditioning can still produce this pattern. The issue also affects observational comparisons such as "users who enabled feature X convert more".
- **Statistical versus practical significance.** With enough data, a small effect can be statistically significant and still not justify the implementation cost. Whether a particular lift is detectable depends on its units, baseline variance and design. Always report the effect size with a confidence interval, not just p.

## Key takeaways
- Means are pulled by outliers and matter for capacity; medians describe the typical case; neither shows the tail.
- Use percentiles for latency; merge histograms, never average percentiles.
- With fan-out, rare backend slowness becomes common user slowness: 1 − 0.99¹⁰⁰ ≈ 63%.
- Standard error is σ/√n; a normal-approximation 95% CI is roughly estimate ± 1.96 SE when iid, finite-variance and sample-size conditions justify it.
- A p-value is a tail probability of a test statistic under the null sampling model, not the probability that the null is true.
- Fix sample size in advance (it scales with 1/δ²), don't peek, pick one primary metric and check for sample ratio mismatch.

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
