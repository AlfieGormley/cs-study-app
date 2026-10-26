---
id: cx-amortised-potential
sourceLesson: cx-amortised-analysis
title: Potential as stored work
level: advanced
minutes: 2
summary: Use changes in a potential function to prove an amortised bound.
---

A potential function tracks saved work for an entire data structure. It should rise during cheap operations and fall when expensive work consumes that saving.

## Actual cost plus the change in stored work

```formula essential
a_i = c_i + Φ_i − Φ_{i−1}
where
a_i: the amortised cost charged for operation i, in work units
c_i: its actual cost in the same work units
Φ_i: potential after operation i, in work units
Φ_{i−1}: potential before that operation
i: the operation number, starting at one
Φ: capital phi, the chosen potential function of the structure's state
In words: charge the actual work plus any newly stored potential; releasing potential reduces the charge for an expensive operation.
```

When these charges are added, every intermediate potential appears once positively and once negatively. Those terms cancel, leaving actual total work plus final potential minus starting potential. Starting at zero and keeping potential nonnegative therefore makes the amortised total an upper bound on actual total work for every sequence prefix. More generally, final potential must not fall below the starting value for that same bound without an extra initial allowance.

## A doubling-array example

Count copies and writes as one work unit each. Start with an empty capacity-zero array, allocate one slot on its first append, then double when full. For this append-only policy the array is at least half full after its first append. One useful reference choice is:

```formula reference
Φ = 2s − K
where
Φ: stored potential, in work units
s: the number of stored elements
K: capacity in element slots
In words: potential increases as the array fills and drops when doubling creates spare room, releasing credit to offset copying.
```

A cheap append stores two potential units alongside its one write. A resize costs many copies, but the drop in potential offsets them. The resulting charge is at most three units per append, including the initial append. This is a proof about counted work, not a claim that each append takes the same time.

Choosing potential is part of designing the proof. The element count alone need not be suitable, and this append-only potential is not automatically valid after arbitrary deletions.

## Key takeaways
- Potential change connects cheap and expensive operations.
- Intermediate potential values cancel in a sequence total.
- Check the starting state and nonnegative-balance condition.

## Further reading
- [Erickson: Amortized Analysis](https://jeffe.cs.illinois.edu/teaching/algorithms/notes/09-amortize.pdf)
