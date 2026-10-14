---
id: tech-greedy-fails-coins
title: Coin change and greedy counterexamples
level: advanced
minutes: 3
sourceLesson: tech-greedy-fails
summary: Canonical coin systems permit largest-first change under unlimited supply.
---

Greedy algorithms are seductive: short, fast and usually plausible. The previous lesson showed problems where greedy is provably optimal. This lesson is about the much larger set where it isn't, and how to tell the difference *before* you ship a wrong answer.

The underlying reason greedy fails is always the same: **a locally best choice closes off options that a better global solution needed**, and greedy never goes back to reopen them.

## Coin change

Make a non-negative integer amount using the fewest coins, with an unlimited supply of each positive integer denomination. The obvious greedy rule: take the largest coin that fits, repeat.

```python
def greedy_coins(coins, amount):
    coins = list(coins)
    if (type(amount) is not int
            or amount < 0
            or any(type(c) is not int
                   or c <= 0
                   for c in coins)):
        raise ValueError("positive coins")
    count = 0
    for c in sorted(coins, reverse=True):
        # Take every largest coin that
        # currently fits.
        count += amount // c
        # Later denominations must pay this
        # remainder.
        amount %= c
    return count if amount == 0 else None
```

The denomination sets {1, 2, 5, 10, 20, 50, 100, 200} and {1, 5, 10, 25}, familiar from UK and US coin examples, are **canonical**: greedy minimises coin count for every amount under unlimited supply. A cash drawer with limited stock is a different problem.

> [!note] A property of the denomination set
> Canonicity proves an algorithmic property under unlimited supply. These examples do not establish why monetary authorities chose those denominations.

Now try coins {1, 3, 4} and amount 6:

```
greedy:  4 + 1 + 1   = 3 coins
optimal: 3 + 3       = 2 coins
```

Taking the 4 looked best, but it left a remainder of 2 that can only be paid in 1s. The optimal answer needed to *pass up* the biggest coin.

More counterexamples, found by brute-force checking:

| Coins | Amount | Greedy | Best |
|---|---|---|---|
| 1, 3, 4 | 6 | 4+1+1 | 3+3 |
| 1, 5, 12 | 15 | 12+1+1+1 | 5+5+5 |
| 1, 7, 10 | 14 | 10+1+1+1+1 | 7+7 |
| 1, 10, 25 | 30 | 25+1×5 | 10+10+10 |

The last row is the US system without the nickel: removing one coin breaks canonicity.

### Greedy can fail to find any answer

Without a 1-coin, greedy can get stuck even when a solution exists. Coins {3, 5}, amount 6: greedy takes 5, leaving 1, which nothing can pay. But 3 + 3 works.

## Key takeaways
- Canonical coin systems permit largest-first change under unlimited supply.
- A locally largest coin can increase the total count or prevent any answer.

## Further reading
- [Greedy algorithms — Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/book/04-greedy.pdf)
- [Dynamic programming — Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
