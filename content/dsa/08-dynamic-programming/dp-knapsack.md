---
id: dp-knapsack
title: The knapsack family
level: intermediate
minutes: 18
summary: 0/1 and unbounded knapsack, subset sum and partition, why the loop direction matters, and why the table of items by weight limit is pseudo-polynomial rather than polynomial.
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

**State**: `K[i][c]` = best value using only the first i items with weight limit c.

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
i: how many items have been considered, 0 to n
n: the number of items
c: the remaining capacity, a whole number of weight units (kg here) from 0 to W
W: the bag's capacity
w_i: the weight of item i, in the same units as c
v_i: the value of item i
max: the larger of the two options
In words: either skip item i and keep the best for the earlier items, or, if it fits, take it, gaining its value but losing its weight from the capacity.
```

**Base**: `K[0][c] = 0` (no items, no value). For example, with the items above, K[3][7] = max(K[2][7], K[2][3] + 5) = max(5, 4 + 5) = 9: adding C (4 kg, value 5) to the best 3 kg packing from A and B.

For the items above (rows = items considered, columns = weight limit 0..7):

```
cap     0  1  2  3  4  5  6  7
none    0  0  0  0  0  0  0  0
+A      0  1  1  1  1  1  1  1
+B      0  1  1  4  5  5  5  5
+C      0  1  1  4  5  6  6  9
+D      0  1  1  4  5  7  8  9
```

Answer `K[4][7] = 9`.

**Reconstruction**: walk up from `K[n][W]`. If `K[i][c] != K[i-1][c]`, item i was taken; subtract its weight. Here: row D at c=7 is 9, same as row C, so D not taken. Row C: 9 ≠ 5, so C taken, c = 3. Row B: 4 ≠ 1, so B taken, c = 0. Result {B, C}.

### One row, iterated backwards

Each row only reads the previous row, at the same or a smaller weight limit. So use a single array and loop the weight limit **downwards**:

```python
def knapsack_01(items, W):
    items = tuple(items)
    if (type(W) is not int or W < 0
            or any(type(w) is not int
                   or type(v) is not int
                   or w <= 0 or v < 0
                   for w, v in items)):
        raise ValueError("knapsack domain")
    best = [0] * (W + 1)
    for w, v in items:
        for c in range(W, w - 1, -1):
            best[c] = max(best[c],
                          best[c - w] + v)
    return best[W]
```

Why downwards? When you update `best[c]`, you read `best[c - w]`. Going downwards, `best[c - w]` hasn't been touched yet in this round, so it still holds the "previous row" value: item i hasn't been used. Going upwards, `best[c - w]` may already include item i, so you'd use it twice.

> [!warning] The one-character bug
> Loop direction is the only difference between 0/1 and unbounded knapsack in the 1-D form. With one item of weight 2 and value 3 and weight limit 6, the downward loop gives 3 (one copy), and the upward loop gives 9 (three copies). Get the direction wrong and your 0/1 solution silently becomes unbounded.

## Unbounded knapsack

Unlimited copies of each item. Same array, loop the weight limit **upwards**:

```python
def knapsack_unbounded(items, W):
    items = tuple(items)
    if (type(W) is not int or W < 0
            or any(type(w) is not int
                   or type(v) is not int
                   or w <= 0 or v < 0
                   for w, v in items)):
        raise ValueError("knapsack domain")
    best = [0] * (W + 1)
    for w, v in items:
        for c in range(w, W + 1):
            best[c] = max(best[c],
                          best[c - w] + v)
    return best[W]
```

Now `best[c - w]` may already contain copies of this item, which is exactly what we want. Example: items (3 kg, 4), (4 kg, 5), (5 kg, 6), weight limit 10 kg. 0/1 gives 11 (4 + 5 kg); unbounded gives 13 (3 + 3 + 4 kg).

Coin change from lesson 3 is unbounded knapsack: "minimum coins" is min-count knapsack, "number of ways" is counting knapsack.

**Bounded knapsack** (item i available up to a limited number of times) can be solved by splitting each item into bundles of 1, 2, 4, ... copies, plus a final remainder, so that every count from 0 to the limit is a sum of distinct bundles:

```formula
k_i = 1 + 2 + 4 + ... + 2^{t − 1} + r
bundles = O(log_2(k_i + 1))
k_i = 13 = 1 + 2 + 4 + 6
where
k_i: how many copies of item i are available
t: how many power-of-two bundles fit (1, 2, 4, ... up to 2^{t − 1})
2^{t − 1}: t − 1 copies of 2 multiplied together, the largest power-of-two bundle
r: the remainder bundle, whatever is left after the powers of two (0 up to 2^t − 1)
bundles: the number of 0/1 items produced for item i
log_2(k_i + 1): the base-2 logarithm of k_i + 1, roughly how many times you can halve it
O(...): Big-O, growing at most in proportion to the expression inside
In words: split k_i copies into doubling bundles plus a leftover; any count up to k_i can be made by picking some bundles, and there are only about log_2(k_i) of them.
```

With 13 copies, bundles of 1, 2, 4 and 6 replace 13 separate items with 4; any count from 0 to 13 is a sum of distinct bundles (for example 9 = 1 + 2 + 6). A limit of 0 contributes no items.

## Subset sum

> For nonnegative integer `nums` and target T, is there a subset of positions that sums exactly to T?

It's 0/1 knapsack where each item's value equals its weight and we only ask about feasibility.

```python
def subset_sum(nums, T):
    nums = tuple(nums)
    if (type(T) is not int or T < 0
            or any(type(x) is not int
                   or x < 0 for x in nums)):
        raise ValueError("nonnegative sums")
    can = [True] + [False] * T
    for x in nums:
        for s in range(T, x - 1, -1):
            can[s] = can[s] or can[s - x]
    return can[T]
```

`subset_sum([3, 34, 4, 12, 5, 2], 9)` is True (4 + 5). With T = 30 it's False.

Variants change only the combiner:

- **Count** subsets summing to T: `cnt[s] += cnt[s - x]`, with `cnt[0] = 1`.
- **Minimum items** to reach T: `+∞` sentinel value and `min(..., dp[s - x] + 1)`.

> [!tip] Bitset trick
> A Python integer can encode reachable sums. Start with `mask = 1` and `limit = (1 << (T + 1)) - 1`; for each nonnegative x ≤ T, update `mask = (mask | (mask << x)) & limit`. Skip x > T, then test `(mask >> T) & 1`. Masking bounds retained and temporary lengths by O(T + 1) bits. Without masking, storage instead grows with the sum of all inputs. Packed word operations can improve constants, but a shift is not constant-time on arbitrary-size integers.
>
> Content gap: fixed 64× or Python speedup claims are omitted because no pinned benchmark supports them.

## Partition

> Can `nums` be split into two groups with equal sums?

Let S be the total of all the numbers. If S is odd, no. Otherwise it's subset sum with target S / 2: if one group sums to S / 2, the rest does too.

```python
def can_partition(nums):
    nums = tuple(nums)
    if any(type(x) is not int or x < 0
           for x in nums):
        raise ValueError("nonnegative nums")
    S = sum(nums)
    return S % 2 == 0 and \
        subset_sum(nums, S // 2)
```

`[1, 5, 11, 5]`: S = 22, target 11, and {11} works, so True. `[1, 2, 3, 5]`: S = 11 is odd, so False.

**Minimum difference partition** (split into two groups as evenly as possible): compute all reachable sums up to S / 2 and take the largest one.

```formula
diff = (S − s) − s = S − 2 × s
diff = 22 − 2 × 11 = 0
where
diff: the smallest possible difference between the two groups' sums
S: the total of all the numbers
s: the largest subset sum that is reachable and no more than S / 2
S − s: the sum of the other group
In words: one group gets s and the other gets the rest, so the gap is the total minus twice the smaller group.
```

For [1, 5, 11, 5], S = 22 and s = 11, so the difference is 0. For [1, 2, 3, 5], S = 11, the best s is 5 (5 alone, or 2 + 3), and the difference is 11 − 10 = 1.

## Pseudo-polynomial time

0/1 knapsack takes O(n · W) time, where n is the number of items and W the weight limit. That looks polynomial. It isn't, quite.

Complexity is measured against the **size of the input**: the number of bits needed to write it. The input includes every weight and value as well as W, so their bit lengths all matter. Writing W in binary takes far fewer bits than W itself:

```formula
b = ⌊log_2(W)⌋ + 1
W < 2^b
T = O(n × W) = O(n × 2^b)
where
b: the number of bits needed to write W in binary
W: the capacity, a positive whole number
log_2(W): the base-2 logarithm of W, the power you raise 2 to in order to get W
⌊x⌋: floor, x rounded down to a whole number
2^b: b copies of 2 multiplied together
T: the running time of the table algorithm
n: the number of items
O(...): Big-O, growing at most in proportion to the expression inside
In words: W is about 2 to the power of its bit length, so work proportional to W is exponential in the number of bits used to write it.
```

For W = 1,000: log_2(1,000) ≈ 9.97, so b = 9 + 1 = 10 bits, yet the table has 1,001 columns. O(nW) is therefore not a polynomial bound in the full binary encoding length.

| W | Bits | nW work expression (n = 100) |
|---|---|---|
| 1,000 | 10 | 10⁵ |
| 10⁶ | 20 | 10⁸ |
| 10⁹ | 30 | 10¹¹ |
| 10¹⁸ | 60 | 10²⁰ |

Adding ten bits to W multiplies the work by about 1,000 (2¹⁰ = 1,024). An algorithm that's polynomial in the **numeric value** but not in its bit length is called **pseudo-polynomial**.

This is consistent with knapsack, subset sum and partition being **NP-complete** (as decision problems). These decision versions are **weakly NP-complete**: they have pseudo-polynomial algorithms, unlike strongly NP-complete numeric problems, unless P = NP (unless every problem whose solutions can be checked in polynomial time can also be solved in polynomial time, which is widely believed to be false). Large numbers do not make every individual instance difficult. When the numbers are small (bounded by a polynomial in n), DP solves them efficiently. Contrast with *strongly* NP-hard problems like the travelling salesman, whose decision versions remain NP-complete even with polynomially bounded weights.

### What to do when W is huge

- **DP over value instead of weight**: `minW[v]` = minimum weight needed to achieve value exactly v. It takes O(n · V) time, where V is the total of all values. Useful when values are small but weights are big.
- **Meet in the middle**: for n up to about 40, split the items in half, enumerate all subsets of each half, sort one side and binary-search it:

```formula
T = O(2^{n/2} × n)
T(40) ≈ 2^20 × 20 ≈ 10^6 × 20 = 2 × 10^7
where
T: the running time, in basic steps
n: the number of items
2^{n/2}: n/2 copies of 2 multiplied together, the number of subsets of one half of the items
O(...): Big-O, growing at most in proportion to the expression inside
≈: approximately equal to
In words: each half has only 2^(n/2) subsets, and sorting plus binary search adds about a factor of n, so the work never depends on W.
```

For n = 40 that is about 20 million steps, compared with 2^40 ≈ 1.1 × 10^12 subsets for brute force.

- **Approximation algorithms**: scale and round the values, then run the value DP. Pick an allowed relative error ε (epsilon) between 0 and 1. For nonnegative values, discard individually overweight items, choose an appropriate scaling factor and handle the zero-optimum case separately. The resulting value DP gives a (1 − ε)-approximation: its total value is at least (1 − ε) times the optimum, for example within 1 % of it when ε = 0.01. The work is polynomial in n and 1/ε (plus input bit costs), which makes it an FPTAS.
- **Branch and bound / integer programming** solvers can exploit structure in some large instances, but retain exponential worst-case risks.

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

The example is five 1s with T = 3: count the subsets of sum 4, of which there are 5 (choose which four 1s are positive). If |T| (the size of T, ignoring sign) is greater than S, or S + T is odd, no assignment exists; equal-valued positions still count as distinct.

- **Last stone weight II**: minimum-difference partition.
- **Ones and zeroes**: knapsack with a two-dimensional budget (count of 0s and 1s), state `dp[zeros][ones]`.

## Key takeaways
- 0/1 knapsack: each table cell is the better of skipping or taking the current item; one row iterated **downwards** so each item is used at most once.
- Unbounded knapsack is the same code with the weight limit iterated **upwards**; coin change is unbounded knapsack.
- Subset sum is 0/1 knapsack on feasibility; partition is subset sum with target S / 2.
- O(n·W) for n items and weight limit W is pseudo-polynomial: exponential in the bits of W. Knapsack is weakly NP-hard.
- Huge W? Switch to DP over value, meet in the middle (n ≤ ~40), approximation, or an ILP solver.

## Further reading
- [Knapsack problem — Wikipedia](https://en.wikipedia.org/wiki/Knapsack_problem)
- [Knapsack problem — cp-algorithms](https://cp-algorithms.com/dynamic_programming/knapsack.html)
- [Subset sum problem — Wikipedia](https://en.wikipedia.org/wiki/Subset_sum_problem)
- [Partition problem — Wikipedia](https://en.wikipedia.org/wiki/Partition_problem)
- [Pseudo-polynomial time — Wikipedia](https://en.wikipedia.org/wiki/Pseudo-polynomial_time)
- [Weak NP-completeness — Wikipedia](https://en.wikipedia.org/wiki/Weak_NP-completeness)
