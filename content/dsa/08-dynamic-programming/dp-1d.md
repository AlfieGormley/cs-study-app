---
id: dp-1d
title: 1-D DP
level: intermediate
minutes: 18
summary: Climbing stairs, house robber, coin change (minimum coins and number of ways) and longest increasing subsequence, both the simple quadratic-time DP and the faster binary-search method.
---

A 1-D DP has a state described by a single index or amount: `dp[i]` for a position in an array, or `dp[a]` for an amount of money. These problems are the best place to practise the method, because the state is obvious and all the difficulty is in the recurrence.

## Climbing stairs

> You can climb 1 or 2 steps at a time. How many distinct ways are there to reach step n?

- **State**: `ways[i]` = number of ways to reach step i.
- **Recurrence**: the last move was a 1-step (from i − 1) or a 2-step (from i − 2). Those are disjoint (no route is counted in both), so add them.
- **Base**: `ways[0] = 1` (one way to stand still), `ways[1] = 1`.

```formula
ways[0] = 1
ways[1] = 1
ways[i] = ways[i − 1] + ways[i − 2]
ways[5] = ways[4] + ways[3] = 5 + 3 = 8
where
ways[i]: the number of different sequences of 1-steps and 2-steps that end exactly on step i
i: the step number, 0 at the bottom; the rule applies for i of 2 or more
ways[i − 1]: routes whose last move was a single step from i − 1
ways[i − 2]: routes whose last move was a double step from i − 2
In words: every route to step i ends with either a 1-step or a 2-step, so the count is the routes to the step below plus the routes to the step two below.
```

```python
def climb(n):
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative n")
    a, b = 1, 1  # ways[0], ways[1]
    for _ in range(n - 1):
        a, b = b, a + b
    return b
```

`climb(5) = 8`. It's Fibonacci shifted by one place: ways[i] is the Fibonacci number at position i + 1 (counting 0, 1, 1, 2, 3, 5, 8, ... from position 0), so ways[5] is 8. If you can take steps of size 1, 2 or 3, the recurrence gains a third term. In general, for any set of allowed step sizes:

```formula
ways[i] = Σ ways[i − s]   for s ∈ S
where
ways[i]: the number of ordered step sequences that reach step i exactly
i: the step number
S: the set of allowed step sizes, distinct positive whole numbers, for example {1, 2, 3}
s: one allowed step size from S
∈: "is a member of", so s ∈ S means s is one of the sizes in S
Σ: sum, add up the term for every s in S
In words: the routes to step i are grouped by their last step size, so add up the routes to each step that is one allowed jump below i.
```

Any term with i − s below zero counts as 0 (you can't start below the bottom). With S = {1, 2, 3}, ways[3] = ways[2] + ways[1] + ways[0] = 2 + 1 + 1 = 4.

## House robber

> Houses in a row hold amounts `h[0..n-1]`. You can't rob two adjacent houses. Maximise the total.

**State**: `best[i]` = the most you can take from the first i houses.

**Recurrence**: for house i − 1 (the last of the first i houses) there are two choices.

- Skip it: `best[i-1]`.
- Rob it: then house i − 2 is off limits, so `best[i-2] + h[i-1]`.

```formula
best[i] = max(best[i − 1],
  best[i − 2] + h[i − 1])
best[0] = 0
best[1] = max(0, h[0])
where
best[i]: the largest total you can take from houses 0 to i − 1 (the first i houses) without robbing two neighbours
i: how many houses, counted from the left, are being considered; the first line applies for i of 2 or more
h[i − 1]: the amount in house i − 1 (houses are numbered from 0)
max: the larger of the values listed
In words: either leave the last house alone and keep the best plan for the houses before it, or rob it and add its amount to the best plan that stops two houses earlier.
```

Taking no houses is allowed, which is why best[1] can be 0 if amounts may be negative.

Each state needs only the previous two, so two variables suffice:

```python
def rob(h):
    prev, cur = 0, 0  # best[i-2], best[i-1]
    for x in h:
        prev, cur = cur, max(cur, prev + x)
    return cur
```

Trace `h = [2, 7, 9, 3, 1]`:

```
house  x   prev  cur
start      0     0
0      2   0     2
1      7   2     7
2      9   7     11   (2 + 9)
3      3   11    11   (7 + 3 = 10 < 11)
4      1   11    12   (11 + 1)
```

Answer 12: houses 0, 2 and 4 (2 + 9 + 1).

> [!note] Why greedy fails here
> "Take the biggest house, remove its neighbours, repeat" fails on `[2, 3, 2]`: it takes the 3 and must stop, but robbing both 2s gives 4. Local choices interact, and DP's "try both, keep the best" handles that.

**Variant**: houses in a **circle** (first and last adjacent). With n houses and n ≥ 2, run the linear version on `h[1:]` and `h[:-1]` and take the max. Every valid plan excludes at least one end. Handle n = 0 with 0 and n = 1 with max(0, h[0]). Slicing allocates O(n) extra space; index-bounded passes avoid those copies.

## Coin change: minimum coins

> Given coin denominations and an amount, what's the fewest coins that make the amount exactly (unlimited supply of each)?

Greedy (largest fitting coin first) is optimal for the unlimited-supply denomination set {1, 2, 5, 10, 20, 50, 100, 200}, but not arbitrary sets. The code below deduplicates positive integer denominations and requires a nonnegative integer amount. With coins `{1, 3, 4}` and amount 6, greedy takes 4 + 1 + 1 = 3 coins; the optimum is 3 + 3 = 2 coins.

- **State**: `dp[a]` = fewest coins to make amount a.
- **Recurrence**: the last coin used is some coin c no bigger than a; remove it and what's left is a smaller amount solved the same way.
- **Base**: `dp[0] = 0`. Unreachable amounts stay `+∞`.

```formula
dp[0] = 0
dp[a] = 1 + min dp[a − c]   for c ≤ a
dp[6] = 1 + min(dp[5], dp[3], dp[2])
dp[6] = 1 + min(2, 1, 2) = 2
where
dp[a]: the fewest coins that add up to exactly a, or +∞ if a can't be made
a: the amount of money, a whole number from 0 up to the target
c: a coin denomination (value), taken from the given set
min: the smallest value, taken over every coin c no larger than a; +∞ if no coin fits
+∞: positive infinity, a stand-in for "impossible" that loses every min
In words: choose the last coin; the rest of the amount is a smaller problem, so take the coin that leaves the cheapest remainder and add one.
```

The example uses coins {1, 3, 4}: for amount 6 the last coin is 1, 3 or 4, leaving 5, 3 or 2.
```python
def min_coins(coins, amount):
    coins = tuple(dict.fromkeys(coins))
    if (type(amount) is not int
            or amount < 0
            or any(type(c) is not int
                   or c <= 0
                   for c in coins)):
        raise ValueError("positive coins")
    INF = float('inf')
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                dp[a] = min(dp[a],
                            dp[a-c] + 1)
    return dp[amount] if dp[amount] < INF \
        else -1
```

For coins `{1, 3, 4}`: `dp = [0, 1, 2, 1, 1, 2, 2]`, so `dp[6] = 2`. For `{1, 2, 5}` and 11, it's 3 (5 + 5 + 1).

**Complexity**: there are A + 1 amounts and each tries every coin:

```formula
T = O(k + A × (k + 1)) = O(A × k)
M = O(A + k)
where
T: the running time, counting each comparison and addition as one step
M: the memory used, in table slots
A: the target amount (amount in the code), a positive whole number
k: the number of distinct coin denominations, positive
O(...): Big-O, growing at most in proportion to the expression inside
In words: every amount from 1 to A checks every coin, so the work is about the amount times the number of coins.
```

For amount 10,000 with 5 coins that is about 50,000 steps. Note that this depends on the **value** of A, not the number of digits used to write it. That's pseudo-polynomial time, covered properly in lesson 5.

## Coin change: number of ways

> How many ways can you make the amount? (Order doesn't matter: 1 + 2 and 2 + 1 are the same.)

This is where a subtle loop-order detail changes the answer.

```python
def count_combinations(coins, amount):
    coins = tuple(dict.fromkeys(coins))
    if (type(amount) is not int
            or amount < 0
            or any(type(c) is not int
                   or c <= 0
                   for c in coins)):
        raise ValueError("positive coins")
    dp = [1] + [0] * amount
    for c in coins:            # coins outer
        for a in range(c, amount + 1):
            dp[a] += dp[a - c]
    return dp[amount]

def count_orderings(coins, amount):
    coins = tuple(dict.fromkeys(coins))
    if (type(amount) is not int
            or amount < 0
            or any(type(c) is not int
                   or c <= 0
                   for c in coins)):
        raise ValueError("positive coins")
    dp = [1] + [0] * amount
    for a in range(1, amount + 1):
        # amount outer
        for c in coins:
            if c <= a:
                dp[a] += dp[a - c]
    return dp[amount]
```

For coins `{1, 2, 5}` and amount 5:

- `count_combinations` returns **4**: {5}, {2, 2, 1}, {2, 1, 1, 1}, {1, 1, 1, 1, 1}.
- `count_orderings` returns **9**, because it counts 1 + 2 + 2, 2 + 1 + 2 and 2 + 2 + 1 separately (and similarly for the others).

Why? With coins in the outer loop, after processing coin c, `dp[a]` counts ways using **only the coins seen so far**. Written as a two-dimensional recurrence, that loop computes:

```formula
N[j][a] = N[j − 1][a] + N[j][a − c_j]
N[j][0] = 1
N[3][5] = N[2][5] + N[3][0] = 3 + 1 = 4
where
N[j][a]: the number of combinations (order ignored) of the first j coin types that add up to exactly a
j: how many coin types have been processed so far, 1 to k
k: the number of coin types
a: the amount, from 0 up to the target; a term with a − c_j below 0 counts as 0
c_j: the value of the jth coin type
N[j − 1][a]: combinations that use no coin of type j
N[j][a − c_j]: combinations that use at least one coin of type j (remove one and count what is left)
In words: a combination either uses none of the newest coin type or at least one of it, so add the two counts.
```

The example is coins {1, 2, 5} and amount 5: N[2][5] = 3 ways with only 1s and 2s, plus the single way that uses a 5. The 1-D code stores only the latest row, so `dp[a] += dp[a - c]` performs this addition in place. Each combination is built in one canonical order (all 1s, then all 2s, then 5s), so it's counted once. With the amount outer, every coin is a candidate for the "last coin" of every amount, which counts sequences.

> [!warning] Know which one you need
> "Number of combinations" (coin change) puts items in the outer loop. "Number of sequences" (climbing stairs with step set S, or LeetCode's "combination sum IV", which despite its name counts orderings) puts the target outer.

## Longest increasing subsequence

> Find the length of the longest strictly increasing subsequence (not necessarily next to each other).

For `[10, 9, 2, 5, 3, 7, 101, 18]`, one LIS is `[2, 3, 7, 18]`, length 4.

### O(n²): a DP over end positions

- **State**: `L[i]` = length of the longest increasing subsequence **ending at** index i.
- **Recurrence**: the element before `a[i]` is some earlier `a[j] < a[i]`, or there is none and `a[i]` stands alone.
- **Answer**: `max(L)`, not `L[n-1]`, because the LIS can end anywhere.

```formula
L[i] = 1 + max(0, L[j] for j < i
         with a[j] < a[i])
answer = max(L[0], ..., L[n − 1])
where
L[i]: the length of the longest strictly increasing subsequence that ends with element i
i: an index into the array, 0 to n − 1
j: an earlier index, smaller than i
a[i]: the element at index i
max: the largest of the listed values; the 0 covers the case where no earlier element is smaller
answer: the length of the longest increasing subsequence anywhere in the array
n: the number of elements in the array
In words: element i either starts a new subsequence of length 1, or extends the longest subsequence ending at a smaller, earlier element.
```

For example, with a = [10, 9, 2, 5, 3, 7] and i = 5 (the 7), the smaller earlier elements are 2, 5 and 3, with L values 1, 2 and 2, so L[5] = 1 + 2 = 3.

```python
def lis_quadratic(a):
    L = [1] * len(a)
    for i in range(len(a)):
        for j in range(i):
            if a[j] < a[i]:
                L[i] = max(L[i], L[j] + 1)
    return max(L, default=0)
```

For the example, `L = [1, 1, 1, 2, 2, 3, 4, 4]`, so the answer is 4.

"Ending at i" is a common trick: "the best subsequence in `a[:i]`" doesn't give you a usable recurrence, because you need to know the last element to decide whether `a[i]` can extend it. Fixing the end fixes that.

To reconstruct, store `parent[i] = j` for the j that gave the best value and follow parents back from the argmax.

### O(n log n): patience sorting

Keep an array `tails` where `tails[k]` is the **smallest possible last element** of an increasing subsequence of length k + 1 seen so far. `tails` is always sorted, so you can binary-search it.

For each x:

- If x is bigger than every tail, append it: you've extended the longest subsequence.
- Otherwise replace the first tail ≥ x with x: you've found a length-(k+1) subsequence with a smaller ending, which is easier to extend later.

```python
from bisect import bisect_left

def lis_fast(a):
    tails = []
    for x in a:
        k = bisect_left(tails, x)
        if k == len(tails):
            tails.append(x)
        else:
            tails[k] = x
    return len(tails)
```

Trace:

```
x     tails
10    [10]
9     [9]
2     [2]
5     [2, 5]
3     [2, 3]
7     [2, 3, 7]
101   [2, 3, 7, 101]
18    [2, 3, 7, 18]
```

Length 4. Each of the n elements costs one binary search on `tails`, plus an amortised O(1) append or O(1) replacement:

```formula
T = n × O(log_2(n)) = O(n × log n)
T(10^5) ≈ 10^5 × 17 = 1.7 × 10^6
where
T: the number of comparisons made by lis_fast
n: the number of elements in the input array, positive
log_2(n): the base-2 logarithm of n, the number of halvings a binary search needs on n items (about 17 for 100,000)
log: logarithm; the base only changes a constant factor
O(...): Big-O, growing at most in proportion to the expression inside
≈: approximately equal to
In words: n binary searches on a list of at most n items, each taking about log_2(n) comparisons.
```

The memory is O(n) slots for `tails`.

> [!warning] tails is not the LIS
> On `[3, 1, 4, 1, 5, 9, 2, 6]` the final `tails` is `[1, 2, 5, 6]`. That isn't a subsequence at all: the 2 comes *after* the 5 in the input. The *length* is right (4, e.g. `[3, 4, 5, 9]`), but the contents of `tails` mix different subsequences. To reconstruct, store for each element the index of the element before it in the subsequence (the tail at position k − 1 when it was placed).

**Non-strict** (non-decreasing) LIS: use `bisect_right` instead, so equal elements extend rather than replace. With `bisect_left`, `[2, 2, 2]` gives 1; with `bisect_right` it gives 3.

## Real-world uses

- The **change-making problem** models cash selection, but a real drawer has limited stock and may need a bounded formulation.

> [!note] Content gap
> Claims about how most currencies were designed or which algorithms shops use are omitted because no authoritative survey or implementation evidence was verified.

- **LIS** underlies patience diff (used by Bazaar and available in Git as `git diff --patience`), which matches unique lines between files and keeps a longest increasing subsequence of unique-line matches, not necessarily an unbroken run.
- **House robber** is the 1-D case of **maximum-weight independent set**, which is NP-hard on general graphs but easy on paths and trees (lesson 6).

## Pitfalls

1. Returning `L[n-1]` instead of `max(L)` for LIS.
2. Mixing up combinations and orderings in coin counting.
3. Using greedy for coin change with arbitrary denominations.
4. Forgetting `dp[0] = 1` in counting problems: the empty selection is one way to make zero.
5. Integer overflow in counting problems outside Python: counts can grow exponentially; use arbitrary precision or a modulus only when the requested answer is modular.

## Key takeaways
- Climbing stairs and house robber are "the last move" recurrences that need only the previous one or two states, so they need O(1) value slots; exact counting values may grow in bit size.
- Coin change: the fewest coins for an amount is one more than the fewest for what remains after the best last coin; greedy fails for coins like {1, 3, 4}.
- When counting, coins outer counts combinations; amount outer counts orderings.
- LIS on n elements: "ending at i" states give O(n²); patience sorting with binary search gives O(n log n), but `tails` itself need not be a valid subsequence.
- Coin-change DP is O(amount × coins), which is pseudo-polynomial.

## Further reading
- [Change-making problem — Wikipedia](https://en.wikipedia.org/wiki/Change-making_problem)
- [Longest increasing subsequence — Wikipedia](https://en.wikipedia.org/wiki/Longest_increasing_subsequence)
- [Longest increasing subsequence — cp-algorithms](https://cp-algorithms.com/sequences/longest_increasing_subsequence.html)
- [Patience sorting — Wikipedia](https://en.wikipedia.org/wiki/Patience_sorting)
- [bisect — Python docs](https://docs.python.org/3/library/bisect.html)
