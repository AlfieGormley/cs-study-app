---
id: dp-coin-counting-order
title: Count combinations or ordered sequences
level: intermediate
minutes: 4
summary: Coins outside and amounts increasing count combinations.
sourceLesson: dp-1d
---

## Coin change: number of ways

> How many ways can you make the amount? (Order doesn't matter: 1 + 2 and 2 + 1 are the same.)

This is where a subtle loop-order detail changes the answer.

```python
def count_combinations(coins, amount):
    # Validate every supplied value first.
    coins = tuple(coins)
    if (type(amount) is not int
            or amount < 0
            or any(type(c) is not int
                   or c <= 0
                   for c in coins)):
        raise ValueError("positive coins")
    # Equal denominations are one coin type.
    coins = tuple(dict.fromkeys(coins))
    # The empty selection makes zero once.
    dp = [1] + [0] * amount
    # Earlier coin types are fixed first.
    for c in coins:            # coins outer
        # Reuse this coin without reordering
        # types.
        for a in range(c, amount + 1):
            dp[a] += dp[a - c]
    return dp[amount]

def count_orderings(coins, amount):
    # Validate every supplied value first.
    coins = tuple(coins)
    if (type(amount) is not int
            or amount < 0
            or any(type(c) is not int
                   or c <= 0
                   for c in coins)):
        raise ValueError("positive coins")
    # Equal denominations are one coin type.
    coins = tuple(dict.fromkeys(coins))
    # The empty selection makes zero once.
    dp = [1] + [0] * amount
    # Each smaller remainder is already
    # ready.
    for a in range(1, amount + 1):
        # amount outer
        # Each coin can be the sequence's
        # last.
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

For coins {1, 2, 5} and amount 5, there are three ways using only ones and twos, plus the single combination using a five. The 1-D code stores only the latest row, so `dp[a] += dp[a - c]` performs this addition in place. Each combination is built in one canonical order (all 1s, then all 2s, then 5s), so it's counted once. With the amount outer, every coin is a candidate for the "last coin" of every amount, which counts sequences.

> [!warning] Know which one you need
> "Number of combinations" (coin change) puts items in the outer loop. "Number of sequences" (climbing stairs with step set S, or LeetCode's "combination sum IV", which despite its name counts orderings) puts the target outer.

## Pitfalls

- Mixing up combinations and orderings in coin counting.
- Forgetting `dp[0] = 1` in counting problems: the empty selection is one way to make zero.
- Integer overflow in counting problems outside Python: counts can grow exponentially; use arbitrary precision or a modulus only when the requested answer is modular.

## Key takeaways
- Coins outside and amounts increasing count combinations.
- Amounts outside count ordered sequences.
- The empty selection gives one way to make zero.

## Further reading
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
- [MIT algorithms course](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/)
