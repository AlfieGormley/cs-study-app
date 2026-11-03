---
id: dp-held-karp-resources
title: Count Held–Karp work and storage
level: advanced
minutes: 2
summary: Held–Karp reduces factorial enumeration to exponential DP.
sourceLesson: dp-advanced
---

The visited-set recurrence is exact for the stated cost matrix. Its resource requirements depend on the table representation and on which states are reachable.

Let n be the number of cities. The allocated table has one slot per subset of cities and possible end city: n × 2ⁿ slots. Each reachable state tries up to n next cities, so the work is at most about n² × 2ⁿ steps. So **O(n² · 2ⁿ) time, O(n · 2ⁿ) space**.

For 20 cities that is about 420 million steps, against about 1.2 × 10¹⁷ brute-force tours: roughly 300 million times fewer. It is a work bound, not this implementation's exact transition count, because many allocated states are never reached.

The two growth rates also respond differently to one more city. Adding a city a little more than doubles the Held–Karp work (twice as many subsets, slightly more cities per state), but multiplies the brute-force tour count by the number of cities. Memory grows as fast as the table, which is often the first limit you hit.

Held–Karp remains exponential, but its bound is much smaller than factorial enumeration. NP-hardness does not prove that every exact TSP algorithm must take exponential time; even a proof that polynomial-time solving differs from polynomial-time verification would rule out polynomial time, not every subexponential possibility. Concorde uses branch-and-cut techniques and has solved particular large benchmark instances, which is not a worst-case guarantee.

## Key takeaways
- Held–Karp reduces factorial enumeration to exponential DP.
- Allocated table states and executed transitions are different counts.
- Memory layout and available resources matter as much as the growth bound.

## Further reading
- [Held–Karp algorithm](https://en.wikipedia.org/wiki/Held%E2%80%93Karp_algorithm)
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
