---
id: dp-held-karp-states
title: A visited-set state for travelling salesman
level: advanced
minutes: 5
summary: Visited cities and current city determine the remaining tour choices.
sourceLesson: dp-advanced
---

### Held–Karp: the travelling salesman

> Given distances between n cities, find the shortest tour that starts at city 0, visits every city exactly once, and returns.

Brute force fixes city 0 as the start and tries every order of the rest:

```formula
tours = (n − 1)!
(20 − 1)! = 19! ≈ 1.2 × 10^17
where
tours: the number of orderings brute force must check
n: the number of cities; the tour-closing recurrence applies for at least two cities, while zero or one city returns zero
!: factorial, the product of every whole number from 1 up to the number (4! = 1 × 2 × 3 × 4 = 24)
≈: approximately equal to
In words: after fixing the start, the remaining n − 1 cities can be visited in (n − 1)! different orders.
```

That is 120 quadrillion tours for just 20 cities. Hopeless.

The key observation: once you've visited a set of cities and are standing at city j, the **order** you visited them in no longer matters for the rest of the tour. Only the set and the current city do. That's the state.

**State**: `dp[mask][j]` records length of the shortest path that starts at 0, visits exactly the cities in `mask`, and ends at j.

**Recurrence**: extend a path by one unvisited city k. Written "pulling" from the state before k was added:

```formula
dp[S ∪ {k}][k] = min(dp[S][j] + d[j][k])
   for j ∈ S, k ∉ S
dp[{0}][0] = 0
best = min(dp[F][j] + d[j][0])
   for j ≠ 0
where
dp[S][j]: the length of the shortest path that starts at city 0, visits exactly the cities in the set S, and ends at city j
S: a set of cities that includes 0 (stored as the bitmask `mask`)
S ∪ {k}: the set S with city k added (mask | 1 << k in code)
∪: union, combining two sets
{0}: the set containing only city 0 (mask 1)
j: the city where the shorter path ended, a member of S
k: the newly added city, not yet in S
∈: "is a member of"; ∉: "is not a member of"
d[j][k]: the distance from city j to city k
min: the smallest value over all the allowed choices
F: the full set of every city (the bitmask full = 2^n − 1)
n: the number of cities; the tour-closing recurrence applies for at least two cities, while zero or one city returns zero
best: the length of the shortest complete tour
≠: not equal to
In words: the cheapest way to have visited S plus k, ending at k, is the cheapest way to have visited S ending at some j, plus the hop from j to k; the tour closes with the hop back to city 0.
```

**Base**: `dp[1][0] = 0` (only city 0 visited, standing at 0). The code below "pushes" forwards instead: from each finished state it tries every unvisited k and keeps the minimum, which computes the same values.

```python
def held_karp(d):
    n = len(d)
    if any(len(row) != n for row in d):
        raise ValueError("square matrix")
    if any(type(w) is not int
           for row in d for w in row):
        raise ValueError("integer costs")
    if n <= 1:
        return 0
    INF = float('inf')
    # One set bit per city means all
    # visited.
    full = (1 << n) - 1
    dp = [[INF] * n for _ in range(1 << n)]
    # Start with only city zero visited.
    dp[1][0] = 0
    for mask in range(1 << n):
        if not mask & 1:
            continue  # tours start at 0
        for j in range(n):
            cur = dp[mask][j]
            # Skip unreachable allocated
            # table states.
            if cur == INF:
                continue
            for k in range(n):
                # A tour may not visit this
                # city again.
                if mask & (1 << k):
                    continue
                # Add one city; the numeric
                # mask increases.
                nm = mask | (1 << k)
                c = cur + d[j][k]
                # Keep the cheapest path to
                # this state.
                if c < dp[nm][k]:
                    dp[nm][k] = c
    return min(dp[full][j] + d[j][0]
               for j in range(1, n))
```

Why does increasing `mask` order work? Adding a city sets a bit, so the new mask is numerically larger. Every state is final before anything reads it.

For the four-city distance matrix

```
     0   1   2   3
0    0  10  15  20
1   10   0  35  25
2   15  35   0  30
3   20  25  30   0
```

it returns 80 (0 → 1 → 3 → 2 → 0: 10 + 25 + 30 + 15).

## Key takeaways
- Visited cities and current city determine the remaining tour choices.
- Adding a bit moves to a larger numeric mask.
- Close the full-set path by returning to city zero.

## Further reading
- [Held–Karp algorithm](https://en.wikipedia.org/wiki/Held%E2%80%93Karp_algorithm)
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
