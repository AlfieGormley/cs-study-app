---
id: prob-binomial-counts
title: Model fixed trials with the binomial
level: intermediate
minutes: 4
sourceLesson: prob-distributions
summary: A binomial count needs independent trials with one fixed probability.
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
P: probability of measurable events, dimensionless and between zero and one
X: the number of successes, a whole number from 0 to n
~: "is distributed as", "has the distribution"
Bin(n, p): the binomial distribution with n trials and success probability p
n: the nonnegative integer number of trials
p: the common trial success probability, between 0 and 1; use the displayed mass formula away from the endpoints
k: a particular number of successes we ask about, 0 to n
P(X = k): the probability of exactly k successes
C(n, k): "n choose k", the number of ways to pick which k of the n trials succeed
!: factorial; n! = n × (n − 1) × … × 2 × 1, and 0! = 1
p^k: k copies of p multiplied together, the chance that k chosen trials all succeed
(1 − p)^{n − k}: the chance that the other n − k trials all fail
E[X]: the expected (mean) number of successes
Var(X): the variance of the number of successes
Expectations: all displayed expectations are finite; an expectation has the units of the quantity averaged
Moments: variables in these variance or covariance expressions have finite second moments
In words: count the arrangements with exactly k successes, times the probability of any one arrangement; on average you get n × p successes.
```

At probability zero all trials fail; at probability one all succeed. Those degenerate endpoint cases avoid ambiguous zero-to-zero powers in the mass formula.

For 10 independent fair coin tosses:

```formula
P(X = 3) = C(10, 3)(0.5)^10
P(X = 3) = 120/1024 ≈ 0.117
E[X] = 5
where
X: the number of heads in 10 independent fair tosses
P: probability; probabilities are dimensionless and apply to measurable events
C(10, 3): the 120 ways to choose the three head positions
E[X]: the expected number of heads
≈: approximately equal to
Expectations: all displayed expectations are finite; an expectation has the units of the quantity averaged
In words: exactly three heads has about an 11.7% chance, while the average number of heads is five.
```

> [!example] Packet loss
> A link drops each packet independently with probability 1%. You send 100 packets, so the number lost is binomial with 100 trials and probability 0.01.

```formula
P(L = 0) = 0.99^100 ≈ 0.366
P(L = 1) = 100 × 0.01 × 0.99^99 ≈ 0.370
P(L ≥ 2) ≈ 1 − 0.366 − 0.370 = 0.264
where
P: probability of measurable events, dimensionless and between zero and one
L: the number of packets lost out of 100
P(L = 0): the probability that none is lost
0.99: the chance one packet gets through
0.99^100: 100 copies of 0.99 multiplied together, one factor per packet
100: C(100, 1), the number of ways to choose which single packet is lost
0.01: the chance one packet is lost (1%)
≥: greater than or equal to
≈: approximately equal to
In words: a clean transfer happens only about 37% of the time, exactly one loss about 37%, and two or more about 26%.
```

Even at 1% loss, a 100-packet transfer suffers at least one loss nearly two times in three. That is why **TCP** (the Transmission Control Protocol, the internet's reliable-delivery protocol) needs retransmission to be cheap.

## Key takeaways
- A binomial count needs independent trials with one fixed probability.
- Choose successful positions and multiply one arrangement probability.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
