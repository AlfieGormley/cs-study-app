---
id: prob-quicksort-comparison-proof
title: Prove expected quicksort comparisons
level: advanced
minutes: 3
sourceLesson: prob-algorithms
summary: A pair is compared when an endpoint is the first pivot in its rank interval.
---

Random pivots protect quicksort's expected comparison count against a fixed bad input order. They do not remove unlucky executions. The reason becomes clear by following one pair of values.

## Specify the comparison model

Assume distinct totally ordered keys, fresh independent uniform pivots, and one comparison between each pivot and every other element in its partition. The input is fixed independently of those choices.

A first-element pivot on sorted input repeatedly removes only one element, giving quadratic work. A uniform pivot can occupy any rank, so sorted input has the same comparison-count distribution as any other fixed ordering of distinct keys.

## Follow a pair through the partitions

Consider two values and all values between them in sorted order. Pivots outside this interval leave the pair together. The first pivot chosen from within the interval determines whether they ever meet:

- An endpoint pivot is compared with the other endpoint.
- An interior pivot separates the endpoints into different recursive calls, so they never meet.

```formula essential
P(X_ij = 1) = 2 / (j − i + 1)
where
z_1 < z_2 < … < z_n: the n elements in sorted order
i, j: integer ranks from one through n, with i < j; pivots are fresh independent uniform choices
X_ij: the indicator that z_i and z_j are ever compared: 1 if so, 0 if not
j − i + 1: the number of elements in the block from z_i to z_j
2: the two "good" first pivots, z_i or z_j
P: probability; probabilities are dimensionless and apply to measurable events
In words: two elements are compared only if one of them is the first pivot picked from the block between them, a chance of 2 divided by the number of elements in the block.
```

Every element in the interval is equally likely to be that first pivot. There are exactly two favourable endpoints. Nearby ranks are therefore more likely to be compared than distant ranks.

## Turn pairs into total work

Each pair is compared at most once because a pivot is excluded from later recursive calls. Give each pair an indicator and add its comparison probability. Linearity requires no independence between the indicators.

```formula reference
E[Q] = Σ_{i<j} 2 / (j − i + 1)
E[Q] = 2 × (n + 1) × H_n − 4 × n
E[Q] ≈ 2 × n × ln(n)
where
Q: the total number of comparisons
E[Q]: its expected value
n: the positive integer number of distinct totally ordered elements, with fresh independent uniform pivots and one comparison per pivot-other-element pair
i, j: integer ranks from one through n, with i less than j
Σ_{i<j}: sigma, "add up over every pair with i less than j"
H_n: the n-th harmonic number, 1 + 1/2 + … + 1/n
ln(n): the natural logarithm of n (base e ≈ 2.718)
≈: approximately equal to (for large n)
Expectations: all displayed expectations are finite; an expectation has the units of the quantity averaged
In words: nearby ranks are compared more often than distant ranks. Adding every pair's comparison probability gives an expected total growing as input length times its logarithm.
```

The expected count grows as input length times its logarithm. A particular pivot sequence can still give quadratic work. Duplicates, adaptive comparisons or predictable pivot choices need their own analysis rather than inheriting this guarantee automatically.

## Key takeaways
- The first pivot within a rank interval decides whether its endpoints meet.
- Pair indicators turn local probabilities into expected total work.
- The expectation is over pivots for every fixed distinct-key input.

## Further reading
- [Quicksort and indicator analysis — MIT lecture notes](https://ocw.mit.edu/courses/18-310-principles-of-discrete-applied-mathematics-fall-2013/7db820f51ad2de2340639a7ea14b7795_MIT18_310F13_Ch12.pdf)
- [Mathematics for Computer Science — MIT](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-fall-2010/)
