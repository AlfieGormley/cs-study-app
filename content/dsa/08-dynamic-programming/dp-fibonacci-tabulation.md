---
id: dp-fibonacci-tabulation
title: Tables, rolling values and DP cost
level: basic
minutes: 3
summary: Bottom-up evaluation fills dependencies before reading them.
sourceLesson: dp-intro
---

Here n is the nonnegative requested Fibonacci position. Fibonacci at a position uses only the two preceding values. This unit changes how those values are evaluated and stored, while preserving the same answer.

### Fix 2: tabulation (bottom-up)

Turn the recursion inside out. Fill a table from the smallest subproblem upwards, so that every value you need has already been computed.

```python
def fib(n):
    # Reject values outside the recurrence.
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative n")
    # The first two positions are base
    # cases.
    if n < 2:
        return n
    table = [0] * (n + 1)
    table[1] = 1
    # Both dependencies are already filled.
    for i in range(2, n + 1):
        table[i] = table[i-1] + table[i-2]
    return table[n]
```

Same O(n) time, same O(n) space, but no recursion.

### Fix 3: keep only what you need

`table[i]` only looks back two entries, so the rest of the table is dead weight. Keep two variables:

```python
def fib(n):
    # Reject values outside the recurrence.
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative n")
    a, b = 0, 1  # F(0), F(1)
    for _ in range(n):
        # Advance the two retained values
        # together.
        a, b = b, a + b
    return a
```

**O(n) additions, O(1) integer slots.** With Python’s exact integers, F(n) has Θ(n) bits: this loop uses O(n) bits and O(n²) bit work, while retaining the whole Fibonacci table uses Θ(n²) bits. This "keep only the last few rows" trick is a standard DP space optimisation you'll see again for grids and knapsack.

The table counts unit-cost arithmetic and integer slots rather than bits. In its naive-recursion row, φ is the golden ratio, about 1.618.

| Version | Unit-cost work | Extra slots |
|---|---|---|
| Naive recursion | O(φⁿ) | O(n) stack |
| Memoised | O(n) | O(n) |
| Tabulated | O(n) | O(n) |
| Two variables | O(n) | O(1) |

This gives the rule of thumb for the cost of any DP. The exact cost is the work summed over every state you evaluate; multiplying the number of states by the most work any one state needs gives a quick upper bound:

```formula
T ≤ S w_max
T_fib = O(n + 1)
where
T: the total running time of the DP, in basic steps
S: the number of distinct states (subproblems) evaluated
w_max: the most work any single state does, not counting the states it looks up
≤: less than or equal to
T_fib: the running time of memoised or tabulated Fibonacci
n: the nonnegative Fibonacci position asked for; there are at most n + 1 states, each using bounded unit-cost work
O(...): Big-O, an upper growth bound up to a constant factor; for positive positions this is conventionally written O(n)
In words: count the subproblems, multiply by the work each one does on its own, and you have an upper bound on the running time.
```

> [!tip] What the formula leaves out
> Add any preprocessing, the work to reconstruct the chosen solution, and the cost of arithmetic on very large numbers (operand bits) when they matter.

## Key takeaways
- Bottom-up evaluation fills dependencies before reading them.
- Two integer slots suffice for Fibonacci, but their bit sizes grow.
- Count states and transition work, including preprocessing and reconstruction.

## Further reading
- [Python caching](https://docs.python.org/3/library/functools.html)
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
