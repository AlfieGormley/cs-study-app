---
id: fund-cap-pacelc
title: CAP and PACELC, and what they really mean
level: advanced
minutes: 13
summary: What the CAP theorem actually proves, why "pick two of three" is misleading, and how PACELC adds the latency trade-off that matters every day.
---

The CAP theorem is the most quoted and most misunderstood result in distributed systems. Used carefully, it's a sharp tool for reasoning about what happens during a network failure. Used loosely ("Mongo is CP, Cassandra is AP"), it mostly causes confusion.

## The precise statement

Eric Brewer conjectured it in 2000; Seth Gilbert and Nancy Lynch proved it in 2002. In their formulation:

- **C (consistency)** means **linearisability**: every read sees the most recent completed write, as if there were a single copy of the data.
- **A (availability)** means **every request received by a non-failing node must get a non-error response**. No time limit, but no "sorry, try later".
- **P (partition tolerance)** means the system keeps operating even if the network drops arbitrary messages between nodes.

The theorem: **in the presence of a network partition, a system cannot be both linearisable and available.**

## Why it's true: the two-node argument

```
  client X              client Y
     |                     |
     v                     v
 +--------+   //////   +--------+
 | node 1 |<-- cut --->| node 2 |
 |  v = 1 |   //////   |  v = 0 |
 +--------+            +--------+
```

1. Cut the network between the nodes before the write, so node 2 cannot receive it.
2. Client X writes `v = 1` to node 1 and receives a successful acknowledgement before Y starts reading.
3. Client Y reads `v` from node 2.

Node 2 has two choices:

- **Answer with `v = 0`.** It stays available but returns stale data: not linearisable. *Choose A.*
- **Refuse or wait** until it can contact node 1. It stays consistent but isn't available. *Choose C.*

There is no third option. That's the whole theorem.

## Misconception 1: "pick two of three"

The Venn-diagram version suggests you can pick CA, CP or AP like menu items. But **you don't get to choose whether partitions happen**. Networks drop packets, switches fail, GC pauses make nodes unreachable, cloud zones lose connectivity.

So for any system spread over a network, P isn't optional. The real statement is:

> [!note] The useful form
> *When a partition happens*, choose between consistency and availability. *When there's no partition*, you can have both.

A "CA" system is one that just doesn't handle partitions, which in practice means a single node, or a system whose behaviour during a partition is undefined.

## Misconception 2: CAP's "A" is the same as high availability

CAP availability is extreme: *every* non-failing node must respond successfully, even a node isolated on the minority side of a partition.

Real systems usually mean something weaker by "highly available": most requests succeed most of the time. A system using **majority quorums** (Raft in etcd, Paxos in Spanner, the similar Zab protocol in ZooKeeper) is CP in CAP terms. The minority side refuses writes during a partition. Yet such systems routinely achieve very high availability, because:

- Partitions are relatively rare.
- Clients on the minority side can often fail over to the majority side.

Google Spanner is technically CP, yet it advertises 99.999% availability for multi-region configurations, because Google invests heavily in making partitions rare.

## Misconception 3: CAP's "C" is ACID's "C"

They're unrelated.

| Term | Meaning |
|---|---|
| ACID C | Transactions keep invariants (constraints) valid |
| CAP C | Linearisability: reads see the latest write |

A single-node database can provide linearisable operations, but being single-node does not guarantee that every API or isolation level does so. ACID consistency is a separate question: application logic and constraints must preserve the intended invariants.

## Misconception 4: databases are "CP" or "AP"

Martin Kleppmann's essay "Please stop calling databases CP or AP" makes the case well. Most real systems are **neither** strictly:

- Many offer **tunable** consistency per request. Cassandra lets you pick `ONE`, `QUORUM` or `ALL`; DynamoDB offers eventually consistent or strongly consistent reads.
- Many aren't linearisable even without partitions (e.g. asynchronous replication with reads from replicas), so they don't satisfy CAP's C anyway.
- Many aren't CAP-available either (e.g. a leader-based system where nodes refuse writes when they can't see the leader).

A system that is neither linearisable nor CAP-available is just... a system with other trade-offs. Describe its *actual* guarantees instead: "reads may be up to ~1 s stale", "writes are rejected on the minority side".

## Misconception 5: CAP covers the important trade-offs

CAP only talks about behaviour **during a partition**, and only about one consistency model (linearisability) and one extreme availability definition. It says nothing about:

- **Latency**, which you trade against consistency *all the time*, not just during failures.
- Weaker but useful consistency models (causal, read-your-writes, bounded staleness).
- Node crashes, disk failures, or slow nodes (which are indistinguishable from partitions to the other nodes).

That gap is what PACELC fills.

## PACELC

Daniel Abadi proposed PACELC in 2010 (published 2012):

```
if Partition:
    choose Availability or Consistency
Else (normal operation):
    choose Latency or Consistency
```

The "else" half is the important addition. Even with a perfectly healthy network, strong consistency costs latency: a write must be acknowledged by multiple replicas (often in different zones or regions) before it's confirmed, and a linearisable read may need to contact a leader or a quorum.

```
 EC: write -> wait for quorum ack
     London --80ms-- Virginia
     latency >= 1 cross-region RTT

 EL: write -> ack locally, replicate
     async; fast but may be stale
```

### Classifying real systems

These are approximate defaults; many are tunable.

| System | Partition | Else |
|---|---|---|
| Cassandra (ONE reads/writes) | PA-like | EL |
| DynamoDB | Depends on API and global-table consistency mode | Eventual or strong reads |
| Spanner, CockroachDB | PC | EC |
| etcd, ZooKeeper | PC | EC |

- **Cassandra** with `ONE` reads and writes favours availability and low latency when at least one actual replica for the key is reachable, but can still time out or reject requests. With `QUORUM` reads and writes, it pays latency for stronger guarantees (though it still isn't fully linearisable without lightweight transactions). The rule behind this: with *N* replicas, writes acknowledged by *W* and reads consulting *R*, reads are guaranteed to overlap the latest write when **W + R > N**. With N = 3, `QUORUM` is 2, and 2 + 2 > 3.
- **DynamoDB** reads are eventually consistent by default (cheaper and faster); `ConsistentRead=true` costs twice the read capacity and is served by the partition's leader replica. Multi-Region eventual-consistency global tables replicate asynchronously across regions, though AWS now also offers a multi-Region strong consistency mode that pays cross-region latency on writes.
- **etcd** serves linearisable reads by default, confirming with a quorum before answering. **ZooKeeper** commits writes through a quorum, but by default a client reads from whichever server it's connected to, which may lag: reads are ordered but can be stale. `sync()` is a useful freshness barrier, but is not a quorum operation and is not a strict linearisability guarantee under all failures. Same "CP" label, different everyday guarantee.
- **Spanner** pays commit latency for external consistency, using TrueTime and Paxos across replicas.

> [!tip] The everyday question
> PACELC's "E" half is the one you face daily. Partitions are rare; latency is paid on every request. "Do we need this read to be strongly consistent, at the cost of a cross-zone round trip?" is a question you'll ask constantly.

## Using this in a design

1. **Decide per data type, not per system.** A bank's balance needs strong consistency; its "recently viewed" list doesn't.
2. **Ask what happens on the minority side of a partition.** Refuse writes? Accept and reconcile later? Serve stale reads with a warning? Brewer's own example is an ATM: during a partition it can keep dispensing cash up to a small limit, accepting a bounded risk and reconciling (and charging overdraft fees) afterwards.
3. **If you choose availability, plan for conflicts.** Last-write-wins (loses data silently), version vectors with application merge, or CRDTs. Amazon's original Dynamo merged conflicting shopping carts, occasionally resurrecting deleted items.
4. **If you choose consistency, plan for unavailability.** Clients need retries, timeouts and clear errors.
5. **Quantify the latency cost.** Same-zone quorum: ~1 ms. Cross-region quorum: tens to hundreds of ms.

The distributed consistency and consensus module covers linearisability, quorums, Raft and conflict resolution in depth.

## Key takeaways
- CAP: during a network partition, a system can't be both linearisable and available to every non-failing node.
- Partitions aren't optional in distributed systems, so the real choice is C or A *when a partition happens*.
- CAP's C is linearisability (not ACID's C) and CAP's A is very strict; CP systems can still be highly available in practice.
- Most real databases are neither strictly CP nor AP; describe their actual guarantees, often tunable per request.
- PACELC adds the everyday trade-off: without partitions, choose between lower latency and stronger consistency.
- Make consistency decisions per data type, and plan for conflicts (if A) or errors (if C).

## Further reading
- [Brewer's Conjecture and the Feasibility of CAP (Gilbert and Lynch, PDF)](https://users.ece.cmu.edu/~adrian/731-sp04/readings/GL-cap.pdf)
- [CAP Twelve Years Later (Eric Brewer, InfoQ)](https://www.infoq.com/articles/cap-twelve-years-later-how-the-rules-have-changed/)
- [Please stop calling databases CP or AP (Martin Kleppmann)](https://martin.kleppmann.com/2015/05/11/please-stop-calling-databases-cp-or-ap.html)
- [Consistency Tradeoffs in Modern Distributed Database System Design (Abadi, PDF)](https://www.cs.umd.edu/~abadi/papers/abadi-pacelc.pdf)
- [PACELC theorem (Wikipedia)](https://en.wikipedia.org/wiki/PACELC_theorem)
- [DynamoDB read consistency (AWS docs)](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadConsistency.html)
