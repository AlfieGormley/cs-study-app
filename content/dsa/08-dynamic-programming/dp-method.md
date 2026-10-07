---
id: dp-method
title: A method for solving DP problems
level: basic
minutes: 12
summary: A five-step recipe (state, recurrence, base cases, evaluation order, reconstruction) applied to word break and a stock-trading state machine.
---

Defining the state and recurrence is often the hardest part of a DP problem. A systematic method helps make those decisions explicit.

Here are five questions to answer, in order. Write the answers down in plain English before you write any code.

1. **State**: what does `dp[...]` mean, exactly?
2. **Recurrence**: how is one state computed from smaller ones?
3. **Base cases**: which states can be answered directly?
4. **Order**: in what order must states be evaluated?
5. **Answer and reconstruction**: which state holds the answer, and how do you recover the actual choices, not just the number?

Then add a sixth, quick step: **complexity** = number of states × work per state.

## Step 1: define the state

The state is the set of parameters that describes a subproblem. It must capture **everything the future depends on**. Extra information can increase cost even when the state remains correct.

A good test: "If I know only these values, can I solve the rest of the problem optimally without knowing how I got here?" If yes, you have a valid state. If the answer also depends on something else (a previous choice, a remaining budget), that something must join the state.

Common state shapes:

| Input | Typical state |
|---|---|
| One sequence | prefix `i` or suffix `i` |
| Two sequences | pair `(i, j)` |
| Sequence, ranges | interval `(i, j)` |
| Items + budget | `(i, capacity)` |
| Tree | node `v` (+ flag) |
| Small set | bitmask |

Write the definition as a full sentence: "`ok[i]` is True if the suffix `s[i:]` can be split into dictionary words." Vague definitions ("`dp[i]` is the answer at i") are the root of most wrong recurrences.

## Step 2: the recurrence

Ask: **what is the first (or last) decision**, and what are the options? Each option leads to a smaller subproblem. Combine the results with whatever the question asks for:

- "minimum/maximum" → `min` / `max` over options
- "how many ways" → **sum** over options (they must be disjoint, or you'll double-count)
- "is it possible" → **or** over options

## Step 3: base cases

The smallest states, where no decision is left: an empty string, zero capacity, a single element. Also decide what an **impossible** state returns: `0` for counting, `False` for feasibility, `+∞` for minimisation, `−∞` for maximisation.

## Step 4: evaluation order

Every state depends on some others. For a finite recurrence evaluated once per state, those dependencies must form a **directed acyclic graph**. Cyclic Bellman equations can require fixed-point methods such as value iteration; plain memoisation does not solve a dependency cycle. Bottom-up evaluation is just a topological order of that DAG.

- If `dp[i]` depends on larger `i`, loop `i` downwards.
- If `dp[i][j]` depends on `[i-1][j]` and `[i][j-1]`, loop rows then columns, both upwards.
- If an interval depends on shorter intervals, loop by length.

Memoisation finds the order automatically, which is why it's a good first draft.

## Step 5: answer and reconstruction

Say which state is the answer (`dp[0]`, `dp[n]`, `max(dp)`, ...). Then, if the problem wants the actual solution, either:

- **Store the choice** that achieved each state's best value, in a parallel array, and follow it from the answer state; or
- **Recompute**: walk from the answer state and, at each step, check which option reproduces the stored value.

Following stored choices takes time proportional to the number of reconstruction steps plus output construction. Rechecking alternatives can cost more: include the number of candidates examined at each step.

## Worked example 1: word break

> Given a string `s` and nonempty dictionary words, can `s` be split into a sequence of dictionary words? If so, return one split.

**State.** `ok[i]` is True if the suffix `s[i:]` can be split into words.

**Recurrence.** The first decision is which word starts at position i. For each word `w`, if `s` has `w` at position i and the rest can be split, we're done:

```
ok[i] = any(s.startswith(w, i)
            and ok[i + len(w)]
            for w in words)
```

**Base case.** `ok[n] = True`: the empty suffix is trivially split (into zero words).

**Order.** `ok[i]` depends on larger indices, so loop `i` from `n − 1` down to 0.

**Answer.** `ok[0]`. To reconstruct, store `nxt[i]`, the end of the word chosen at i.

```python
def word_break(s, words):
    words = tuple(words)
    if any(not isinstance(w, str) or not w
           for w in words):
        raise ValueError("nonempty words")
    n = len(s)
    ok = [False] * (n + 1)
    nxt = [None] * (n + 1)
    ok[n] = True
    for i in range(n - 1, -1, -1):
        for w in words:
            j = i + len(w)
            if s.startswith(w, i) and ok[j]:
                ok[i], nxt[i] = True, j
                break
    if not ok[0]:
        return None
    out, i = [], 0
    while i < n:
        out.append(s[i:nxt[i]])
        i = nxt[i]
    return out
```

Trace `s = "catsanddog"`, words `["cat", "cats", "and", "sand", "dog"]`:

```
i  suffix       ok   via
10 ""           T    base
7  "dog"        T    dog -> 10
6  "ddog"       F
4  "anddog"     T    and -> 7
3  "sanddog"    T    sand -> 7
0  "catsanddog" T    cat -> 3
```

(Positions 1, 2, 5, 8 and 9 are False.) Following `nxt` from 0 gives `["cat", "sand", "dog"]`. With "cats" listed first you'd get `["cats", "and", "dog"]`; both are valid.

**Complexity.** n + 1 states, each trying W words of length up to L: O(n · W · L + n + W) worst-case character/transition work and O(n + W) auxiliary slots for nonempty words, including materialising the dictionary references; reconstruction copies at most n characters. Compare with brute force, which can explore exponentially many splits of a string like `"aaaa...ab"`.

## Worked example 2: when the state needs more than an index

> You know a stock's price on each day. You may buy and sell as often as you like, holding at most one share, but after selling you must wait one day before buying again. Maximise profit.

Try `dp[i]` = best profit from day i onwards. It doesn't work: whether you can sell on day i depends on whether you're **holding** a share. The future depends on more than i, so add that to the state.

**State.** `f(i, holding)` = best profit from day i onwards, given whether we hold a share.

**Recurrence.**

- Holding: either keep it (`f(i+1, True)`) or sell (`price[i] + f(i+2, False)`; the `+2` skips the cooldown day).
- Not holding: either wait (`f(i+1, False)`) or buy (`−price[i] + f(i+1, True)`).

**Domain and base case.** Prices are nonnegative integers. All bought shares must be sold: for i ≥ n, `f(i, False) = 0` and `f(i, True) = −∞`. This explicitly excludes unfinished transactions, including zero-price ties.

```python
from functools import cache

def max_profit(prices):
    prices = tuple(prices)
    if any(type(p) is not int or p < 0
           for p in prices):
        raise ValueError("price domain")
    n = len(prices)

    @cache
    def f(i, holding):
        if i >= n:
            return (-float("inf")
                    if holding else 0)
        skip = f(i + 1, holding)
        if holding:
            sell = prices[i] + f(i+2, False)
            return max(skip, sell)
        buy = -prices[i] + f(i + 1, True)
        return max(skip, buy)

    return f(0, False)
```

For prices `[1, 2, 3, 0, 2]` this returns 3. The tempting plan, buy at 1 and sell at 3 (+2), forces a cooldown on the day priced 0, leaving only one day: total 2. The better plan is buy at 1, sell at 2 (+1), cool down on the day priced 3, buy at 0, sell at 2 (+2): total 3. Spotting that by hand is fiddly, which is exactly why you let the recurrence try every option.

**Complexity.** O(n + 1) states with O(1) arithmetic operations each. The shown version keeps O(n) cached states, prices and recursion frames. An iterative hold/sold/rest version can use O(1) value slots; integer bit costs remain additional.

> [!tip] The state machine view
> Many "sequence with modes" problems are DP over (position, mode). Draw the modes as boxes and the allowed moves between them as arrows; each arrow is a term in the recurrence.

```
 rest --buy--> hold --sell--> sold
  ^ |           ^ |             |
  +-+ wait      +-+ keep        |
  ^                             |
  +-------- cooldown -----------+
```

## Choosing between prefix and suffix states

Both work for most sequence problems. Pick whichever makes the recurrence read naturally:

- **Suffix** (`f(i)` = answer for `s[i:]`): the first decision is "what do I do at i?". It matches top-down recursion well.
- **Prefix** (`dp[i]` = answer for `s[:i]`): the last decision is "what was the final piece?". It matches left-to-right loops.

## Pitfalls

1. **Under-specified state.** The stock problem without `holding`. Symptom: a recurrence that needs to "remember" something it can't see.
2. **Over-specified state.** Including the full path or a list in the key. It explodes the number of states and usually means you haven't found what really matters.
3. **Double counting.** In "how many ways" problems the options must be disjoint. Counting coin combinations versus orderings is the classic trap (lesson 3).
4. **Wrong sentinel.** Using `0` for "impossible" in a minimisation makes impossible states look free. Use `float('inf')`.
5. **Order bugs.** Bottom-up code that reads a cell before it's filled. If unsure, write it top-down first and convert.

## Key takeaways
- Answer five questions before coding: state, recurrence, base cases, order, answer/reconstruction. Then count states × work.
- The state must contain everything the future depends on. If a recurrence needs to remember a past choice, add it to the state.
- Combine options with min/max (optimise), sum (count, over disjoint options) or any (decide).
- Bottom-up order is a topological order of the dependency DAG.
- Reconstruct by storing the winning choice per state, or by re-checking which option reproduces the stored value.

## Further reading
- [Jeff Erickson, Algorithms, ch. 3: Dynamic Programming (PDF)](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
- [Dynamic programming — Wikipedia](https://en.wikipedia.org/wiki/Dynamic_programming)
- [Bellman equation — Wikipedia](https://en.wikipedia.org/wiki/Bellman_equation)
- [MIT 6.006 Introduction to Algorithms (OCW)](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/)
