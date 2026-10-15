---
id: pat-input-growth
title: Compare growth against input constraints
level: basic
minutes: 4
sourceLesson: pat-approach
summary: Compare candidate growth expressions at the largest permitted input.
---

Input limits tell you which growth expressions deserve investigation. Here n is the number of input elements; constants, memory and the deadline still matter.

## Let the constraints choose the complexity

Interview and contest problems specify limits on input size. For example, an array may contain between one and one hundred thousand elements:

```formula
1 ≤ n ≤ 10^5
where
n: the number of elements in the input; its upper limit 10^5 is ten to the power 5, a 1 followed by five zeros: 100,000
≤: "is less than or equal to"
In words: the input holds at least one element and at most 100,000 of them.
```

That is a heavy hint. Input size helps compare growth, but whether an approach is fast enough also depends on the algorithm’s constants, operation types, numeric sizes, memory, hardware and deadline.

> [!note] Content gap
> Generic C++/Python operations-per-second figures and universal pass/fail thresholds are omitted because no pinned benchmark or judge configuration establishes them.

The table uses a few growth expressions you may not have met. Each one describes how the work grows with n:

```formula
n! = n × (n − 1) × … × 2 × 1
2^n = 2 × 2 × … × 2
4! = 4 × 3 × 2 × 1 = 24
2^4 = 2 × 2 × 2 × 2 = 16
where
n: the number of elements in the input
n!: "n factorial", the number of different orders (permutations) of n distinct items
2^n: n copies of 2 multiplied together, the number of subsets of n items (each item is either in or out)
…: "and so on", continuing the same pattern
In words: factorial counts orderings and grows fastest of all; 2^n counts in-or-out choices and doubles with every extra item.
```

For zero items there is one empty ordering and one empty subset. The factorial product displayed above uses the usual continuation pattern for at least two items; its zero-input value is defined as one.

The table also uses Big-O notation: O(f(n)) supplies an asymptotic upper bound, up to a constant factor, for a nonnegative cost function f(n). It need not be tight or count exact operations. A base-2 logarithm measures the exponent needed to produce its argument; for 100,000 it is about 16.6. The whole number of successive halvings needed to reach one or less is 17.

The table lists growth expressions to investigate for illustrative input sizes, not guaranteed feasible limits.

| Example n | Growth to investigate | Candidate technique |
|---|---|---|
| ≤ 10 | O(n!) | Permutations |
| ≤ 20 | O(2ⁿ) | Subsets, bitmasks |
| ≤ 500 | O(n³) | Triple loop, DP |
| ≤ 5,000 | O(n²) | Pairs, 2-D DP |
| ≤ 10⁶ | O(n log n) | Sort, heap |
| > 10⁶ | O(n), O(log n) | One pass, math |

Plugging the largest allowed n into two of these expressions shows the gap:

```formula
n^2 = (10^5)^2 = 10^10
n log_2(n) = 10^5 × log_2(10^5)
n log_2(n) ≈ 10^5 × 16.6
n log_2(n) ≈ 1.66 × 10^6
where
n: the number of elements in the input; here 10^5 = 100,000
n^2: n squared, n × n
log_2: the base-2 logarithm: log_2(n) is the power you raise 2 to in order to get n, so log_2(1024) = 10
≈: approximately equal to (the result is rounded)
In words: a quadratic algorithm faces about 10 billion units of work at 100,000 elements, while an n log n algorithm faces about 1.7 million, roughly 6,000 times less.
```

These are work expressions, not exact operation counts inferred from big-O. Compare them with the actual resource budget before choosing.

## Key takeaways
- Compare candidate growth expressions at the largest permitted input.
- Factorial counts orderings; powers of two count subsets.
- Big-O expressions are not exact instruction counts or promises about runtime.

## Further reading
- [Coding interview techniques — Tech Interview Handbook](https://www.techinterviewhandbook.org/coding-interview-techniques/)
- [Coding interview cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/coding-interview-cheatsheet/)
- [How to Solve It (Pólya) — Wikipedia](https://en.wikipedia.org/wiki/How_to_Solve_It)
- [Time complexity — Wikipedia](https://en.wikipedia.org/wiki/Time_complexity)
