---
id: dp-stock-cooldown
title: Add a holding state for stock trading
level: basic
minutes: 5
summary: Day alone cannot describe both holding and empty-handed histories.
sourceLesson: dp-method
---

A position-only state is useful only when the future needs no extra information. Stock trading demonstrates a small flag that changes which actions are available.

## Worked example 2: when the state needs more than an index

> You know a stock's price on each day. You may buy and sell as often as you like, holding at most one share, but after selling you must wait one day before buying again. Maximise profit.

Try `dp[i]` records best profit from day i onwards. It doesn't work: whether you can sell on day i depends on whether you're **holding** a share. The future depends on more than i, so add that to the state.

**State.** `f(i, holding)` records best profit from day i onwards, given whether we hold a share.

**Recurrence.**

- Holding: either keep it (`f(i+1, True)`) or sell (`price[i] + f(i+2, False)`; the `+2` skips the cooldown day).
- Not holding: either wait (`f(i+1, False)`) or buy (`-price[i] + f(i+1, True)`).

```formula
f(i, True) = max(f(i + 1, True),
  p_i + f(i + 2, False))
f(i, False) = max(f(i + 1, False),
  −p_i + f(i + 1, True))
where
f(i, h): the best profit obtainable from day i onwards, where h says whether we hold a share at the start of day i
i: the day number, starting at 0
h: the holding flag, True or False
True: we hold a share
False: we hold no share
p_i: the price of the share on day i (price[i] in the code), in money units
max: the larger of the two options
In words: on each day, either do nothing and move to the next day, or act (sell, then skip a cooldown day; or buy, paying today's price), and keep whichever gives more profit.
```

Selling adds the price to the profit; buying subtracts it, which is why the buy option has −p_i.

**Domain and base case.** Prices are nonnegative integers. All bought shares must be sold, so once the days run out (i is n or more, where n is the number of days):

```formula
f(i, False) = 0   for i ≥ n
f(i, True) = −∞   for i ≥ n
where
f(i, h): the best profit from day i onwards with holding flag h
i: the day number
n: the number of days with a price
True: still holding a share
False: holding nothing
−∞: negative infinity, a value worse than any real profit, so this state is never chosen
≥: greater than or equal to
In words: after the last day, finishing empty-handed adds nothing, and finishing while still holding a share is forbidden.
```

The `−∞` explicitly excludes unfinished transactions, including zero-price ties.

```python
from functools import cache

def max_profit(prices):
    prices = tuple(prices)
    if any(type(p) is not int or p < 0
           for p in prices):
        raise ValueError("price domain")
    n = len(prices)

    # Repeated arguments reuse stored
    # answers.
    @cache
    def f(i, holding):
        # Reject a share never sold by the
        # end.
        if i >= n:
            return (-float("inf")
                    if holding else 0)
        # Waiting preserves the holding
        # state.
        skip = f(i + 1, holding)
        if holding:
            # Selling skips the following
            # cooldown day.
            sell = prices[i] + f(i+2, False)
            return max(skip, sell)
        # Buying pays now and enables later
        # sales.
        buy = -prices[i] + f(i + 1, True)
        return max(skip, buy)

    return f(0, False)
```

For prices `[1, 2, 3, 0, 2]` this returns 3. The tempting plan, buy at 1 and sell at 3 (+2), forces a cooldown on the day priced 0, leaving only one day: total 2. The better plan is buy at 1, sell at 2 (+1), cool down on the day priced 3, buy at 0, sell at 2 (+2): total 3. Spotting that by hand is fiddly, which is exactly why you let the recurrence try every option.

**Complexity.** With n days, there are O(n + 1) states (two per day, plus the end) with O(1) arithmetic operations each, so O(n) time. The shown version keeps O(n) cached states, prices and recursion frames. An iterative hold/sold/rest version can use O(1) value slots; integer bit costs remain additional.

> [!tip] The state machine view
> Many "sequence with modes" problems are DP over (position, mode). Draw the modes as boxes and the allowed moves between them as arrows; each arrow is a term in the recurrence.

```
 rest --buy--> hold --sell--> sold
  ^ |           ^ |             |
  +-+ wait      +-+ keep        |
  ^                             |
  +-------- cooldown -----------+
```

## A transaction limit changes the state

Without a cooldown, a cap on completed buy-sell transactions requires another parameter: the number still available. Keep the holding flag too. Counting a transaction when buying consumes one allowance; selling then uses the already-reserved allowance. Each day and allowance has two holding modes, with constant candidate actions per state. Finish without an unsold share, as in the cooldown version.

## Pitfalls

1. **Under-specified state.** The stock problem without `holding`. Symptom: a recurrence that needs to "remember" something it can't see.
2. **Over-specified state.** Including the full path or a list in the key. It explodes the number of states and usually means you haven't found what really matters.
3. **Double counting.** In "how many ways" problems the options must be disjoint. Counting coin combinations versus orderings is the classic trap (the later unit “Count combinations or ordered sequences”).
4. **Wrong sentinel value.** Using `0` for "impossible" in a minimisation makes impossible states look free. Use `float('inf')`.
5. **Order bugs.** Bottom-up code that reads a cell before it's filled. If unsure, write it top-down first and convert.

## Key takeaways
- Day alone cannot describe both holding and empty-handed histories.
- Selling jumps over the cooldown day.
- Forbid unfinished trades with a negative-infinity terminal value.

## Further reading
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
- [MIT algorithms course](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/)
