---
id: prob-percentiles-fanout
title: Compute percentiles and understand fan-out tails
level: advanced
minutes: 3
sourceLesson: prob-statistics
summary: State the sample percentile convention and allow ties.
---

A **percentile** is a threshold in a distribution, not an average of its tail. Under the empirical **nearest-rank** convention, at least the requested percentage of observations are at or below that threshold. Ties can put more there.

## State the convention

The nearest-rank rule sorts observations, rounds the percentage rank upwards and selects that observation. This implementation extends the rule at zero by returning the minimum:

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

Some other conventions interpolate between observations. Small samples can therefore produce different answers. A percentile also describes observed spread, not confidence about a population parameter. A p99.9 from only 500 observations is effectively at the sample maximum and provides weak evidence about the population tail.

## Combine distributions, not percentile values

Averaging per-server p99 values does not produce fleet p99. Servers can have different traffic volumes and different distributions that the single percentile hides. Merge raw observations, histograms with compatible buckets or compatible quantile sketches over the same window, then estimate the combined percentile. Histograms and sketches retain representation error.

## Fan-out changes the user experience

If a page waits for every backend, any slow required backend can delay it. With independent calls, the chance all are fast is the product of their fast probabilities; its complement is the chance at least one is slow.

With 100 independent calls each having a 1% slow-event probability, about 63% of pages encounter a slow call. This is an explicit probability assumption: ties mean exceeding an empirical p99 need not occur exactly 1% of the time.

Reducing unnecessary fan-out can help. Hedged requests send a delayed backup and use the first acceptable result, but add load and require suitable request semantics. Correlated backend delays need a different probability model.

## Key takeaways
- Percentiles need a convention, adequate data and attention to ties.
- Combine observations or compatible summaries before computing fleet percentiles.
- Waiting for many backends amplifies opportunities for tail delays.

## Further reading
- [The Tail at Scale — Dean and Barroso](https://research.google/pubs/the-tail-at-scale/)
- [Histograms and summaries — Prometheus](https://prometheus.io/docs/practices/histograms/)
