---
id: dp-advanced
title: Advanced DP and spotting DP problems
level: advanced
minutes: 16
summary: Bitmask DP and Held–Karp for the travelling salesman, digit DP for counting numbers with digit constraints, DP over DAGs as the unifying view, and how to recognise a DP problem from its constraints.
---

Every DP so far has had states indexed by positions, lengths or capacities. This lesson covers three less obvious state spaces, then ties everything together with one idea: **a finite, acyclic DP can be evaluated over a DAG of states**. It ends with a practical checklist for spotting DP in an interview.

## Bitmask DP

When the state needs to know **which items from a small set have been used**, encode that set as the bits of an integer. With n items there are 2ⁿ subsets, so practical limits depend on the number of dimensions, transitions, representation and available resources; the following table shows growth, not a hardware guarantee.

| n | 2ⁿ | n · 2ⁿ | n² · 2ⁿ |
|---|---|---|---|
| 10 | 1,024 | ~10⁴ | ~10⁵ |
| 16 | 65,536 | ~10⁶ | ~1.7 × 10⁷ |
| 20 | ~10⁶ | ~2 × 10⁷ | ~4 × 10⁸ |
| 25 | ~3.4 × 10⁷ | ~8 × 10⁸ | ~2 × 10¹⁰ |

The bit operations you need:

```python
mask & (1 << j)     # is j in the set?
mask | (1 << j)     # add j
mask & ~(1 << j)    # remove j
(1 << n) - 1        # the full set
bin(mask).count('1')  # set size
```

### Held–Karp: the travelling salesman

> Given distances between n cities, find the shortest tour that starts at city 0, visits every city exactly once, and returns.

Brute force tries (n − 1)! orderings: 19! ≈ 1.2 × 10¹⁷ for n = 20. Hopeless.

The key observation: once you've visited a set of cities and are standing at city j, the **order** you visited them in no longer matters for the rest of the tour. Only the set and the current city do. That's the state.

**State**: `dp[mask][j]` = length of the shortest path that starts at 0, visits exactly the cities in `mask`, and ends at j.

**Recurrence**: extend a path by one unvisited city k:

```
dp[mask | 1<<k][k] = min(...,
    dp[mask][j] + d[j][k])
```

**Base**: `dp[1][0] = 0` (only city 0 visited, standing at 0).

**Answer**: `min over j of dp[full][j] + d[j][0]` (close the loop).

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
    full = (1 << n) - 1
    dp = [[INF] * n for _ in range(1 << n)]
    dp[1][0] = 0
    for mask in range(1 << n):
        if not mask & 1:
            continue  # tours start at 0
        for j in range(n):
            cur = dp[mask][j]
            if cur == INF:
                continue
            for k in range(n):
                if mask & (1 << k):
                    continue
                nm = mask | (1 << k)
                c = cur + d[j][k]
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

**Complexity**: n · 2ⁿ states, n transitions each: **O(n² · 2ⁿ) time, O(n · 2ⁿ) space**. For n = 20 the expression n²2ⁿ is about 4.2 × 10⁸. It is a work-bound proxy, not this implementation’s exact transition count: many allocated states are unreachable.

> [!note] Content gap
> C++/Python runtime predictions and a universal city-count cutoff are omitted because no pinned implementation, machine and benchmark support them.

Held–Karp remains exponential, but its bound is much smaller than factorial enumeration. NP-hardness does not prove that every exact TSP algorithm must take exponential time; even P ≠ NP would rule out polynomial time, not every subexponential possibility. Concorde uses branch-and-cut techniques and has solved particular large benchmark instances, which is not a worst-case guarantee.

> [!note] Content gap
> A claim that this is the current best exact worst-case TSP bound is omitted: that research frontier requires a separately scoped, up-to-date comparison of weight models and algorithm variants.

### Other bitmask DPs

- **Assignment**: n workers, n jobs, cost matrix. `dp[mask]` = minimum cost to assign the first `popcount(mask)` workers to the jobs in `mask`. O(n · 2ⁿ). (The Hungarian algorithm does it in O(n³), but the bitmask DP generalises to constraints Hungarian can't handle.)
- **Set cover / partition into groups**: iterate submasks with `sub = (sub - 1) & mask`, stopping explicitly after zero (otherwise it wraps back to mask). Including the empty submask, there are exactly 3ⁿ (mask, submask) pairs; transitions may have additional work. The count follows because each element is in the submask, in the mask but not the submask, or outside the mask.
- **Profile DP** (broken-profile, e.g. tiling a grid with dominoes): the mask records which cells of the current column boundary are already filled.

## Digit DP

> How many integers in [0, N] have digits summing to k? (Or contain no "4", or have no two equal adjacent digits, ...) N can be up to 10¹⁸.

Looping to N is impossible. Instead, build the number **digit by digit from the left** and count how many completions satisfy the property.

**State**: `(pos, acc, tight)`

- `pos`: which digit we're placing.
- `acc`: whatever the property needs to remember (here, the digit sum so far).
- `tight`: whether every digit so far has equalled N's digit. If so, the next digit can be at most N's digit at this position; otherwise any digit 0–9 is allowed.

```python
from functools import cache

def count_digit_sum(N, k):
    if (type(N) is not int
            or type(k) is not int):
        raise ValueError("integer bounds")
    if N < 0 or k < 0:
        return 0
    digits = list(map(int, str(N)))

    @cache
    def go(pos, s, tight):
        if s > k:
            return 0
        if pos == len(digits):
            return 1 if s == k else 0
        limit = digits[pos] if tight else 9
        return sum(
            go(pos + 1, s + d,
               tight and d == limit)
            for d in range(limit + 1))

    return go(0, 0, True)
```

`count_digit_sum(100, 5)` is 6 (5, 14, 23, 32, 41, 50). `count_digit_sum(2024, 10)` is 120.

**Complexity**: states = (number of digits) × (range of acc) × 2. For N ≤ 10¹⁸, decimal length is at most 19. Including the terminal position gives at most 20 × 172 × 2 = 6,880 possible (position, sum, tight) tuples, each with at most 10 digit choices; many are unreachable. Exact counts may require growing integers.

> [!note] Content gap
> The original microsecond runtime prediction is omitted because no reproducible benchmark supports it.

Two standard moves:

- **Ranges**: count in [L, R] as `f(R) − f(L − 1)`.
- **Leading zeros**: if the property cares about them (e.g. "no two adjacent equal digits", where 007 shouldn't count as having adjacent zeros), add a `started` flag to the state.

> [!tip] The intuition
> Once you've placed a digit smaller than N's digit, you're "free": every remaining combination is below N. That's why the `tight=False` states are shared between many prefixes and get cached. `tight=True` is a single path that hugs N.

## DP over DAGs: the unifying view

Draw each state as a node and each "depends on" relation as an edge. For the finite recurrences here, dependencies are acyclic, so this graph is a **DAG**. More general cyclic Bellman equations may instead require iterative methods. Then:

- **Bottom-up evaluation** is processing nodes in topological order.
- **Memoisation** is DFS on that DAG with caching.
- **Some optimisation DPs**, such as sequence alignment, are shortest/longest path problems in that DAG.
- **Some counting DPs** count paths in the DAG. Others combine independent child choices by multiplication, so the dependency graph alone is not a path-counting recurrence.

Edit distance, for example, is the shortest path from `(0, 0)` to `(m, n)` in a grid DAG with edges of weight 0 or 1. Knapsack is a longest path through a DAG of (item, capacity) nodes.

When the problem itself is a DAG, apply this directly:

```python
def longest_path(n, edges, order):
    # order: a topological order
    best = [0] * n
    out = [[] for _ in range(n)]
    for u, v, w in edges:
        out[u].append((v, w))
    for u in order:
        for v, w in out[u]:
            best[v] = max(best[v],
                          best[u] + w)
    return max(best, default=0)
```

Given vertices 0..n−1, valid edges with integer weights and a complete topological order, this computes the best path starting anywhere, allowing a zero-edge path of value 0. It takes O(V + E) unit-cost work. For single-source **shortest paths**, initialise only the source to 0 and all other distances to +∞, use min-relaxation, and return the distance array rather than its maximum. Negative edge weights are valid in a DAG.

Real uses: **critical path method** in project scheduling (longest path through task dependencies), scheduling lower bounds with unlimited parallel resources, and the **Viterbi algorithm** (most likely path through a layered DAG of hidden states over time).

For shortest paths with nonnegative weights, Dijkstra’s settling proof gives a safe order for finalising distances even on cyclic graphs. This is not a topological order of all graph edges.

## Recognising DP in an interview

### Wording signals

- "Count the number of ways..." → counting DP (often mod 10⁹ + 7).
- "Minimum cost / maximum value / longest / shortest..." with **choices at each step** → optimisation DP.
- "Is it possible to..." over subsets or partitions → feasibility DP.
- Greedy feels natural but you can construct a counterexample → DP.

### Constraint signals

The input limits often tell you the intended complexity:

| Constraint | Likely approach |
|---|---|
| n ≤ 20 | Bitmask, O(2ⁿ · n) |
| n ≤ 500 | Interval, O(n³) |
| n ≤ 5,000 | 2-D, O(n²) |
| n ≤ 10⁵ | 1-D, O(n log n) |
| values ≤ 10⁴ | Knapsack on values |
| N ≤ 10¹⁸, digits | Digit DP |

These are prompts to estimate work and storage, not runtime guarantees. Transition costs, memory layout, hardware and language can change feasibility substantially.

### A process that works

1. **Brute force first**: write the recursive "try every choice" solution. It defines the recurrence.
2. **Identify the state**: which arguments does the recursion actually depend on? Small integer parameters suggest a manageable table, but you must still prove that they determine a subproblem and that dependencies and transitions are valid.
3. **Check for overlap**: can two different paths of choices reach the same arguments? If yes, memoise.
4. **Count**: states × transitions. Compare with the constraints.
5. **Convert** to bottom-up only if you need the speed, the space optimisation, or to avoid recursion limits.

### When it's not DP

- The best choice is provably always the same local choice → **greedy** (interval scheduling by earliest finish, Huffman coding).
- The subproblems don't overlap → plain recursion or divide and conquer.
- The state would have to include an unbounded history → look for a different formulation, or the problem may be NP-hard with no good DP (general longest path, general TSP for large n).

## Key takeaways
- Bitmask DP encodes "which of a small set is used" as an integer; practical limits depend on transition and storage costs. Held–Karp solves TSP in O(n² · 2ⁿ) instead of O(n!).
- Digit DP counts numbers up to N with a digit property using states (position, accumulator, tight); handle ranges as f(R) − f(L − 1).
- Finite acyclic DP can use a topological evaluation order. Path formulations cover many sequence DPs, while transitions combining several child states require richer combination rules.
- On an actual DAG, longest and shortest paths (even with negative weights) take O(V + E).
- Read the constraints: n ≤ 20 suggests bitmask, n ≤ 500 suggests O(n³), n ≤ 5,000 suggests O(n²); start from brute-force recursion and find the state.

## Further reading
- [Held–Karp algorithm — Wikipedia](https://en.wikipedia.org/wiki/Held%E2%80%93Karp_algorithm)
- [Travelling salesman problem — Wikipedia](https://en.wikipedia.org/wiki/Travelling_salesman_problem)
- [Longest path problem — Wikipedia](https://en.wikipedia.org/wiki/Longest_path_problem)
- [Topological sorting — cp-algorithms](https://cp-algorithms.com/graph/topological-sort.html)
- [Viterbi algorithm — Wikipedia](https://en.wikipedia.org/wiki/Viterbi_algorithm)
- [Jeff Erickson, Algorithms (free textbook)](https://jeffe.cs.illinois.edu/teaching/algorithms/)
