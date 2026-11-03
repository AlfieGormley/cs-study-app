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

Interview and contest problems state limits on input size, for example "the array has between 1 and 100,000 elements". That is a heavy hint about which growth rates are worth trying. It is only a hint: whether an approach is fast enough also depends on the algorithm's constants, operation types, numeric sizes, memory, hardware and deadline.

The Complexity Analysis module covers Big-O and the common growth rates ("Comparing growth rates") and how to turn an assumed operation rate into a budget ("Estimating a feasible input budget"). Two rates matter most for spotting brute force here:

- **n!** (n factorial) counts the possible *orders* of n items. It grows fastest of all: 10 items already have over 3.6 million orders.
- **2ⁿ** counts the possible *subsets* of n items, because each item is either in or out. Every extra item doubles it: 20 items have about a million subsets.

The table lists growth rates to investigate for illustrative input sizes, not guaranteed feasible limits.

| Example n | Growth to investigate | Candidate technique |
|---|---|---|
| ≤ 10 | O(n!) | Permutations |
| ≤ 20 | O(2ⁿ) | Subsets, bitmasks |
| ≤ 500 | O(n³) | Triple loop, DP |
| ≤ 5,000 | O(n²) | Pairs, 2-D DP |
| ≤ 10⁶ | O(n log n) | Sort, heap |
| > 10⁶ | O(n), O(log n) | One pass, math |

Read the table as a prediction about scaling. At 100,000 elements, a quadratic algorithm faces about 10 billion units of work (100,000 squared), while an n log n algorithm faces about 1.7 million (the base-2 logarithm of 100,000 is about 17), roughly 6,000 times less. The more useful habit is to ask what happens when n grows: multiplying n by 10 multiplies quadratic work by 100, but n log n work by only about 12 when going from 100,000 to a million elements (ten times as many elements, with a base-2 logarithm of about 20 instead of about 17).

These are growth expressions, not exact operation counts. Compare them with the actual resource budget before choosing.

## Key takeaways
- Compare candidate growth expressions at the largest permitted input.
- Factorial counts orderings; powers of two count subsets.
- Big-O expressions are not exact instruction counts or promises about runtime.

## Further reading
- [Coding interview techniques — Tech Interview Handbook](https://www.techinterviewhandbook.org/coding-interview-techniques/)
- [Coding interview cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/coding-interview-cheatsheet/)
- [How to Solve It (Pólya) — Wikipedia](https://en.wikipedia.org/wiki/How_to_Solve_It)
- [Time complexity — Wikipedia](https://en.wikipedia.org/wiki/Time_complexity)
