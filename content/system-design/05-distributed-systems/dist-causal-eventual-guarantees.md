---
id: dist-causal-eventual-guarantees
title: Causal order and eventual convergence
level: intermediate
minutes: 3
summary: Keep dependencies in order while understanding what partition availability and convergence leave unspecified.
sourceLesson: dist-consistency-models
---

Sequential consistency imposes a total order on all operations. Causal consistency relaxes that requirement for unrelated work; eventual convergence is a separate promise about what happens after updates stop.

## Causal consistency

**Causal consistency** only orders operations that are **causally related**. If operation A could have influenced operation B (B happened after reading A's result, or they're in the same session), everyone must see A before B. **Concurrent** operations can be seen in different orders by different nodes.

```
Alice: post "I lost my job"
Alice: post "Never mind, got a new one!"
Bob reads 2nd post, replies "Congrats!"

Causal: nobody sees "Congrats!" before
        the post it replies to.
```

Without causal consistency, Carol might see Bob's "Congrats!" before Alice's posts arrive, or see the posts in reverse, which reads as Bob celebrating a sacking.

Causal consistency is, in effect, the **strongest model that remains available during partitions**: each side keeps working and merges causal histories later. (Strictly, Mahajan et al. proved this for a slight strengthening called real-time causal, and it needs *sticky* availability, where each client keeps talking to the same replica.) Systems track causality with version vectors or dependency metadata; MongoDB offers causally consistent sessions.

## Eventual consistency

**Eventual consistency** promises only that if writes stop, all replicas *eventually* converge to the same value. It says nothing about what you read in the meantime: stale values, values going backwards, writes out of order.

It's what you get from Dynamo-style stores with low quorum settings, DNS, and asynchronous read replicas. It is cheap and highly available, and fine for things like like-counts and product views. But "eventually" has no bound, and convergence needs a conflict-resolution rule (covered in the CRDT units later in this module).

Some systems offer **bounded staleness** in between: reads may lag, but by no more than a stated time or number of versions (Azure Cosmos DB offers this as a named level). That is stronger than eventual, because it gives a bound, but weaker than linearizable.

## Key takeaways
- Causal consistency orders dependent operations; independent concurrent writes need no common total order.
- Partition availability for causal histories needs suitable sticky replicas; moving clients may require waiting for dependencies.
- Eventual consistency promises convergence after writes stop, not bounded staleness or a particular intermediate read order.

## Further reading
- [Consistency models map (Jepsen)](https://jepsen.io/consistency)
- [Causal consistency (Jepsen)](https://jepsen.io/consistency/models/causal)
- [Please stop calling databases CP or AP (Kleppmann)](https://martin.kleppmann.com/2015/05/11/please-stop-calling-databases-cp-or-ap.html)
