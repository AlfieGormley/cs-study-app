---
id: dp-1d
title: 1-D DP
level: intermediate
minutes: 14
summary: Climbing stairs, house robber, coin change (minimum coins and number of ways) and longest increasing subsequence in both O(n²) and O(n log n).
---

A 1-D DP has a state described by a single index or amount: `dp[i]` for a position in an array, or `dp[a]` for an amount of money. These problems are the best place to practise the method, because the state is obvious and all the difficulty is in the recurrence.

## Climbing stairs

> You can climb 1 or 2 steps at a time. How many distinct ways are there to reach step n?

- **State**: `ways[i]` = number of ways to reach step i.
- **Recurrence**: the last move was a 1-step (from i − 1) or a 2-step (from i − 2). Those are disjoint, so add: `ways[i] = ways[i-1] + ways[i-2]`.
- **Base**: `ways[0] = 1` (one way to stand still), `ways[1] = 1`.

```python
def climb(n):
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative n")
    a, b = 1, 1  # ways[0], ways[1]
    for _ in range(n - 1):
        a, b = b, a + b
    return b
```

`climb(5) = 8`. It's Fibonacci shifted by one. If you can take steps of size 1, 2 or 3, the recurrence gains a third term; with distinct positive step sizes S, `ways[i] = Σ ways[i-s]`, treating negative-index terms as zero.

## House robber

> Houses in a row hold amounts `h[0..n-1]`. You can't rob two adjacent houses. Maximise the total.

**State**: `best[i]` = the most you can take from the first i houses.

**Recurrence**: for house i − 1 there are two choices.

- Skip it: `best[i-1]`.
- Rob it: then house i − 2 is off limits, so `best[i-2] + h[i-1]`.

```
best[i] = max(best[i-1],
              best[i-2] + h[i-1])
```

**Base**: `best[0] = 0`, `best[1] = max(0, h[0])`. Taking no houses is allowed; integer amounts may be negative.

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

**Variant**: houses in a **circle** (first and last adjacent). For n ≥ 2, run the linear version on `h[1:]` and `h[:-1]` and take the max. Every valid plan excludes at least one end. Handle n = 0 with 0 and n = 1 with max(0, h[0]). Slicing allocates O(n) extra space; index-bounded passes avoid those copies.

## Coin change: minimum coins

> Given coin denominations and an amount, what's the fewest coins that make the amount exactly (unlimited supply of each)?

Greedy (largest fitting coin first) is optimal for the unlimited-supply denomination set {1, 2, 5, 10, 20, 50, 100, 200}, but not arbitrary sets. The code below deduplicates positive integer denominations and requires a nonnegative integer amount. With coins `{1, 3, 4}` and amount 6, greedy takes 4 + 1 + 1 = 3 coins; the optimum is 3 + 3 = 2 coins.

- **State**: `dp[a]` = fewest coins to make amount a.
- **Recurrence**: the last coin is some c ≤ a: `dp[a] = 1 + min(dp[a-c])`.
- **Base**: `dp[0] = 0`. Unreachable amounts stay `+∞`.

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

**Complexity**: O(k + A(k + 1)) unit-cost work including input/table setup; conventionally O(Ak) for positive A and k. Space is O(A + k) slots. Note that this depends on the **value** of A, not the number of digits used to write it. That's pseudo-polynomial time, covered properly in lesson 5.

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

Why? With coins in the outer loop, after processing coin c, `dp[a]` counts ways using **only the coins seen so far**. Each combination is built in one canonical order (all 1s, then all 2s, then 5s), so it's counted once. With the amount outer, every coin is a candidate for the "last coin" of every amount, which counts sequences.

> [!warning] Know which one you need
> "Number of combinations" (coin change) puts items in the outer loop. "Number of sequences" (climbing stairs with step set S, or LeetCode's "combination sum IV", which despite its name counts orderings) puts the target outer.

## Longest increasing subsequence

> Find the length of the longest strictly increasing subsequence (not necessarily contiguous).

For `[10, 9, 2, 5, 3, 7, 101, 18]`, one LIS is `[2, 3, 7, 18]`, length 4.

### O(n²): a DP over end positions

- **State**: `L[i]` = length of the longest increasing subsequence **ending at** index i.
- **Recurrence**: the element before `a[i]` is some earlier `a[j] < a[i]`:
  `L[i] = 1 + max(L[j] for j < i if a[j] < a[i])`, or 1 if there's none.
- **Answer**: `max(L)`, not `L[n-1]`, because the LIS can end anywhere.

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

Length 4. Each step is one binary search plus an amortized O(1) append or O(1) replacement: **O(n log n)** comparisons and O(n) slots for positive n.

> [!warning] tails is not the LIS
> On `[3, 1, 4, 1, 5, 9, 2, 6]` the final `tails` is `[1, 2, 5, 6]`. That isn't a subsequence at all: the 2 comes *after* the 5 in the input. The *length* is right (4, e.g. `[3, 4, 5, 9]`), but the contents of `tails` mix different subsequences. To reconstruct, store for each element the index of its predecessor (the tail at position k − 1 when it was placed).

**Non-strict** (non-decreasing) LIS: use `bisect_right` instead, so equal elements extend rather than replace. With `bisect_left`, `[2, 2, 2]` gives 1; with `bisect_right` it gives 3.

## Real-world uses

- **Change-making** models cash selection, but a real drawer has limited stock and may need a bounded formulation.

> [!note] Content gap
> Claims about how most currencies were designed or which algorithms shops use are omitted because no authoritative survey or implementation evidence was verified.

- **LIS** underlies patience diff (used by Bazaar and available in Git as `git diff --patience`), which matches unique lines between files and keeps a longest increasing subsequence of unique-line matches, not necessarily a contiguous run.
- **House robber** is the 1-D case of **maximum-weight independent set**, which is NP-hard on general graphs but easy on paths and trees (lesson 6).

## Pitfalls

1. Returning `L[n-1]` instead of `max(L)` for LIS.
2. Mixing up combinations and orderings in coin counting.
3. Using greedy for coin change with arbitrary denominations.
4. Forgetting `dp[0] = 1` in counting problems: the empty selection is one way to make zero.
5. Integer overflow in counting problems outside Python: counts can grow exponentially; use arbitrary precision or a modulus only when the requested answer is modular.

## Key takeaways
- Climbing stairs and house robber are "the last move" recurrences that need only the previous one or two states, so they need O(1) value slots; exact counting values may grow in bit size.
- Coin change: `dp[a] = 1 + min dp[a − c]` for minimum coins; greedy fails for coins like {1, 3, 4}.
- When counting, coins outer counts combinations; amount outer counts orderings.
- LIS: "ending at i" states give O(n²); patience sorting with binary search gives O(n log n), but `tails` itself need not be a valid subsequence.
- Coin-change DP is O(amount × coins), which is pseudo-polynomial.

## Further reading
- [Change-making problem — Wikipedia](https://en.wikipedia.org/wiki/Change-making_problem)
- [Longest increasing subsequence — Wikipedia](https://en.wikipedia.org/wiki/Longest_increasing_subsequence)
- [Longest increasing subsequence — cp-algorithms](https://cp-algorithms.com/sequences/longest_increasing_subsequence.html)
- [Patience sorting — Wikipedia](https://en.wikipedia.org/wiki/Patience_sorting)
- [bisect — Python docs](https://docs.python.org/3/library/bisect.html)
