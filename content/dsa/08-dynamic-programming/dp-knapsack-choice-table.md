---
id: dp-knapsack-choice-table
title: Indivisible items and the knapsack table
level: intermediate
minutes: 4
summary: Ratio-based greedy solves fractional knapsack but can fail for whole items.
sourceLesson: dp-knapsack
---

You have a bag that holds weight W and a set of items, each with a weight and a value. Which items should you pack to maximise the total value?

That's the **knapsack problem**, and a surprising number of real problems are knapsack in disguise: choosing which features fit in a sprint, which ads fill a slot, which jobs fit on a machine, which files fit on a disk, how to split a bill evenly. Learn this family well and you'll recognise it everywhere.

## Why greedy fails

The obvious greedy is "take items in order of value per unit weight". With a weight limit of 7 kg and items:

| Item | Weight | Value | Value/kg |
|---|---|---|---|
| A | 1 | 1 | 1.00 |
| B | 3 | 4 | 1.33 |
| C | 4 | 5 | 1.25 |
| D | 5 | 7 | 1.40 |

Greedy takes D (5 kg, value 7), then B doesn't fit, C doesn't fit, takes A: total 8 for 6 kg. The optimum is B + C: 7 kg, value **9**.

Greedy *is* optimal for the **fractional knapsack**, where you can take part of an item (gold dust rather than gold bars). For indivisible items this greedy rule is not generally exact; DP is one option alongside exhaustive search, branch and bound and other methods.

## 0/1 knapsack

Each item can be taken at most once. The code assumes positive integer weights, nonnegative integer values and a nonnegative integer weight limit; choosing nothing is allowed.

**State**: `K[i][c]` records best value using only the first i items with weight limit c.

**Recurrence**: decide about item i (weight `w`, value `v`).

- Skip it: `K[i-1][c]`.
- Take it, if it fits: `K[i-1][c-w] + v`.

```formula
K[i][c] = K[i − 1][c]   if w_i > c
K[i][c] = max(K[i − 1][c],
  K[i − 1][c − w_i] + v_i)   if w_i ≤ c
K[0][c] = 0
where
K[i][c]: the best total value achievable using only the first i items with a weight limit of c
i: how many items have been considered, 0 to n; the item-reading recurrence applies only when at least one item is considered
n: the number of items
c: the remaining capacity, a whole number of weight units (kg here) from 0 to W
W: the bag's capacity
w_i: the weight of item i, in the same units as c
v_i: the value of item i
max: the larger of the two options
In words: either skip item i and keep the best for the earlier items, or, if it fits, take it, gaining its value but losing its weight from the capacity.
```

No items give zero value. With the items above:

```formula
K[3][7] = max(K[2][7], K[2][3] + 5)
K[3][7] = max(5, 4 + 5) = 9
where
K[i][c]: the best value using the first i items within capacity c
i: the number of items considered
c: the capacity in whole kilograms
max: the larger value
In words: Adding item C to the best earlier three-kilogram packing beats skipping it.
```

For the items above (rows count considered items; columns give weight limits zero through seven):

```
cap     0  1  2  3  4  5  6  7
none    0  0  0  0  0  0  0  0
+A      0  1  1  1  1  1  1  1
+B      0  1  1  4  5  5  5  5
+C      0  1  1  4  5  6  6  9
+D      0  1  1  4  5  7  8  9
```

Answer `K[4][7] = 9`.

**Reconstruction**: walk up from `K[n][W]`. If `K[i][c] != K[i-1][c]`, item i was taken; subtract its weight. Here, at capacity 7, rows D and C both give 9, so skip D. Row C improves the previous value from 5 to 9, so take C and leave capacity 3. Row B improves the previous value from 1 to 4 there, so take B and leave capacity zero. Result {B, C}.

## Key takeaways
- Ratio-based greedy solves fractional knapsack but can fail for whole items.
- A state records items considered and the remaining weight limit.
- Compare skipping an item with taking it once.

## Further reading
- [Knapsack recurrences](https://cp-algorithms.com/dynamic_programming/knapsack.html)
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
