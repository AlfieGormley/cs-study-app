---
id: prob-variance-linearity
title: Separate spread from linearity
level: intermediate
minutes: 4
sourceLesson: prob-expectation
summary: Variance measures squared spread; standard deviation uses the original units.
---

## Variance

For a variable with a finite **second moment** (finite expected square), the mean says where values centre; **variance** says how spread out they are. It is the average squared distance from the mean, and the **standard deviation** is its square root, which is back in the original units.

```formula
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

For one fair die:

```formula
E[X^2] = (1 + 4 + 9 + 16 + 25 + 36) / 6
E[X^2] = 91/6
Var(X) = 91/6 − 3.5^2 = 91/6 − 49/4
Var(X) = 35/12 ≈ 2.92
σ = √(35/12) ≈ 1.71
where
X: the number shown by one fair die
E[X^2]: the average of the squared face values
3.5: the mean roll, E[X]
Var(X): the variance of the roll
σ: sigma, the standard deviation of the roll
√: the square root
≈: approximately equal to
Expectations: all displayed expectations are finite; an expectation has the units of the quantity averaged
Moments: variables in these variance or covariance expressions have finite second moments
In words: the root-mean-square distance of a die roll from its mean is about 1.7.
```

Two systems with the same mean latency can feel completely different if one has much higher variance. Engineers care about the spread as much as the centre (later units return to this with percentiles).

## Linearity of expectation

For random variables X and Y with finite absolute expectations, and constants a and b:

```formula
E[X + Y] = E[X] + E[Y]
E[a × X + b] = a × E[X] + b
where
X, Y: any two random variables, dependent or not
E[ ]: expected value
a, b: fixed numbers (constants), not random
Expectations: all displayed expectations are finite; an expectation has the units of the quantity averaged
In words: the average of a sum is the sum of the averages, and scaling or shifting a variable scales or shifts its average the same way.
```

The crucial point: **this holds even when X and Y are dependent.** No independence assumption is needed. That is what makes it so powerful: you can break a complicated count into simple pieces, find each piece's expectation separately, and add, without ever working out how the pieces interact.

For example, the sum of two dice has expectation 3.5 + 3.5 = 7, and twice one die plus 1 has expectation 2 × 3.5 + 1 = 8.

> [!warning] What does NOT hold in general
> Products, sums of variances and non-linear functions do not behave like linearity. The three rules below are the true versions.

```formula
E[X × Y] = E[X] × E[Y]   if Cov(X, Y) = 0
Var(X + Y) = Var(X) + Var(Y)
  + 2 × Cov(X, Y)
E[X^2] ≥ (E[X])^2
where
X, Y: random variables with finite second moments
E[ ]: expected value
Var( ): variance, the average squared distance from the mean
Cov(X, Y): the **covariance** of X and Y, E[X × Y] − E[X] × E[Y]; positive when they tend to move together, 0 when **uncorrelated**
≥: greater than or equal to
Expectations: all displayed expectations are finite; an expectation has the units of the quantity averaged
Moments: variables in these variance or covariance expressions have finite second moments
In words: the mean of a product splits only when the covariance is zero (independence is enough but not necessary); variances add only when the covariance is zero; and the mean of a square is at least the square of the mean, which is why variance is never negative.
```

More generally, the expectation of a non-linear function of X need not equal that function of the expectation, though it can in particular cases. The later transfer-time example shows the cost.

## Key takeaways
- Variance measures squared spread; standard deviation uses the original units.
- Linearity of expectation needs no independence.
- Variance sums and product means require additional covariance conditions.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
