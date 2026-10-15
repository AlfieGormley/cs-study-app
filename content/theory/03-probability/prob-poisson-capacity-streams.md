---
id: prob-poisson-capacity-streams
title: Calculate Poisson tails and combine streams
level: intermediate
minutes: 3
sourceLesson: prob-distributions
summary: Arrival-count exceedance is different from queueing delay or exceeding queue capacity.
---

## Capacity planning

Requests arrive at an average of 5 per second, so the count in one second is modelled as Poisson with mean 5. Compare that count with a nominal capacity of 9 requests per second. How often does a one-second arrival count exceed 9? Add the probabilities of 0 to 9 and subtract from 1:

```formula
P(X ≥ 10)
  = 1 − Σ_{k=0}^{9} (λ^k e^{−λ}) / k!
P(X ≥ 10) ≈ 0.0318   for λ = 5
where
X: the number of requests arriving in one second
P: probability; probabilities are dimensionless and apply to measurable events
λ: lambda, the expected count in the one-second window, 5; a dimensionless count
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
# Sum counts within the nine-request limit.
p_ok = sum(poisson_pmf(k, lam)
           for k in range(10))
print(round(1 - p_ok, 4))  # 0.0318
```

The direct PMF calculation is a small-parameter demonstration; large arguments can exceed the floating-point range or lose precision. Use a numerical distribution library for general calculations.

About 3.2% of one-second windows see 10 or more requests: about 0.0318 × 60 ≈ 1.91 such windows per minute in expectation. A threshold of 12 is exceeded (13 or more arrivals) with probability about 0.202%, still above 0.1%. A threshold of 13 is exceeded (14 or more) with probability about 0.0698%. These are arrival-count probabilities, not probabilities that a queue fills up or that latency is high: buffering, existing backlog and service times also matter.

## Useful properties

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
Expectations: all displayed expectations are finite; an expectation has the units of the quantity averaged
In words: merging independent streams adds their means; randomly keeping a fraction q of events scales the mean by q; and at 5 events per second the average gap is 1/5 = 0.2 s.
```

## Key takeaways
- Arrival-count exceedance is different from queueing delay or exceeding queue capacity.
- Superposition requires independent Poisson processes; thinning uses independent labels.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
