---
id: prob-quicksort-comparison-proof
title: Prove expected quicksort comparisons
level: advanced
minutes: 4
sourceLesson: prob-algorithms
summary: A pair is compared when an endpoint is the first pivot in its rank interval.
---

## Quicksort with uniform random pivots

Quicksort picks a pivot, partitions the array into smaller and larger elements, and recurses. With a fixed pivot (say the first element), a sorted input of n elements gives the maximum-comparison case: every partition peels off one element, as shown by this count:

```formula
Q_w = (n(n − 1)) / 2
Q_w = (1000 × 999) / 2 = 499,500
where
Q_w: the maximum number of pivot comparisons
n: the positive integer number of distinct elements; 1,000 in the example
In words: peeling off one element per partition compares every unordered pair once.
```

 Sorted and nearly sorted inputs are common in practice, so this matters.

For distinct keys, standard pivot partitioning that compares the pivot once with every other element, and fresh independent uniform pivots, the comparison-count distribution does not depend on the initial order. The expected comparison count grows on the order of the input length times its logarithm, for every fixed distinct-key input. The exact formula and its leading-term approximation are derived below.

## The indicator proof

Name the elements in sorted order, smallest first. Every comparison is between a pivot and another element, and each pair is compared no more than once (after partitioning, the pivot is never touched again). So the number of comparisons is a sum of indicators, one per pair.

Take the i-th smallest and the j-th smallest elements, and the block of sorted elements from one to the other. They stay together in one subarray until one element of that block is chosen as a pivot:

- If the first pivot chosen from the block is one of the two ends, the pair is compared.
- If it is anything in between, the two are split into different sides and never compared.

Each element of the block is equally likely to be first, so:

```formula
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

By linearity, summing over all pairs:

```formula
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
In words: close pairs are compared often and distant pairs rarely; adding up all pairs gives about 2 n ln(n) comparisons.
```

For n = 1,000:

```formula
E[Q] = 2 × 1001 × H_1000 − 4000
E[Q] ≈ 2002 × 7.485471 − 4000
E[Q] ≈ 10,986
where
E[Q]: the expected number of pivot comparisons for 1,000 distinct totally ordered elements under fresh independent uniform pivots
H_1000: the 1,000th harmonic number, about 7.485
≈: approximately equal to
Expectations: all displayed expectations are finite; an expectation has the units of the quantity averaged
In words: quicksort with uniform random pivots makes about 11,000 comparisons on 1,000 elements, against 499,500 in the maximum-comparison case.
```

That is about 11,000 comparisons, versus 499,500 in the maximum-comparison case. The next unit checks this mean against sampled executions.

```formula
2n ln(n) ≈ 1.39n log_2(n)
where
n: the integer input length, greater than 1
ln: the natural logarithm, to base Euler’s number
log_2: the base-two logarithm
≈: approximately equal to, from rounding twice the natural logarithm of 2
In words: changing logarithm base gives the same leading comparison count with a different constant factor.
```

## Key takeaways
- A pair is compared when an endpoint is the first pivot in its rank interval.
- Summing indicator expectations gives the exact harmonic-number formula.
- The expectation uses distinct keys and fresh independent uniform pivots.

## Further reading
- [Mathematics for Computer Science — MIT](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-fall-2010/)
