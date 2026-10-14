---
id: dist-crdt-counters-escrow
title: Grow-only, PN and escrow counters
level: advanced
minutes: 3
summary: Merge replicated counts without double-counting and distinguish convergence from stock invariants.
sourceLesson: dist-crdts-gossip
---

The merge laws become concrete in counters. Each replica owns a part of the history, and repeated exchange must preserve that history without counting it twice.

### G-Counter (grow-only counter)

Each replica keeps a vector of counts, one per replica, and only increments its own entry.

```formula
P_new[i] = P[i] + 1
v = Σ_k P[k]
M[k] = max(X[k], Y[k])
where
P: a replica's vector of counts, one whole number per replica
i: the position of the replica doing the increment (its own entry)
P_new: the vector after an increment
v: the counter's value
k: any position in the vector, one per replica
Σ_k: sigma: add up the following term for every position k
X: one replica's vector being merged
Y: the other replica's vector being merged
M: the merged vector
max: the larger of its two inputs
In words: an increment bumps only your own entry; the value is the sum of all entries; a merge keeps the larger count in each position.
```

```
A: [A:3, B:0, C:0]  (3 local incs)
B: [A:1, B:2, C:0]  (saw 1 of A's)
merge -> [A:3, B:2, C:0]
counter value: 5
```

Why max and not sum? Because merging the same state twice must not double count (idempotence). Each entry is only ever increased by its owner, so the max retains the largest owner count present in the states being merged. An update not yet delivered is still missing.

### PN-Counter (increment and decrement)

A G-Counter can't decrement: lowering an entry would be undone by max. So use **two** G-Counters: `P` for increments and `N` for decrements.

```formula
v = Σ P − Σ N
v = (5 + 3) − (1 + 2) = 8 − 3 = 5
where
v: the counter's value
P: the G-Counter of increments, one entry per replica
N: the G-Counter of decrements, one entry per replica
Σ: sigma: add up every entry of the vector that follows
In words: the value is all the increments ever made minus all the decrements ever made; each vector still only grows, so max-merge stays correct.
```

`merge` merges P and N separately, each by element-wise max. The numbers in the block come from this example:

```
A: P=[A:5,B:0] N=[A:1,B:0]
B: P=[A:2,B:3] N=[A:0,B:2]
merge:
P=[A:5,B:3]  total 8
N=[A:1,B:2]  total 3
counter value: 5
```

Used for like-counts, stock levels where brief overselling is tolerable, and Redis Enterprise's active-active counters. Note that a PN-Counter can't enforce "never below zero": that's a global invariant needing coordination.

A middle ground is an **escrow** (or bounded) counter: split the available stock between replicas up front (say 60 units to EU, 40 to US). Each replica can decrement its own share without coordination and only needs to talk to others to borrow more. The invariant holds, and coordination happens only near the limit.

## Key takeaways
- A G-Counter lets each replica grow its own entry and merges by entry-wise maximum, avoiding double-counting repeated state.
- A PN-Counter subtracts a grow-only decrement vector from a grow-only increment vector.
- A convergent PN-Counter can oversell; preallocating escrow rights preserves a bound while permitting local use of those rights.

## Further reading
- [Conflict-free replicated data type (Wikipedia)](https://en.wikipedia.org/wiki/Conflict-free_replicated_data_type)
- [A comprehensive study of CRDTs (Shapiro et al.)](https://www.lip6.fr/Marc.Shapiro/papers/2011/Comprehensive-CRDTs-RR7506-2011-01.pdf)
- [Escrow rights and numeric invariants (Balegas et al.)](https://arxiv.org/pdf/1503.09052)
- [crdt.tech: resources and implementations](https://crdt.tech/)
