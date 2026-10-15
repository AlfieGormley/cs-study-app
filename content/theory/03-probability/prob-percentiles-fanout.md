---
id: prob-percentiles-fanout
title: Compute percentiles and understand fan-out tails
level: advanced
minutes: 4
sourceLesson: prob-statistics
summary: State the sample percentile convention and allow ties.
---

## Percentiles

A **p-th percentile** is a distribution threshold defined by a chosen quantile convention; "p99" is shorthand for the 99th percentile, "p50" for the 50th. Under the empirical **nearest-rank** convention, at least the requested percentage of observations are at or below the threshold; ties can make the percentage strictly above it smaller than the remaining percentage. The population p50 is a median; sample conventions can differ from the usual averaged-middle median.

```formula
r = ⌈(pn) / 100⌉
Q_p = x_(r)
r = ⌈(90 × 10) / 100⌉ = 9
where
p: the percentile wanted, greater than 0 and at most 100 (90 in the last line); the code separately extends zero to return the minimum
n: the positive integer number of observations (10 in the last line)
r: the rank, the position in the sorted list to read off
⌈ ⌉: ceiling, round up to the next whole number; ⌈8.1⌉ = 9
x_(r): the r-th smallest observation (the list sorted ascending)
Q_p: the nearest-rank p-th percentile
In words: sort the values, go p% of the way along the list rounding up, and read the value there; for 10 latencies the p90 is the 9th smallest.
```

The code below implements the same rule (with zero returning the minimum):

```python
import math
from fractions import Fraction

def percentile(xs, p):
    # Nearest rank; p=0 returns minimum.
    s = sorted(xs)
    if not s or not 0 <= p <= 100:
        raise ValueError("invalid input")
    # Fraction avoids rank rounding drift.
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

## The tail at scale

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
P: probability; probabilities are dimensionless and apply to measurable events
≈: approximately equal to
In words: if each call is slow 1% of the time, a page that waits for 100 calls is slow about 63% of the time.
```

A backend's 1-in-100 event becomes the experience of nearly two-thirds of users. Jeff Dean and Luiz Barroso's paper *The Tail at Scale* (2013) made this argument from Google's systems and described mitigations such as **hedged requests**: send a backup request after a chosen delay and use the first acceptable answer. A delay near a measured p95 is one possible policy, not a universal threshold; extra load and request semantics matter.

## Key takeaways
- State the sample percentile convention and allow ties.
- Merge compatible observations or summaries rather than averaging percentiles.
- Independent fan-out amplifies the chance of at least one slow backend.

## Further reading
- [The Tail at Scale — Dean and Barroso](https://research.google/pubs/the-tail-at-scale/)
- [Histograms and summaries — Prometheus](https://prometheus.io/docs/practices/histograms/)
