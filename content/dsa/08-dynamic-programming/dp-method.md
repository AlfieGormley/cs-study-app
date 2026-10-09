---
id: dp-method
title: A method for solving DP problems
level: basic
minutes: 15
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

The smallest states, where no decision is left: an empty string, a zero weight limit, a single element. Also decide what an **impossible** state returns: `0` for counting, `False` for feasibility, `+∞` (positive infinity, a value worse than any real cost) for minimisation, and `−∞` (negative infinity, worse than any real profit) for maximisation. In Python these are `float('inf')` and `-float('inf')`. A `min` never picks `+∞` when a real option exists, and a `max` never picks `−∞`, so impossible options drop out automatically.

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

```formula
ok[i] = OR of ok[i + |w|]
  for each w with m(w, i)
ok[n] = True
where
ok[i]: True if the suffix of s starting at position i can be split into dictionary words, False otherwise
i: a position in s, from 0 (the start) to n (just past the end)
w: one dictionary word
m(w, i): True if the word w appears in s starting exactly at position i (s.startswith(w, i) in Python)
|w|: the length of w, in characters
OR: logical or, True if at least one of the values is True (False if there are none)
s: the input string
n: the length of s, in characters
True: the Boolean value "yes"
In words: the suffix from i can be split if some dictionary word matches at i and the rest after that word can also be split.
```

The same rule in Python:

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

(Positions 1, 2, 5, 8 and 9 are False.) Following `nxt[i]` from i = 0 gives `["cat", "sand", "dog"]`. With "cats" listed first you'd get `["cats", "and", "dog"]`; both are valid.

**Complexity.** Count states and the work per state:

```formula
T = O(n × W × L + n + W)
M = O(n + W)
where
T: the worst-case running time, counting character comparisons and table steps
M: the extra memory used, in slots (table entries and word references)
n: the length of the string s, in characters; there are n + 1 states
W: the number of words in the dictionary
L: the length of the longest dictionary word, in characters
O(...): Big-O, growing at most in proportion to the expression inside
In words: each of the n + 1 positions tries all W words, and checking a word costs up to L character comparisons.
```

For example, a 1,000-character string with 500 words of up to 10 characters costs at most about 1,000 × 500 × 10 = 5 million character comparisons. The `+ n + W` terms cover setting up the table and copying the word list; reconstruction copies at most n characters. Compare with brute force, which can explore exponentially many splits of a string like `"aaaa...ab"`.

## Worked example 2: when the state needs more than an index

> You know a stock's price on each day. You may buy and sell as often as you like, holding at most one share, but after selling you must wait one day before buying again. Maximise profit.

Try `dp[i]` = best profit from day i onwards. It doesn't work: whether you can sell on day i depends on whether you're **holding** a share. The future depends on more than i, so add that to the state.

**State.** `f(i, holding)` = best profit from day i onwards, given whether we hold a share.

**Recurrence.**

- Holding: either keep it (`f(i+1, True)`) or sell (`price[i] + f(i+2, False)`; the `+2` skips the cooldown day).
- Not holding: either wait (`f(i+1, False)`) or buy (`−price[i] + f(i+1, True)`).

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

## Choosing between prefix and suffix states

Both work for most sequence problems. Pick whichever makes the recurrence read naturally:

- **Suffix** (`f(i)` = answer for `s[i:]`): the first decision is "what do I do at i?". It matches top-down recursion well.
- **Prefix** (`dp[i]` = answer for `s[:i]`): the last decision is "what was the final piece?". It matches left-to-right loops.

## Pitfalls

1. **Under-specified state.** The stock problem without `holding`. Symptom: a recurrence that needs to "remember" something it can't see.
2. **Over-specified state.** Including the full path or a list in the key. It explodes the number of states and usually means you haven't found what really matters.
3. **Double counting.** In "how many ways" problems the options must be disjoint. Counting coin combinations versus orderings is the classic trap (lesson 3).
4. **Wrong sentinel value.** Using `0` for "impossible" in a minimisation makes impossible states look free. Use `float('inf')`.
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
