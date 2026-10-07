---
id: dp-knapsack
title: The knapsack family
level: intermediate
minutes: 14
summary: 0/1 and unbounded knapsack, subset sum and partition, why the loop direction matters, and why O(n·W) is pseudo-polynomial rather than polynomial.
---

You have a bag that holds weight W and a set of items, each with a weight and a value. Which items should you pack to maximise the total value?

That's the **knapsack problem**, and a surprising number of real problems are knapsack in disguise: choosing which features fit in a sprint, which ads fill a slot, which jobs fit on a machine, which files fit on a disk, how to split a bill evenly. Learn this family well and you'll recognise it everywhere.

## Why greedy fails

The obvious greedy is "take items in order of value per unit weight". With capacity 7 and items:

| Item | Weight | Value | Value/kg |
|---|---|---|---|
| A | 1 | 1 | 1.00 |
| B | 3 | 4 | 1.33 |
| C | 4 | 5 | 1.25 |
| D | 5 | 7 | 1.40 |

Greedy takes D (5 kg, value 7), then B doesn't fit, C doesn't fit, takes A: total 8 for 6 kg. The optimum is B + C: 7 kg, value **9**.

Greedy *is* optimal for the **fractional** knapsack, where you can take part of an item (gold dust rather than gold bars). For indivisible items this greedy rule is not generally exact; DP is one option alongside exhaustive search, branch and bound and other methods.

## 0/1 knapsack

Each item can be taken at most once. The code assumes positive integer weights, nonnegative integer values and a nonnegative integer capacity; choosing nothing is allowed.

**State**: `K[i][c]` = best value using only the first i items with capacity c.

**Recurrence**: decide about item i (weight `w`, value `v`).

- Skip it: `K[i-1][c]`.
- Take it, if it fits: `K[i-1][c-w] + v`.

```
K[i][c] = max(K[i-1][c],
              K[i-1][c-w] + v)   if w <= c
```

**Base**: `K[0][c] = 0` (no items, no value).

For the items above (rows = items considered, columns = capacity 0..7):

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

Each row only reads the previous row, at the same or a smaller capacity. So use a single array and loop capacity **downwards**:

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
> Loop direction is the only difference between 0/1 and unbounded knapsack in the 1-D form. With one item of weight 2 and value 3 and capacity 6, the downward loop gives 3 (one copy), and the upward loop gives 9 (three copies). Get the direction wrong and your 0/1 solution silently becomes unbounded.

## Unbounded knapsack

Unlimited copies of each item. Same array, loop capacity **upwards**:

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

Now `best[c - w]` may already contain copies of this item, which is exactly what we want. Example: items (3 kg, 4), (4 kg, 5), (5 kg, 6), capacity 10. 0/1 gives 11 (4 + 5 kg); unbounded gives 13 (3 + 3 + 4 kg).

Coin change from lesson 3 is unbounded knapsack: "minimum coins" is min-count knapsack, "number of ways" is counting knapsack.

**Bounded** knapsack (item i available up to kᵢ times) can be solved by splitting each item into bundles of sizes 1, 2, 4, ... plus a final remainder so their sizes sum exactly to kᵢ. This yields O(log(kᵢ + 1)) 0/1 items for each type; kᵢ = 0 contributes none.

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
- **Minimum items** to reach T: `+∞` sentinel and `min(..., dp[s - x] + 1)`.

> [!tip] Bitset trick
> A Python integer can encode reachable sums. Start with `mask = 1` and `limit = (1 << (T + 1)) - 1`; for each nonnegative x ≤ T, update `mask = (mask | (mask << x)) & limit`. Skip x > T, then test `(mask >> T) & 1`. Masking bounds retained and temporary lengths by O(T + 1) bits. Without masking, storage instead grows with the sum of all inputs. Packed word operations can improve constants, but a shift is not constant-time on arbitrary-size integers.
>
> Content gap: fixed 64× or Python speedup claims are omitted because no pinned benchmark supports them.

## Partition

> Can `nums` be split into two groups with equal sums?

If the total S is odd, no. Otherwise it's subset sum with target S / 2: if one group sums to S / 2, the rest does too.

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

**Minimum difference partition** (split into two groups as evenly as possible): compute all reachable sums up to S / 2, take the largest reachable s, and the answer is `S − 2s`.

## Pseudo-polynomial time

0/1 knapsack takes O(n · W) time. That looks polynomial. It isn't, quite.

Complexity is measured against the **size of the input**: the number of bits needed to write it. The input includes every weight and value as well as W, so their bit lengths all matter. Positive W uses floor(log₂W) + 1 bits. The table algorithm can take work exponential in W’s bit length; O(nW) is not a polynomial bound in the full binary encoding length.

| W | Bits | nW work expression (n = 100) |
|---|---|---|
| 1,000 | 10 | 10⁵ |
| 10⁶ | 20 | 10⁸ |
| 10⁹ | 30 | 10¹¹ |
| 10¹⁸ | 60 | 10²⁰ |

Adding ten bits to W multiplies the work by about 1,000. An algorithm that's polynomial in the **numeric value** but not in its bit length is called **pseudo-polynomial**.

This is consistent with knapsack, subset sum and partition being **NP-complete** (as decision problems). These decision versions are **weakly NP-complete**: they have pseudo-polynomial algorithms, unlike strongly NP-complete numeric problems unless P = NP. Large numbers do not make every individual instance difficult. When the numbers are small (bounded by a polynomial in n), DP solves them efficiently. Contrast with *strongly* NP-hard problems like the travelling salesman, whose decision versions remain NP-complete even with polynomially bounded weights.

### What to do when W is huge

- **DP over value instead of weight**: `minW[v]` = minimum weight to achieve value v. O(n · V) where V is the total value. Useful when values are small but weights are big.
- **Meet in the middle**: for n up to about 40, split the items in half, enumerate all 2^(n/2) subsets of each half, sort one side and binary-search: O(2^(n/2) · n). That's about 10⁶ × 20 for n = 40, independent of W.
- **Approximation**: scale and round the values, then run the value DP. For 0 < ε < 1 and nonnegative values, discard individually overweight items, choose an appropriate scaling factor and handle the zero-optimum case separately. The resulting value DP gives a (1 − ε)-approximation with work polynomial in n and 1/ε (plus input bit costs): an FPTAS.
- **Branch and bound / integer programming** solvers can exploit structure in some large instances, but retain exponential worst-case risks.

## Recognising knapsack

Ask: "Am I choosing a **subset** of items, subject to a **budget** on some additive quantity, while optimising or counting another additive quantity?" If so, the state is (items considered, budget used), and it's knapsack. Examples:

- **Target sum** ("assign + or − to each number to reach T"): with P the sum of the + group, `P − (S − P) = T` gives `P = (S + T) / 2`, so it is subset counting for nonnegative integer inputs. If |T| > S or S + T is odd, no assignment exists; equal-valued positions remain distinct.
- **Last stone weight II**: minimum-difference partition.
- **Ones and zeroes**: knapsack with a two-dimensional budget (count of 0s and 1s), state `dp[zeros][ones]`.

## Key takeaways
- 0/1 knapsack: `K[i][c] = max(skip, take)`; one row iterated **downwards** so each item is used at most once.
- Unbounded knapsack is the same code with capacity iterated **upwards**; coin change is unbounded knapsack.
- Subset sum is 0/1 knapsack on feasibility; partition is subset sum with target S / 2.
- O(n·W) is pseudo-polynomial: exponential in the bits of W. Knapsack is weakly NP-hard.
- Huge W? Switch to DP over value, meet in the middle (n ≤ ~40), approximation, or an ILP solver.

## Further reading
- [Knapsack problem — Wikipedia](https://en.wikipedia.org/wiki/Knapsack_problem)
- [Knapsack problem — cp-algorithms](https://cp-algorithms.com/dynamic_programming/knapsack.html)
- [Subset sum problem — Wikipedia](https://en.wikipedia.org/wiki/Subset_sum_problem)
- [Partition problem — Wikipedia](https://en.wikipedia.org/wiki/Partition_problem)
- [Pseudo-polynomial time — Wikipedia](https://en.wikipedia.org/wiki/Pseudo-polynomial_time)
- [Weak NP-completeness — Wikipedia](https://en.wikipedia.org/wiki/Weak_NP-completeness)
