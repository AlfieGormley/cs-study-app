---
id: disc-coin-change-generating-functions
title: "Coin change as generating-function multiplication"
level: intermediate
minutes: 2
summary: "Each coin denomination contributes a geometric-series factor."
sourceLesson: disc-inclusion-recurrences
---

### Example: making change

To make an amount from unlimited 1p, 2p and 5p coins, ignore coin order and track how many of each denomination are used. One series records each denomination’s achievable amounts: pennies can make every non-negative amount, two-pence coins make even amounts, and five-pence coins make multiples of five. Multiplying combines these choices.

```formula reference
G(x) = 1 / ((1 − x) × (1 − x^2) × (1 − x^5))
1 / (1 − x^2) = 1 + x^2 + x^4 + …
1 / (1 − x^5) = 1 + x^5 + x^10 + …
where
G(x): the generating function for making change; the coefficient of x^n is the number of ways to make n pence
x: the placeholder variable; x^k stands for k pence
1 − x, 1 − x^2, 1 − x^5: one factor per coin; 1 / (1 − x^c) lists the amounts 0, c, 2c, … that coins worth c pence can make
…: and so on forever
In words: Each denomination contributes one series describing its possible totals. Multiplying the series combines denominations; the coefficient for an amount counts unordered ways to make that amount.
```

Keep only coefficients up to the target amount. This gives the classic coin-change dynamic programme. In the code, `n` is a non-negative integer amount and `coins` contains distinct positive integer denominations:

```python
def ways(n, coins):
    # Empty choice makes zero once.
    w = [1] + [0] * n
    # Add one denomination at a time.
    for c in coins:
        # Forward updates reuse this coin.
        for v in range(c, n + 1):
            # Add one more of this coin.
            w[v] += w[v - c]
    return w[n]

ways(10, [1, 2, 5])   # 10
```

The list `w` stores the number of combinations for each amount using denominations processed so far. Its zero entry starts at one because choosing no coins makes zero in exactly one way.

The forward amount loop reads a count that may already include the current coin. It therefore permits repeated use of that denomination. Processing one denomination at a time avoids counting different orders of the same coins as different combinations.

## Key takeaways

- Each coin denomination contributes a geometric-series factor.
- Updating amounts in increasing order allows repeated use of the current coin without counting orders.

## Further reading

- [Generating function — Wikipedia](https://en.wikipedia.org/wiki/Generating_function)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
