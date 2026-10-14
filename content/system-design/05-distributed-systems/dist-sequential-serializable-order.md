---
id: dist-sequential-serializable-order
title: Sequential consistency and serializable transactions
level: intermediate
minutes: 3
summary: Distinguish per-client order and transaction order from guarantees about real-time order.
sourceLesson: dist-consistency-models
---

The preceding lesson defined linearizability and strict serializability. Here the question is what remains when a system preserves an agreed order but does not promise that it matches real-time order.

## Sequential consistency

**Sequential consistency** (Lamport, 1979) requires that all operations appear in *some* single total order that is consistent with **each client's program order**, but not necessarily with real-time order.

So in the preceding linearizability unit’s violation diagram, if B and C are different clients with no communication, sequential consistency could allow it (order: C reads 0, A writes 1, B reads 1). What it forbids is a single client seeing time go backwards, or two clients disagreeing about the order of two writes.

It's mostly of interest for CPU memory models and as a stepping stone. ZooKeeper is a real-world example of something close to it: writes are linearizable, but a read served by a follower may be stale, while each client still sees updates in one agreed order.

### Telling the three apart

The names are easy to mix up, so compare them on two questions: what do they cover, and do they respect real-time order?

| Model | Covers | Real-time order? |
|---|---|---|
| Linearizable | Single operations | Yes |
| Sequential | Single operations | No, only per-client order |
| Serializable | Multi-object transactions | No |
| Strict serializable | Transactions | Yes |

A quick test: if a history only looks wrong when you compare *wall-clock* times across different clients, it can still be sequentially consistent or serializable, but it isn't linearizable or strictly serializable.

## Key takeaways
- Sequential consistency preserves each client’s program order inside one total order, without requiring cross-client real-time order.
- Serializable transactions match some serial transaction order; strict serializability also respects real-time order.
- A stale cross-client read can fit sequential consistency or serializability even when it violates linearizability.

## Further reading
- [Sequential consistency (Jepsen)](https://jepsen.io/consistency/models/sequential)
- [Strict serializability (Jepsen)](https://jepsen.io/consistency/models/strict-serializable)
- [Linearizability versus serializability (Peter Bailis)](https://www.bailis.org/blog/linearizability-versus-serializability/)
