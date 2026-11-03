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
- **Set cover / partition into groups**: iterate submasks with `sub = (sub - 1) & mask`, stopping explicitly after zero (otherwise it wraps back to mask). Looping over every mask and all its submasks visits 3ⁿ pairs for n items, because each item independently plays one of three roles: outside the mask, in the mask but not the submask, or in both. That is about 14 million pairs for 15 items, far fewer than the 4ⁿ pairs of two unrelated masks. Each extra item multiplies the work by 3. Transitions may still add work per pair.
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
