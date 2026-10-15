---
id: dp-submask-and-assignment
title: Assignments, submasks and profiles
level: advanced
minutes: 3
summary: A job mask can describe which assignments remain.
sourceLesson: dp-advanced
---

Bitmasks also represent assigned jobs or the occupied boundary of a grid. The mask must retain every fact needed by later choices, not merely count how much work is done.

### Other bitmask DPs

- **Assignment problem**: n workers, n jobs, cost matrix. `dp[mask]` records minimum cost to assign the first `popcount(mask)` workers (popcount is the number of 1 bits in the mask) to the jobs in `mask`. O(n · 2ⁿ). (The Hungarian algorithm does it in O(n³), but the bitmask DP generalises to constraints Hungarian can't handle.)
- **Set cover / partition into groups**: iterate submasks with `sub = (sub - 1) & mask`, stopping explicitly after zero (otherwise it wraps back to mask). Including the empty submask, the number of pairs is:

```formula
pairs = 3^n
3^15 = 14,348,907
where
pairs: the number of (mask, submask) pairs, where every bit of the submask is also set in the mask
n: the number of items (bits)
3^n: n copies of 3 multiplied together
In words: each item independently has three options: in the submask, in the mask but not the submask, or outside the mask.
```

By comparison, independently choosing two arbitrary masks gives:

```formula
arbitrary = 2^n 2^n = 4^n
where
arbitrary: the number of pairs of independently chosen masks
n: the number of available items
In words: Each of the two masks independently selects a subset; a submask restriction reduces the total to three choices per item.
```

Transitions may still add work per pair.
- **Profile DP** (broken-profile, e.g. tiling a grid with dominoes): the mask records which cells of the current column boundary are already filled.

## When assignments interact

The plain job mask is sufficient only when assignment costs depend on the current engineer and chosen project. If adjacent engineers’ project choices interact, also retain the previous engineer’s project. The engineer index is the mask’s set-bit count; the last-project flag supplies the missing boundary information. With n projects this gives O(n × 2ⁿ) allocated states and up to n next choices each, hence O(n² × 2ⁿ) transition work. A mask alone would incorrectly merge histories with different neighbouring costs.

## Key takeaways
- A job mask can describe which assignments remain.
- Extra interaction constraints may require additional boundary state.
- Stop a submask loop after zero to avoid wrapping around.

## Further reading
- [Held–Karp algorithm](https://en.wikipedia.org/wiki/Held%E2%80%93Karp_algorithm)
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
