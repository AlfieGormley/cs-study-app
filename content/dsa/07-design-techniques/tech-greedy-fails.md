---
id: tech-greedy-fails
title: When greedy fails
level: advanced
minutes: 13
summary: Coin systems where greedy gives the wrong change, why fractional knapsack is greedy but 0/1 knapsack isn't, and a practical method for telling a greedy problem from a dynamic programming one.
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
        count += amount // c
        amount %= c
    return count if amount == 0 else None
```

The denomination sets {1, 2, 5, 10, 20, 50, 100, 200} and {1, 5, 10, 25}, familiar from UK and US coin examples, are **canonical**: greedy minimises coin count for every amount under unlimited supply. A cash drawer with limited stock is a different problem.

> [!note] Content gap
> The population-wide claim that most currencies were designed to be canonical is omitted because no supporting monetary-design survey is identified.

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

### The DP alternative

Instead of committing to one coin, consider *every* possible last coin and take the best. Whatever the last coin c is, the rest of the amount must itself be paid optimally:

```formula
B(a) = 1 + min_{c ≤ a} B(a − c)
B(0) = 0
B(6) = 1 + min(B(5), B(3), B(2))
B(6) = 1 + min(2, 1, 2) = 2
where
B(a): the fewest coins that make amount a (best[a] in the code); infinity if a can't be made
a: the amount to make, a whole number of at least 0
c: one coin denomination, a positive whole number
min_{c ≤ a}: the smallest value over every coin c no bigger than a
min: the smallest of its inputs
In words: the best way to pay a is one coin plus the best way to pay what is left, tried for every coin that fits; for coins {1, 3, 4}, 6 is best paid as 3 + 3.
```

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
    best = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                cand = best[a - c] + 1
                best[a] = min(best[a], cand)
    if best[amount] == INF:
        return None
    return best[amount]
```

For {1, 3, 4}, the table for amounts 0 to 6 is 0, 1, 2, 1, 1, 2, 2. The cost is one pass over the coins for each amount:

```formula
W = O(k + A × (k + 1)) = O(A × k)
M = O(A + k)
W ≈ 1,000 × 8 = 8,000
where
W: the unit-cost work, in basic steps, including reading the coins and filling the table
M: the storage used (the table plus the coin list)
k: the number of coin denominations (8 in the last line)
A: the target amount (1,000 in the last line); the simplified form assumes A and k are both at least 1
O: Big-O, grows no faster than this up to a constant factor
≈: approximately equal to
In words: every amount from 1 to A tries every coin once, so the work is about A times k: 8 UK denominations and £10.00 (1,000 pence) take about 8,000 steps.
```

It is correct for the stated positive-integer, unlimited-supply domain. The dynamic programming module develops this way of thinking in depth; here the point is the contrast. Greedy keeps **one** candidate per step; DP compares the last-coin alternatives for each amount, retaining the best value for that state.

### Testing a coin system

You don't have to test every amount. Kozen and Zaks (1994) showed that the smallest counterexample, if there is one, lies in a narrow window:

```formula
1 = c_1 < c_2 < … < c_m
c_3 + 1 < x < c_m + c_{m−1}
13 < x < 17
where
c_1: the smallest denomination, which must be 1
c_2: the second-smallest denomination
c_m: the largest denomination
c_{m−1}: the second-largest denomination
c_3: the third-smallest denomination
m: the number of distinct denominations, at least 3
x: the smallest amount where greedy uses more coins than necessary, if the system is non-canonical
…: and so on, in increasing order
In words: if greedy ever goes wrong, it first goes wrong somewhere between c_3 + 1 and the sum of the two largest coins, so only those amounts need checking; for {1, 5, 12} that is 14 to 16.
```

So for {1, 5, 12}, checking amounts below 17 suffices, and 15 is found. Pearson later gave a polynomial-time test.

## Fractional versus 0/1 knapsack

A knapsack holds a maximum total weight, its capacity W. The examples use positive integer weights, non-negative integer values and non-negative integer capacity. Items may be omitted; maximise the value carried.

### Fractional: greedy works

If you can take **part** of an item, sort by **value per unit weight** and take as much as possible of the best ratio first. The code uses exact rational arithmetic so near-equal ratios are not misordered by floating-point rounding.

```python
from fractions import Fraction

def fractional(items, cap):   # (w, v)
    items = list(items)
    if (type(cap) is not int or cap < 0
            or any(type(w) is not int
                   or w <= 0
                   or type(v) is not int
                   or v < 0
                   for w, v in items)):
        raise ValueError("item domain")
    total = Fraction(0)
    by_ratio = sorted(
        items,
        key=lambda x: Fraction(x[1], x[0]),
        reverse=True)
    for w, v in by_ratio:
        take = min(w, cap)
        total += Fraction(v * take, w)
        cap -= take
        if cap == 0:
            break
    return total
```

Exchange argument: if an optimal load holds some lower-ratio item while higher-ratio material is left behind, swap equal weights. Value goes up or stays the same. So filling by ratio is optimal. For n items, sorting takes O(n log n) ratio comparisons; exact rational arithmetic has additional operand-bit costs.

### 0/1: greedy fails

If each item is taken whole or not at all, ratio-greedy breaks. The classic example (from CLRS), capacity 50:

| Item | Weight | Value | Ratio |
|---|---|---|---|
| A | 10 | 60 | 6 |
| B | 20 | 100 | 5 |
| C | 30 | 120 | 4 |

```
fractional: A + B + 2/3 of C
          = 60 + 100 + 80   = 240
0/1 greedy: A + B (C won't fit)
          = 160, 20 kg wasted
0/1 best:   B + C           = 220
```

Greedy's high-ratio choice, A, wastes capacity that couldn't be filled afterwards. With whole items, *how well the pieces fit together* matters, and the value/weight rule does not capture that interaction.

0/1 knapsack is **NP-hard**: at least as hard as every problem in NP, so no algorithm is known that solves every instance in time polynomial in the size of the input (and none exists unless P = NP). The standard DP fills one table entry per capacity value for each item:

```formula
T = O(n × W)
T ≈ 100 × 50 = 5,000
T ≈ 100 × 5 × 10^9 = 5 × 10^11
where
T: the number of table updates the DP performs
n: the number of items (100 in the examples)
W: the capacity, as a number (50, then 5 × 10^9 in the examples)
O: Big-O, grows no faster than this up to a constant factor
≈: approximately equal to
10^9: one billion
10^11: one hundred billion
In words: the work grows with the capacity's numeric value, not with the number of digits needed to write it, so a capacity of 5 billion makes the table impractically large.
```

That makes it **pseudo-polynomial**: its storage and work depend on W’s numeric value, so whether it is practical depends on both n and W and the available resources.

```python
def knapsack01(items, cap):
    items = list(items)
    if (type(cap) is not int or cap < 0
            or any(type(w) is not int
                   or w <= 0
                   or type(v) is not int
                   or v < 0
                   for w, v in items)):
        raise ValueError("item domain")
    best = [0] * (cap + 1)
    for w, v in items:
        # go downwards so each item is
        # used at most once
        for c in range(cap, w - 1, -1):
            best[c] = max(best[c],
                          best[c - w] + v)
    return best[cap]
```

> [!tip] Greedy as an approximation
> Ratio-greedy alone can be arbitrarily bad: with a large capacity, a small item with a high ratio can block one big item that fills the whole knapsack. A small fix gives a guarantee of at least half the optimum.

For example:

```formula
w_1 = 1, v_1 = 2;   w_2 = M, v_2 = M
G = 2,   OPT = M,   M > 2
where
w_1: the weight of the small item
v_1: the value of the small item (ratio 2)
w_2: the weight of the big item, equal to the capacity
v_2: the value of the big item (ratio 1)
M: the capacity, any number greater than 2
G: the value ratio-greedy collects (it takes the small item, then the big one no longer fits)
OPT: the best possible value (the big item alone)
In words: greedy gets 2 while the optimum is M, so the gap can be made as large as you like.
```

The fix: for positive weights and non-negative values, first discard items heavier than capacity. Take the ratio-ordered whole-item prefix up to the first item that does not fit, and compare its value with the best single feasible item:

```formula
OPT ≤ G + v_next
max(G, v_max) ≥ (G + v_next) / 2
max(G, v_max) ≥ OPT / 2
where
OPT: the best possible 0/1 value
G: the value of the ratio-ordered prefix of whole items
v_next: the value of the first item that didn't fit
v_max: the value of the best single item that fits on its own (at least v_next)
max: the larger of its inputs
≤: at most
≥: at least
In words: the fractional optimum, which beats any 0/1 answer, is at most the prefix plus the whole next item; the larger of two numbers is at least their average, so the better of the prefix and the best single item gets at least half the optimum.
```

Continuing to fit later items can only improve that prefix value.

## Other places greedy breaks

- **Dijkstra with negative edges.** The settling variant of Dijkstra refuses to improve finalised vertices, assuming no later path can be cheaper. With edges A→B 2, A→C 3, C→B −2, it finalises B at 2, but A→C→B costs 1.
- **Nearest-neighbour TSP.** Always visiting the closest unvisited city produces tours that can be much longer than optimal.
- **Weighted interval scheduling.** Earliest finish maximises the count, not the total value.
- **Longest path.** Extending by the heaviest edge each step can walk into a dead end.

## How to tell greedy from DP

There is no mechanical test, but this process works well in practice and in interviews.

### 1. Hunt for a counterexample

Try tiny inputs designed to make the greedy choice bad: an item that is locally best but fits poorly, a coin that leaves an awkward remainder, a long interval that blocks several short ones. If you find one in a few minutes, stop: greedy is wrong.

### 2. Stress-test against brute force

If you can't break it by hand, let the computer try. Compare greedy against an exhaustive search on thousands of small random inputs:

```python
import random

def stress(trials=10_000):
    for _ in range(trials):
        coins = [1] + random.sample(
            range(2, 20), 2)
        amount = random.randint(1, 60)
        g = greedy_coins(coins, amount)
        d = min_coins(coins, amount)
        if g != d:
            return coins, amount, g, d
    return None
```

A possible counterexample is `([1, 7, 6], 18, 6, 3)`. The generator and random seed determine whether and when this test finds one; no trial-count or failure-rate guarantee is asserted. A clean run isn't proof, but a failure is conclusive.

### 3. Try to write the exchange argument

Take an optimal solution that doesn't make the greedy choice. Can you swap the greedy choice in without making it worse? A valid exchange proof for every remaining subproblem establishes correctness; an intuitive swap that works only on examples does not. If a proposed swap makes the solution invalid, that particular proof attempt fails. To disprove the greedy rule, exhibit an input where its final solution is worse than a feasible alternative; a failed exchange attempt alone is insufficient.

### 4. Read the structure of the problem

| Signal | Suggests |
|---|---|
| Can take fractions | Greedy |
| Choice leaves a "clean" subproblem | Greedy |
| Whole items, a hard capacity | DP |
| Choice changes what's possible later | DP |
| Count of ways, or "min/max over all" | DP |
| Matroid structure (e.g. spanning trees) | Greedy |

These are prompts for investigation, not classification rules. Greedy interval scheduling also changes available future choices, and equal-weight 0/1 knapsack is solvable greedily. What matters is whether the proposed choice is provably safe. A failed rule does not rule out another greedy algorithm; DP, branch and bound, exhaustive search and other methods have different tradeoffs.

## Key takeaways
- Greedy fails when a locally best choice closes off options the global optimum needed.
- Under unlimited supply and positive integer denominations, greedy is optimal for canonical systems; the amount DP also handles non-canonical systems.
- Fractional knapsack is solved by greedy on value/weight; general 0/1 knapsack is NP-hard and has a pseudo-polynomial DP, among other exact and approximate approaches.
- Break a greedy rule with small counterexamples, then stress-test against brute force before trusting it.
- If you can't write an exchange argument, suspect DP; greedy may still be a useful approximation.

## Further reading
- [Change-making problem — Wikipedia](https://en.wikipedia.org/wiki/Change-making_problem)
- [Knapsack problem — Wikipedia](https://en.wikipedia.org/wiki/Knapsack_problem)
- [Continuous knapsack problem — Wikipedia](https://en.wikipedia.org/wiki/Continuous_knapsack_problem)
- [Jeff Erickson, Algorithms, chapter 4: Greedy Algorithms (PDF)](https://jeffe.cs.illinois.edu/teaching/algorithms/book/04-greedy.pdf)
- [Jeff Erickson, Algorithms, chapter 3: Dynamic Programming (PDF)](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
- [Optimal substructure — Wikipedia](https://en.wikipedia.org/wiki/Optimal_substructure)
