---
id: cx-operation-budgets
sourceLesson: cx-in-practice
title: Estimating a feasible input budget
level: advanced
minutes: 4
summary: Use an explicitly assumed operation rate to screen algorithm choices.
---

Asymptotic analysis is a model. It is an excellent one, and for large enough inputs it predicts the winner. But it deliberately throws away information: constant factors, the memory hierarchy, the language runtime, and what your inputs actually look like. Experts know both the model and where it leaks.

This lesson is about using complexity as an engineering tool rather than an exam answer.

## What fits in one second

The most practical skill is estimating from the input size n which complexity you can afford. For the arithmetic exercise below, **assume 10^8 counted operations per second** and unit leading constants. This is a hypothetical model, not measured throughput or a guarantee for any language. The estimate is one division:

```formula
t = W(n) / r
where
t: the estimated running time, in seconds (s)
W(n): the number of operations the algorithm does on input size n, read off its complexity with the constant taken as 1 (for example n^2 for a quadratic algorithm)
n: the input size
r: the assumed speed, 10^8 (a hundred million) operations per second
In words: divide the operation count by the speed; anything that comes out near 1 second or less fits the budget.
```

In the table, n! is n factorial (n × (n − 1) × … × 1), 2^n is n copies of 2 multiplied together, and log n is the base-2 logarithm of n:

| Largest n (about 1 s) | Affordable complexity |
|---|---|
| 10 to 11 | O(n!) |
| 20 to 25 | O(2^n) |
| ~500 | O(n^3) |
| ~5,000 to 10,000 | O(n^2) |
| ~10^6 | O(n log n) |
| ~10^8 | O(n) |
| large n, subject to constants and storage | O(log n), O(1) |

The table comes straight from the arithmetic:

```formula
11! ≈ 4 × 10^7
2^25 ≈ 3.4 × 10^7
500^3 = 1.25 × 10^8
(10^4)^2 = 10^8
10^6 × log_2(10^6) ≈ 2 × 10^7
where
11!: 11 factorial, 11 × 10 × … × 1 = 39,916,800
2^25: 25 copies of 2 multiplied together, 33,554,432
500^3: 500 × 500 × 500
log_2(10^6): the base-2 logarithm of a million, about 19.9
≈: approximately equal to
In words: at each table row's largest n, the operation count comes out at about 10^7 to 10^8, which is about a second or less at 10^8 operations per second.
```

Read it backwards too. If a problem says n is up to 200,000, a quadratic algorithm needs about 200,000 × 200,000 = 4 × 10^10 operations, 400 seconds at the assumed rate (minutes rather than a second), so you need O(n log n) or better. If n is at most 20, exponential brute force over subsets may be the simplest correct answer.

> [!note] Content gap: cross-language timings
> A reproducible benchmark for the claimed universal Python-to-compiled speed ratio is absent, so that ratio is omitted. Interpreter version, operation type, data and hardware matter. Native built-ins or vectorisation can reduce interpreter overhead; measure the actual workload.

## Key takeaways
- An operation budget is useful only with a stated rate and cost model.
- Large quadratic counts can rule out an approach before implementation.
- Small inputs can make exhaustive search a sensible starting point.

## Further reading
- [Time complexity guide — USACO Guide](https://usaco.guide/bronze/time-comp)
