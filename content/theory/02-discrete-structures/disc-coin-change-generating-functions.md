---
id: disc-coin-change-generating-functions
title: "Coin change as generating-function multiplication"
level: intermediate
minutes: 3
summary: "Each coin denomination contributes a geometric-series factor."
sourceLesson: disc-inclusion-recurrences
---

### Example: making change

How many ways can you make n pence from 1p, 2p and 5p coins (order doesn't matter)? Any number of 1p coins is allowed, with one way to use each number, which is the geometric series. 2p coins can only make even amounts, and 5p coins multiples of 5. Each term in the product picks one power from each factor, so the coefficient of xⁿ counts the combinations:

```formula
G(x) = 1 / ((1 − x) × (1 − x^2) × (1 − x^5))
1 / (1 − x^2) = 1 + x^2 + x^4 + …
1 / (1 − x^5) = 1 + x^5 + x^10 + …
where
G(x): the generating function for making change; the coefficient of x^n is the number of ways to make n pence
x: the placeholder variable; x^k stands for k pence
1 − x, 1 − x^2, 1 − x^5: one factor per coin; 1 / (1 − x^c) lists the amounts 0, c, 2c, … that coins worth c pence can make
…: and so on forever
In words: multiply one series per coin; the number in front of x^10 counts the ways to make 10p, which is 10.
```

Multiplying the polynomials (truncated at degree n) is precisely the classic coin-change dynamic programme. In this code, n is a non-negative integer and coins contains distinct positive integer denominations:

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

The inner loop multiplies the series in w by one coin's factor. Because w[v − c] has already been updated when w[v] uses it, the loop computes:

```formula
w′(x) = w(x) + x^c × w′(x)
w′(x) = w(x) / (1 − x^c)
where
w(x): the generating function held in the list w before this coin's loop: w[v] is the coefficient of x^v
w′(x): the same list after the loop (the prime mark means "new")
c: the value of the current coin, in pence
x^c: shifting every coefficient up c places, which is what w[v - c] does
In words: the new count for v pence is the old count plus the new count for v − c pence (use at least one more of this coin), which is division by 1 − x^c.
```

## Key takeaways

- Each coin denomination contributes a geometric-series factor.
- Updating amounts in increasing order allows repeated use of the current coin without counting orders.

## Further reading

- [Generating function — Wikipedia](https://en.wikipedia.org/wiki/Generating_function)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
