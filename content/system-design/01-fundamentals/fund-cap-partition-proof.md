---
id: fund-cap-partition-proof
title: Understand CAP through a two-node partition
level: advanced
minutes: 3
summary: Use the exact definitions of linearisability and CAP availability to see why an isolated replica must choose.
sourceLesson: fund-cap-pacelc
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

## Why “pick two of three” misleads

The Venn-diagram version suggests you can pick CA, CP or AP like menu items. But **you don't get to choose whether partitions happen**. Networks drop packets, switches fail, GC pauses make nodes unreachable, cloud zones lose connectivity.

So for any system spread over a network, P isn't optional. The real statement is:

> [!note] The useful form
> *When a partition happens*, choose between consistency and availability. *When there's no partition*, you can have both.

A "CA" system is one that just doesn't handle partitions, which in practice means a single node, or a system whose behaviour during a partition is undefined.

## CAP consistency and ACID invariants

They describe different properties.

| Term | Meaning |
|---|---|
| ACID C | Transactions keep invariants (constraints) valid |
| CAP C | Linearisability: reads see the latest write |

A single-node database can provide linearisable operations, but being single-node does not guarantee that every API or isolation level does so. ACID consistency is a separate question: application logic and constraints must preserve the intended invariants.

## Key takeaways
- During a partition, a replicated system cannot promise both linearisability and successful responses at every non-failing node.
- Partition tolerance is not a menu option that makes network failures disappear.
- CAP consistency concerns operation ordering; ACID consistency concerns application invariants.

## Further reading
- [Brewer’s Conjecture and the Feasibility of CAP](https://users.ece.cmu.edu/~adrian/731-sp04/readings/GL-cap.pdf)
- [CAP Twelve Years Later (Eric Brewer)](https://www.infoq.com/articles/cap-twelve-years-later-how-the-rules-have-changed/)
- [Gilbert and Lynch: perspectives on CAP](https://groups.csail.mit.edu/tds/papers/Gilbert/Brewer2.pdf)
