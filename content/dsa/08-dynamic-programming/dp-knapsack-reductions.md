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

- **Target sum** ("assign + or − to each number to reach T"): it turns into subset counting for nonnegative integer inputs. The numbers given a plus sign form one group; everything else is subtracted. Fixing the plus group's sum fixes the whole expression, so the plus group must sum to exactly half of (the total + the target):

```formula reference
P − (S − P) = T
P = (S + T) / 2
where
P: the sum of the numbers given a + sign
S: the sum of all the numbers
S − P: the sum of the numbers given a − sign
T: the target the signed numbers must add up to
In words: the plus group's sum minus the minus group's sum must equal the target, which fixes the plus group's sum at half of (the total of all the numbers + the target), so count the subsets with that sum.
```

For five ones with target three, the plus group must sum to 4: count the subsets of sum 4, of which there are 5 (choose which four 1s are positive). Equal-valued positions still count as distinct.

Two checks come first. If the target is further from zero than the total, no assignment can reach it. And if the total plus the target is odd, the plus group would need a fractional sum, so no assignment exists. Skipping that parity check is a real bug: integer division silently rounds the half down, and the code counts subsets for the wrong target.

- **Last stone weight II**: minimum-difference partition.
- **Ones and zeroes**: knapsack with a two-dimensional budget (count of 0s and 1s), state `dp[zeros][ones]`.

## Key takeaways
- A subset choice under an additive budget often has a knapsack state.
- Target sum becomes subset counting with a parity and range check.
- Equal-valued input positions remain distinct choices.

## Further reading
- [Knapsack recurrences](https://cp-algorithms.com/dynamic_programming/knapsack.html)
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
