---
id: prob-poisson-capacity-streams
title: Interpret Poisson tails and combine streams
level: intermediate
minutes: 3
sourceLesson: prob-distributions
summary: Arrival-count exceedance is different from queueing delay or exceeding queue capacity.
---

A service whose average arrivals are below capacity can still receive busy windows. To estimate that risk, look at the arrival-count tail, while keeping it separate from actual queueing behaviour.

## Interpret a tail calculation

Suppose arrivals follow a homogeneous Poisson process averaging five per second. The code computes the chance of ten or more arrivals in a one-second window by subtracting the probabilities of zero through nine from one.

```python
from math import exp, factorial

def poisson_pmf(k, lam):
    return lam**k * exp(-lam) / factorial(k)

lam = 5
# Sum counts within the nine-request limit.
p_ok = sum(poisson_pmf(k, lam)
           for k in range(10))
print(round(1 - p_ok, 4))  # 0.0318
```

The result is about 3.18%. It describes arrival-count exceedance of a nine-request threshold. It is not automatically the chance of a full queue or high latency: those also depend on existing backlog, buffering and service times. A higher threshold reduces this count-tail probability without removing all uncertainty.

The direct calculation is suitable for this small example. Large arguments or tiny tails need numerical methods that stay within floating-point range and avoid cancellation; a distribution library's survival function is usually preferable to subtracting a nearly-one cumulative probability.

## Combining and selecting streams

**Poisson superposition** says independent Poisson streams combine into another Poisson stream whose rates add. Independent regions at two and three requests per second produce five per second together. A quiet combined window requires both regions to be quiet; averaging their quiet probabilities is wrong.

**Poisson thinning** independently keeps each event with a fixed probability, producing another Poisson stream with a reduced rate. A label based on a shared burst or changing state does not meet that assumption.

For a homogeneous Poisson process with positive rate, **inter-arrival times** follow an exponential distribution. A larger rate means a shorter average gap.

## Key takeaways
- A count exceeding a threshold does not directly measure queue failure.
- Superposition needs independent Poisson streams.
- Thinning needs independent fixed-probability selection.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
