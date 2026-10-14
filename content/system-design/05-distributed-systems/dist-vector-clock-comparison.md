---
id: dist-vector-clock-comparison
title: Vector clocks detect concurrency
level: intermediate
minutes: 4
summary: Merge vector timestamps and compare every entry to distinguish causality from conflict.
sourceLesson: dist-time-ordering
---

Lamport clocks preserve causality but cannot detect concurrent events. A vector records each process’s progress separately, giving enough information to make that comparison.

## Vector clocks

A vector clock keeps one counter **per process**. With N processes, each process holds a list of N counters, V[1] to V[N]: its best knowledge of how many events every process has had.

```formula
V_new[i] = V[i] + 1
V_new[j] = max(V[j], V′[j])
where
V: this process's vector clock, a list of N whole-number counters
N: the number of processes
i: this process's own position in the list
j: any position in the list, from 1 to N
V_new: the vector after the update
V′: V-prime, the vector carried on an incoming message
max: the larger of its two inputs
In words: on a local event or a send, add one to your own entry only (and attach the vector to the message); on a receive, take the larger value in every position, then add one to your own entry.
```

For example, if P2's clock is [1, 4, 2] and it receives a message stamped [3, 1, 0], the position-by-position maximum is [3, 4, 2], and adding one to P2's own entry gives [3, 5, 2].

To compare two vector timestamps V and W:

```formula
V ≤ W ⇔ ∀k: V[k] ≤ W[k]
V → W ⇔ V ≤ W ∧ V ≠ W
V ∥ W ⇔ V ≰ W ∧ W ≰ V
where
V: one event's vector timestamp
W: another event's vector timestamp
k: a position in the vectors
∀k: "for every position k"
⇔: "exactly when": the left side holds if and only if the right side holds
∧: "and": both conditions must hold
≤: less than or equal to (for vectors: in every position)
≰: not less than or equal to: some position of the left vector is bigger
≠: not equal: at least one position differs
→: "happened before"
∥: "is concurrent with"
In words: V happened before W when no entry of V is bigger than W's and at least one is smaller; if each vector is bigger somewhere, the events are concurrent.
```

The last case is the one Lamport clocks can't see: distinct events are **concurrent** exactly when neither vector is less than or equal to the other in every position.

```
P1: [1,0,0] a
P1: [2,0,0] send to P2
P2: [2,1,0] recv
P2: [2,2,0] send to P3
P3: [0,0,1] e (before recv)
P3: [2,2,2] recv
P1: [3,0,0] c
```

Does event c precede the send on P2? Compare their vectors [3,0,0] and [2,2,0]: 3 > 2 in one position, 0 < 2 in another. **Concurrent.** Vector clocks can detect that, which is why Dynamo and Riak used them to keep both sibling values instead of silently dropping one.

Cost: one entry per participant. With thousands of clients as writers, vectors bloat, so systems use **version vectors** keyed by replica (not client), or prune old entries (which can misclassify causal relationships).

## Key takeaways
- Each process increments its own vector entry; receive takes entry-wise maxima and then increments the receiver’s entry.
- One vector causally precedes another when no entry is greater and at least one is smaller.
- Vectors ahead in different entries are concurrent; metadata grows with the number of participants.

## Further reading
- [Time, Clocks, and the Ordering of Events (Lamport, 1978)](https://lamport.azurewebsites.net/pubs/time-clocks.pdf)
- [Vector clock (Wikipedia)](https://en.wikipedia.org/wiki/Vector_clock)
