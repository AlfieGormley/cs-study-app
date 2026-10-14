---
id: fund-pacelc-latency-consistency
title: Apply PACELC to everyday replica latency
level: advanced
minutes: 3
summary: Reason about consistency and latency during normal operation, using cross-region writes and local reads.
sourceLesson: fund-cap-pacelc
---

CAP alone does not explain the latency paid while every replica is healthy. PACELC asks how replica coordination affects normal reads and writes as well as partition behaviour.

## What CAP leaves out

CAP only talks about behaviour **during a partition**, and only about one consistency model (linearisability) and one extreme availability definition. It says nothing about:

- **Latency**, which you trade against consistency *all the time*, not just during failures.
- Weaker but useful consistency models (causal, read-your-writes, bounded staleness).
- Node crashes, disk failures, or slow nodes (which are indistinguishable from partitions to the other nodes).

That gap is what PACELC fills.

## PACELC

Daniel Abadi proposed PACELC in 2010 (published 2012):

```
# A partition isolates replicas.
if Partition:
    choose Availability or Consistency
# Otherwise, coordination costs latency.
Else (normal operation):
    choose Latency or Consistency
```

The "else" half is the important addition. Even with a perfectly healthy network, strong consistency costs latency: a write must be acknowledged by multiple replicas (often in different zones or regions) before it's confirmed, and a linearisable read may need to contact a leader or a quorum.

```
 EC: write -> wait for quorum ack
     London --80ms-- Virginia
     latency at least 1 cross-region RTT

 EL: write -> ack locally, replicate
     async; fast but may be stale
```

## Classifying real systems

These are approximate classifications; many are tunable. The table summarises coordination choices, not a promise that every read is linearisable. The next unit explains the read guarantees of Cassandra, etcd and ZooKeeper.

| System | Partition | Else |
|---|---|---|
| Cassandra (ONE reads/writes) | PA-like | EL |
| DynamoDB | Depends on API and global-table consistency mode | Eventual or strong reads |
| Spanner, CockroachDB | PC | EC |
| etcd, ZooKeeper | PC | EC |

- **DynamoDB** reads are eventually consistent by default and cost half as much read capacity as strong reads. `ConsistentRead=true` reflects all prior successful writes and is supported for tables and local secondary indexes, not global secondary indexes or streams. The public read contract does not specify which replica serves the request. Multi-Region eventual-consistency global tables replicate asynchronously across regions, though AWS now also offers a multi-Region strong consistency mode that pays cross-region latency on writes.

- **Spanner** pays commit latency for external consistency, using TrueTime and Paxos across replicas.

## Key takeaways
- PACELC adds the normal-operation trade-off between latency and consistency.
- Cross-region coordination pays network delay even when no partition occurs.
- DynamoDB read options and global-table modes have different contracts; local asynchronous reads can be stale.
- System classifications are approximate; check the API and deployment you will actually use.

## Further reading
- [Consistency Tradeoffs in Modern Distributed Database System Design](https://www.cs.umd.edu/~abadi/papers/abadi-pacelc.pdf)
- [DynamoDB read consistency](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadConsistency.html)
- [CAP Twelve Years Later (Eric Brewer)](https://www.infoq.com/articles/cap-twelve-years-later-how-the-rules-have-changed/)
- [DynamoDB global-table modes](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/V2globaltables_HowItWorks.html)
