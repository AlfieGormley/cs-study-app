---
id: tech-greedy-fails-diagnosis
title: Breaking and proving greedy rules
level: advanced
minutes: 3
sourceLesson: tech-greedy-fails
summary: One concrete counterexample disproves a rule; a clean random run does not prove it.
---

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
        # A verified mismatch disproves this
        # greedy rule.
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
- One concrete counterexample disproves a rule; a clean random run does not prove it.
- Structural hints guide investigation, while valid exchange proofs establish correctness.

## Further reading
- [Greedy algorithms — Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/book/04-greedy.pdf)
- [Dynamic programming — Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
