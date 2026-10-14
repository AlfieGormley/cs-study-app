---
id: dist-crdt-merge-laws
title: CRDT merge laws and growing state
level: advanced
minutes: 3
summary: Check both merge algebra and inflationary updates before claiming convergence without coordination.
sourceLesson: dist-crdts-gossip
---

A conflict-free replicated data type supplies a merge policy in advance, instead of asking a reader to resolve siblings by hand. Its convergence guarantee has requirements on both merge and update behaviour.

## CRDTs

A **Conflict-free Replicated Data Type** is a data structure designed so that replicas can be updated independently and **always merge to the same result**, with no coordination and no conflicts to resolve by hand.

State-based CRDTs (CvRDTs) define a `merge` function that is:

| Property | Meaning |
|---|---|
| Commutative | Order of the two inputs doesn't matter |
| Associative | Grouping doesn't matter |
| Idempotent | Merging something with itself changes nothing |

Written as equations:

```formula
merge(a, b) = merge(b, a)
merge(merge(a,b),c) = merge(a,merge(b,c))
merge(a, a) = a
where
merge: the function that combines two replica states into one
a: one replica's state
b: another replica's state
c: a third replica's state
In words: the first line is commutativity (order doesn't matter), the second associativity (grouping doesn't matter), the third idempotence (repeats don't matter).
```

For example, if merge is "take the larger number", merging 3 with 5 gives 5 either way round, merging three states in any grouping gives the largest of the three, and merging 5 with 5 gives 5.

Those three properties mean replicas can exchange state in any order, any number of times, via any path (gossip), and still converge. That's **strong eventual consistency**: replicas that have received the same updates are in the same state.

There's a fourth condition that's easy to miss: **local updates may only move the state "upwards"**, so that the updated state, merged with the old one, gives the updated state. Formally, states form a *join-semilattice*, merge is the least upper bound, and updates are inflationary. That's why a G-Counter may only increase entries and why a set "remove" is recorded as a tombstone rather than by deleting the element: a deletion would be undone by the next merge with a replica that still has it.

Operation-based CRDTs (CmRDTs) instead broadcast operations. Concurrent operations must commute, and the delivery layer usually has to deliver each operation **exactly once** and in **causal order**. They send less data but need more from the network. Delta-state CRDTs sit in between: they ship only the recently changed part of the state, merged with the same join. A grow-only set is another simple example: adds grow the state, and union is a commutative, associative and idempotent merge.

## Key takeaways
- State-based merges are commutative, associative and idempotent, making exchange order and repeats harmless.
- Local updates must grow in the state’s partial order; merge is the join, not any arbitrary function with three algebraic properties.
- Operation-based and delta-state CRDTs trade data volume against delivery assumptions; strong eventual consistency concerns replicas that received the same updates.

## Further reading
- [Conflict-free replicated data type (Wikipedia)](https://en.wikipedia.org/wiki/Conflict-free_replicated_data_type)
- [A comprehensive study of CRDTs (Shapiro et al.)](https://www.lip6.fr/Marc.Shapiro/papers/2011/Comprehensive-CRDTs-RR7506-2011-01.pdf)
- [crdt.tech: resources and implementations](https://crdt.tech/)
