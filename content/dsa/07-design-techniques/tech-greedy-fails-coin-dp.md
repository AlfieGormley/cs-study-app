---
id: tech-greedy-fails-coin-dp
title: Keeping every last-coin alternative
level: advanced
minutes: 3
sourceLesson: tech-greedy-fails
summary: The amount DP chooses among all possible last coins.
---

The previous unit showed largest-coin-first failing. Here coins remain positive integer denominations with unlimited supply, and amount is a non-negative integer. Keeping the best answer for each smaller amount avoids committing to the wrong first coin.

### The DP alternative

Instead of committing to one coin, consider *every* possible last coin and take the best. Whatever the last coin c is, the rest of the amount must itself be paid optimally:

```formula essential
B(a) = 1 + min_{c ≤ a} B(a − c)
B(0) = 0
where
B(a): the fewest coins that make amount a (best[a] in the code); infinity if a can't be made
a: the amount to make, a whole number of at least 0
c: one coin denomination, a positive whole number
min_{c ≤ a}: the smallest value over every coin c no bigger than a
In words: the best way to pay a is one coin plus the best way to pay what is left, tried for every coin that fits.
```

For coins {1, 3, 4} and amount 6, the three possible last coins leave 5, 3 or 2 to pay, which need 2, 1 and 2 coins. The best route ends with a 3-coin and leaves 3, which one more 3-coin pays: 3 + 3, two coins. Greedy never looks at that option because it commits to the 4 first.

```python
def min_coins(coins, amount):
    coins = list(coins)
    if (type(amount) is not int
            or amount < 0
            or any(type(c) is not int
                   or c <= 0
                   for c in coins)):
        raise ValueError("positive coins")
    INF = float("inf")
    # Unreachable amounts start at infinity.
    best = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                # Try this denomination as
                # the last coin.
                cand = best[a - c] + 1
                best[a] = min(best[a], cand)
    if best[amount] == INF:
        return None
    return best[amount]
```

For {1, 3, 4}, the table for amounts 0 to 6 is 0, 1, 2, 1, 1, 2, 2. The cost is one pass over the coins for each amount: for a target amount A and k denominations, about A × k steps and a table of A + 1 entries. Eight UK denominations and £10.00 (1,000 pence) take about 8,000 steps. Note that the work grows with the *value* of the amount, not with the number of digits needed to write it.

It is correct for the stated positive-integer, unlimited-supply domain. The dynamic programming module develops this way of thinking in depth; here the point is the contrast. Greedy keeps **one** candidate per step; DP compares the last-coin alternatives for each amount, retaining the best value for that state.

## Key takeaways
- The amount DP chooses among all possible last coins.
- Its work grows with numeric target amount and denomination count, rather than just the input digit count.

## Further reading
- [Dynamic programming — Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
