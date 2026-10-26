---
id: prob-variance-linearity
title: Separate spread from linearity
level: intermediate
minutes: 3
sourceLesson: prob-expectation
summary: Variance measures squared spread; standard deviation uses the original units.
---

Two services can have the same mean latency but very different consistency. **Variance** measures average squared distance from the mean; **standard deviation** is its square root and uses the original units. Latency variance is in squared time units, while latency standard deviation is a time.

## Spread differs from uncertainty about a mean

Variance describes the distribution of individual values. A finite second moment, meaning a finite expected square, ensures finite variance. The mean alone does not tell you whether delays are consistent or highly variable.

```formula reference
Var(X) = E[(X − μ)^2]
Var(X) = E[X^2] − μ^2
σ = √(Var(X))
where
X: a random variable
μ: mu, the mean of X, the same as E[X]
E[ ]: expected value, the probability-weighted average of whatever is inside the brackets
E[X^2]: the expectation of the square of X, not the square of its expectation
Var(X): the variance of X, in the units of X squared
σ: sigma, the standard deviation of X, in the same units as X
√: the square root
Expectations: all displayed expectations are finite; an expectation has the units of the quantity averaged
Moments: variables in these variance or covariance expressions have finite second moments
In words: variance is the average squared distance from the mean, which also equals the mean of the square minus the square of the mean; its square root is the standard deviation.
```

## Means add even when values move together

For variables with finite absolute expectations, **linearity of expectation** says the expected total is the sum of the expected parts. Scaling or shifting a quantity scales or shifts its expectation too.

```formula essential
E[X + Y] = E[X] + E[Y]
E[a × X + b] = a × E[X] + b
where
X, Y: any two random variables, dependent or not
E[ ]: expected value
a, b: fixed numbers (constants), not random
Expectations: all displayed expectations are finite; an expectation has the units of the quantity averaged
In words: the average of a sum is the sum of the averages, and scaling or shifting a variable scales or shifts its average the same way.
```

No independence is needed. Correlated request counts can still be added to obtain the expected total. This lets us count many small events without deriving the full distribution of their total.

## Do not extend linearity to everything

Variances do not generally add: positive covariance adds spread to a sum, while negative covariance can reduce it. With finite second moments, zero covariance makes the variance of a sum equal the sum of variances and makes the mean of a product equal the product of means. Independence implies zero covariance in this setting; the converse need not hold.

Likewise, averaging after squaring is not generally the same as squaring the average. They agree only when the variable is constant with probability one. For non-linear transformations, reason about the transformed outcomes before taking their average.

## Key takeaways
- Standard deviation uses the original units; variance uses squared units.
- Finite means add regardless of dependence.
- Products, variances and non-linear transformations need separate reasoning.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
