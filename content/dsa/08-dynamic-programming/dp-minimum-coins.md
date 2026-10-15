---
id: dp-minimum-coins
title: Minimise the coins for an amount
level: intermediate
minutes: 4
summary: Try every possible last denomination and take the cheapest reachable remainder.
sourceLesson: dp-1d
---

## Coin change: minimum coins

> Given coin denominations and an amount, what's the fewest coins that make the amount exactly (unlimited supply of each)?

Kozen and Zaks prove that, for a denomination system starting with one, any failure of greedy has a counterexample smaller than the sum of its two largest coins. For the exact set below, checking all amounts below 300 against the DP therefore establishes the all-amount result.

Greedy (largest fitting coin first) is optimal for the unlimited-supply denomination set {1, 2, 5, 10, 20, 50, 100, 200}, but not arbitrary sets. The code below deduplicates positive integer denominations and requires a nonnegative integer amount. With coins `{1, 3, 4}` and amount 6, greedy takes 4 + 1 + 1 = 3 coins; the optimum is 3 + 3 = 2 coins.

- **State**: `dp[a]` records fewest coins to make amount a.
- **Recurrence**: the last coin used is some coin c no bigger than a; remove it and what's left is a smaller amount solved the same way.
- **Base**: `dp[0] = 0`. Unreachable amounts stay `+∞`.

```formula
dp[0] = 0
dp[a] = 1 + min(dp[a − c])   for c ≤ a
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
    INF = float('inf')
    # Zero is reachable; other sums start
    # unreachable.
    dp = [0] + [INF] * amount
    # Each smaller remainder is already
    # ready.
    for a in range(1, amount + 1):
        # Each coin can be the sequence's
        # last.
        for c in coins:
            if c <= a:
                # Try this denomination as
                # the last coin.
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

For amount 10,000 with 5 coins that is about 50,000 steps. Note that this depends on the **value** of A, not the number of digits used to write it. That's pseudo-polynomial time, examined in “Numeric value versus encoded input size”.

## Real-world use

- The **change-making problem** models cash selection, but a real drawer has limited stock and may need a bounded formulation.

> [!note] Content gap
> Claims about how most currencies were designed or which algorithms shops use are omitted because no authoritative survey or implementation evidence was verified.

## Pitfalls

- Using greedy for coin change with arbitrary denominations.

## Key takeaways
- Try every possible last denomination and take the cheapest reachable remainder.
- Infinity marks an unreachable amount.
- Amount-indexed work depends on the numeric amount, not just its bit length.

## Further reading
- [Kozen and Zaks: optimal bounds for change-making](https://www.cs.cornell.edu/kozen/Papers/change.pdf)
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
- [MIT algorithms course](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/)
