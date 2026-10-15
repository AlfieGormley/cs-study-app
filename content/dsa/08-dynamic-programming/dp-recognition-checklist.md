---
id: dp-recognition-checklist
title: Choose a DP state from the problem
level: advanced
minutes: 3
summary: Constraints suggest candidate state spaces, then you must estimate their work.
sourceLesson: dp-advanced
---

## Recognising DP in an interview

### Wording signals

- "Count the number of ways..." → counting DP (often reported modulo 10⁹ + 7, the remainder after dividing by the prime 1,000,000,007, to keep numbers small).
- "Minimum cost / maximum value / longest / shortest..." with **choices at each step** → optimisation DP.
- "Is it possible to..." over subsets or partitions → feasibility DP.
- Greedy feels natural but you can construct a counterexample → DP.

### Constraint signals

The input limits often tell you the intended complexity. Here n is the input size (number of items, string length and so on), N is a numeric bound on a value, and the O(...) entries are Big-O growth rates:

| Constraint | Likely approach |
|---|---|
| Up to 20 items | Bitmask, O(2ⁿ · n) |
| Up to 500 items | Interval, O(n³) |
| Up to 5,000 items | 2-D, O(n²) |
| Up to 100,000 items | 1-D, O(n log n) |
| Values up to 10,000 | Knapsack on values |
| Decimal bound up to 10¹⁸ | Digit DP |

These are prompts to estimate work and storage, not running-time guarantees. Transition costs, memory layout, hardware and language can change feasibility substantially.

### A process that works

1. **Brute force first**: write the recursive "try every choice" solution. It defines the recurrence.
2. **Identify the state**: which arguments does the recursion actually depend on? Small integer parameters suggest a manageable table, but you must still prove that they determine a subproblem and that dependencies and transitions are valid.
3. **Check for overlap**: can two different paths of choices reach the same arguments? If yes, memoise.
4. **Count**: states × transitions. Compare with the constraints.
5. **Convert** to bottom-up only if you need the speed, the space optimisation, or to avoid recursion limits.

### When it's not DP

- The best choice is provably always the same local choice → **greedy** (interval scheduling by earliest finish, Huffman coding).
- The subproblems don't overlap → memoisation saves no repeated calls. Plain recursion or divide and conquer may suffice; tree DP can still combine disjoint subtrees.
- The state would have to include an unbounded history → look for a different formulation, or the problem may be NP-hard with no good DP (general longest path, general TSP for large n).

## Key takeaways
- Constraints suggest candidate state spaces, then you must estimate their work.
- Start with brute force, identify sufficient state, and check overlap.
- Greedy needs a proof; caching cannot rescue an enormous history state.

## Further reading
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
- [MIT algorithms course](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/)
