---
id: dp-knapsack-reductions
title: Recognise budgets and signed-sum reductions
level: intermediate
minutes: 2
summary: A subset choice under an additive budget often has a knapsack state.
sourceLesson: dp-knapsack
---

## Recognising knapsack

Ask: "Am I choosing a **subset** of items, subject to a **budget** on some additive quantity, while optimising or counting another additive quantity?" If so, the state is (items considered, budget used), and it's knapsack. Examples:

- **Target sum** ("assign + or − to each number to reach T"): it turns into subset counting for nonnegative integer inputs.

```formula
P − (S − P) = T
P = (S + T) / 2
P = (5 + 3) / 2 = 4
where
P: the sum of the numbers given a + sign
S: the sum of all the numbers
S − P: the sum of the numbers given a − sign
T: the target the signed numbers must add up to
In words: the plus group minus the minus group must equal T, which fixes the plus group's sum at half of S + T, so count the subsets with that sum.
```

The example is five ones with target three: count the subsets of sum 4, of which there are 5 (choose which four 1s are positive). The reduction needs a valid integer subset target:

```formula
|T| ≤ S
(S + T) mod 2 = 0
where
T: the signed-sum target
S: the total of the nonnegative input numbers
|T|: the absolute value of T, ignoring its sign
mod: the remainder after integer division
≤: less than or equal to
In words: The target must be within the total’s positive and negative range, and the required subset sum must be an integer.
```

If either check fails, no assignment exists; equal-valued positions still count as distinct.

- **Last stone weight II**: minimum-difference partition.
- **Ones and zeroes**: knapsack with a two-dimensional budget (count of 0s and 1s), state `dp[zeros][ones]`.

## Key takeaways
- A subset choice under an additive budget often has a knapsack state.
- Target sum becomes subset counting with a parity and range check.
- Equal-valued input positions remain distinct choices.

## Further reading
- [Knapsack recurrences](https://cp-algorithms.com/dynamic_programming/knapsack.html)
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
