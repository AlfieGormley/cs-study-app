---
id: prob-ab-hypothesis-tests
title: Interpret an A/B hypothesis test
level: advanced
minutes: 4
sourceLesson: prob-statistics
summary: A p-value conditions on the null model rather than assigning it a posterior probability.
---

## A/B testing

An A/B test randomly splits users between a control (A) and a variant (B) and compares a metric. Randomisation is what makes it work: it balances every other factor, known or unknown, between the groups in expectation.

## Hypothesis testing in one page

1. **Null hypothesis**: the variant has no effect.
2. Compute a **test statistic** measuring how far the observed difference is from zero, in standard errors.
3. The **p-value** is the probability, under the null hypothesis and the assumed sampling model, of a test statistic at least as extreme as observed in the pre-specified direction or directions.
4. If the p-value is below a threshold chosen in advance (the **significance level**, usually 0.05), call the result **statistically significant**.

Two kinds of error:

| | No real effect | Real effect |
|---|---|---|
| Significant | **Type I error** (false positive) | correct (power) |
| Not significant | correct | **Type II error** (false negative) |

The actual error probabilities have standard symbols. The notation below treats the null and the stated alternative as sampling models; they are not random hypotheses with assigned prior probabilities.

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
P: probability; probabilities are dimensionless and apply to measurable events
α: alpha, the actual Type I false positive probability under the specified null model; an ideal test calibrated at 0.05 has this value
β: beta, the Type II (false negative) rate for an effect of the stated size
Pow: the **statistical power**, the chance of detecting a real effect of that size
Conditioning: every event to the right of a given bar in this card has positive probability
In words: α is how often you cry wolf when nothing changed; β is how often you miss a real change; power is one minus β.
```

A test’s nominal significance level is its intended upper bound on the Type I probability, rather than an automatic equality. Discrete tests can be conservative, and approximate tests can miss that target when their assumptions fail. An 80% power target is a common design choice, not a universal requirement.

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
    # The null assumes one shared rate.
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

A p-value of 0.021 does **not** mean "there is a 2.1% chance B is no better". It is the chance of data this extreme given no effect, not the chance of no effect given the data. That is the Bayes inversion from the earlier Bayesian update again.

## Key takeaways
- A p-value conditions on the null model rather than assigning it a posterior probability.
- Power is tied to a specified alternative effect size.

## Further reading
- [Engineering Statistics Handbook — NIST](https://www.itl.nist.gov/div898/handbook/)
