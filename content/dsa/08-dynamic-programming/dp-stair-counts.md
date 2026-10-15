---
id: dp-stair-counts
title: Count ordered staircase routes
level: intermediate
minutes: 4
summary: Group routes by their final allowed step.
sourceLesson: dp-1d
---

A 1-D DP has a state described by a single index or amount: `dp[i]` for a position in an array, or `dp[a]` for an amount of money. These problems are the best place to practise the method, because the state is obvious and all the difficulty is in the recurrence.

## Climbing stairs

> You can climb 1 or 2 steps at a time. How many distinct ways are there to reach step n?

- **State**: `ways[i]` records number of ways to reach step i.
- **Recurrence**: the last move was a 1-step (from i − 1) or a 2-step (from i − 2). Those are disjoint (no route is counted in both), so add them.
- **Base**: `ways[0] = 1` (one way to stand still), `ways[1] = 1`.

```formula
ways[0] = 1
ways[1] = 1
ways[i] = ways[i − 1] + ways[i − 2]
ways[5] = ways[4] + ways[3] = 5 + 3 = 8
where
ways[i]: the number of different sequences of 1-steps and 2-steps that end exactly on step i
i: the step number, 0 at the bottom; the rule applies for i of 2 or more
ways[i − 1]: routes whose last move was a single step from i − 1
ways[i − 2]: routes whose last move was a double step from i − 2
In words: every route to step i ends with either a 1-step or a 2-step, so the count is the routes to the step below plus the routes to the step two below.
```

```python
def climb(n):
    # Reject values outside the recurrence.
    if type(n) is not int or n < 0:
        raise ValueError("nonnegative n")
    a, b = 1, 1  # ways[0], ways[1]
    for _ in range(n - 1):
        # Advance the two retained values
        # together.
        a, b = b, a + b
    return b
```

The call `climb(5)` returns 8. The counts are Fibonacci shifted by one position:

```formula
ways[i] = F(i + 1)
ways[5] = F(6) = 8
where
ways[i]: the number of ordered routes to step i using steps of size one or two
i: a nonnegative whole-number stair position
F(k): the Fibonacci number at position k, counting from values zero and one
k: a Fibonacci position
In words: Staircase counts start with one empty route and one single-step route, so they are the next Fibonacci number.
```

If you can take steps of size 1, 2 or 3, the recurrence gains a third term. In general, for any set of allowed step sizes:

```formula
ways[i] = Σ ways[i − s]   for s ∈ S
where
ways[i]: the number of ordered step sequences that reach step i exactly
i: a positive step number; zero has one empty route and negative positions have none
S: the set of allowed step sizes, distinct positive whole numbers, for example {1, 2, 3}
s: one allowed step size from S
∈: "is a member of", so s ∈ S means s is one of the sizes in S
Σ: sum, add up the term for every s in S
In words: the routes to step i are grouped by their last step size, so add up the routes to each step that is one allowed jump below i.
```

A remainder below step zero counts as zero routes. With step sizes one, two and three:

```formula
S = {1, 2, 3}
ways[3] = ways[2] + ways[1] + ways[0]
ways[3] = 2 + 1 + 1 = 4
where
S: the allowed positive step sizes
ways[i]: the count of ordered routes to step i with sizes from S
i: a nonnegative stair position
In words: Three possible final step sizes give four routes to the third stair.
```

## Key takeaways
- Group routes by their final allowed step.
- The empty climb counts as one route; overshooting backwards counts as none.

## Further reading
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
- [MIT algorithms course](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/)
