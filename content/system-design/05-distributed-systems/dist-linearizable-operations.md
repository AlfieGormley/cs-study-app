---
id: dist-linearizable-operations
title: Linearizability and real-time order
level: intermediate
minutes: 4
summary: Judge overlapping reads and writes using the single-copy contract and real-time order.
sourceLesson: dist-consistency-models
---

When data is replicated, different clients can see different values at the same moment. A **consistency model** is a contract that says which histories of reads and writes are allowed. Stronger models allow fewer surprising histories, at a cost in latency and availability.

The CAP theorem's "C" means one specific model, linearizability. In practice there's a whole spectrum, and choosing the right point on it is one of the most important design decisions you make.

## The hierarchy

From strongest to weakest (these are models for individual reads and writes, not multi-step transactions):

```
   Linearizable
        |
   Sequential
        |
     Causal
```

Each level shown allows every history the level above allows, plus more. Session guarantees form additional, partly independent properties. Eventual convergence is a separate liveness promise and should not be inferred merely from a safety ordering model. Jepsen's map also places transactional models such as serializability alongside these.

## Linearizability

**Linearizability** (also called atomic or strong consistency) means the system behaves as if there were **one copy** of the data, and every operation takes effect **atomically at some instant between its start and its end**.

In the timelines below, x is a single stored value (one key) that starts at 0. `write x=1` means a client sets it to 1, `read x` means a client asks for its current value, and each bar runs from when the client sent the request to when it got the reply.

The key consequence is **recency guarantee**: once a write completes, every later read (in real-time order) must see it or something newer. And once any client has read a new value, no later read anywhere may return the old one.

```
time ------------------------------->
A: |--write x=1--|
B:                 |--read x--| -> 1
C:   |------read x------|        -> 0 or 1
```

C's read overlaps A's write, so either answer is fine. B's read starts after the write finished, so it **must** return 1.

These examples contain only one write. A later write can deliberately restore an old-looking value without violating linearizability; recency concerns operation/version order, not a number always increasing.

### A violation

```
A: |--------write x=1--------|
B:    |-read-| -> 1
C:              |-read-| -> 0   ILLEGAL
```

B saw the new value; C started *after* B finished, yet saw the old one. That's what happens with naive async replication: B hit an up-to-date replica, C hit a lagging one.

### Composability

Linearizability is **local** (Herlihy and Wing call it *composable*): if every individual object is linearizable, the system as a whole is linearizable. You can shard keys across independent linearizable groups and still reason about each one alone. Sequential consistency does **not** compose: two objects that are each sequentially consistent can together produce a history that no single order explains.

### Where you need it

- **Leader election and locks**: everyone must agree who holds the lock.
- **Uniqueness constraints**: two users can't both claim username `alice`.
- **Cross-channel timing**: a user uploads a file, then a message on a queue tells a worker to process it. If the worker reads a stale replica, the file "doesn't exist".

### What it costs

Linearizability needs coordination (a single leader with synchronous confirmation, or consensus). A replicated service must establish an authoritative order for writes and freshness for reads. Many protocols pay a quorum round trip; safe leader leases can permit local reads while their timing assumptions hold, so a network round trip is not required for every read. During a partition, the minority side must stop serving. That's the CAP theorem, and PACELC's "else latency" is the cost even without partitions.

> [!note] Linearizable vs serializable
> **Serializability** is about *transactions* over many objects: the result equals *some* serial order, which needn't match real-time order. **Linearizability** is about *single operations* respecting real-time order. Having both is called **strict serializability**. Spanner (which calls it external consistency) and FoundationDB provide it; CockroachDB provides serializability with somewhat weaker guarantees about real-time order.

## Key takeaways
- Linearizability places each operation at an instant between invocation and response, respecting real-time order.
- An overlapping read may return old or new; once a new value is observed, a later read cannot go backwards.
- Linearizability composes across objects and requires coordination; serializability concerns transactions.

## Further reading
- [Consistency models map (Jepsen)](https://jepsen.io/consistency)
- [Linearizability (Jepsen)](https://jepsen.io/consistency/models/linearizable)
- [Strict serializability (Jepsen)](https://jepsen.io/consistency/models/strict-serializable)
- [Linearizability versus serializability (Peter Bailis)](https://www.bailis.org/blog/linearizability-versus-serializability/)
