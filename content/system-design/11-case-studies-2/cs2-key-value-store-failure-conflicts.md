---
id: cs2-key-value-store-failure-conflicts
title: Replica outages and conflicting versions
level: advanced
minutes: 4
summary: Separate short-term hints from causal version merges and clock-based winner selection.
sourceLesson: cs2-key-value-store
---

## Handling temporary failures: sloppy quorum and hinted handoff

Suppose replica B for key k is down. A strict quorum fails only if too few home replicas respond: with 3 replicas and 2 acknowledgements required, one failed replica is tolerable. Dynamo instead uses a **sloppy quorum**: the write goes to the first N *healthy* nodes on the ring, so node D stands in for B. D stores the write with a **hint** saying "this belongs to B". When gossip shows B is back, D **hands off** the data and deletes its copy.

This keeps writes available during failures. The price is that read and write counts exceeding the home-replica count no longer guarantee overlap, because the W nodes that acknowledged may not be the "home" replicas that a later read asks.

Cassandra kept hinted handoff but not the sloppy quorum. A hint doesn't count towards the consistency level (except at the special `ANY` level), so a `QUORUM` write still needs acknowledgements from real home replicas, and fails if too few are up.

Hints are a short-term fix. Cassandra stops collecting hints for a node once it has been down longer than `max_hint_window` (3 hours by default). After a longer outage, repair must compare the home replicas and stream the missing represented data. Hints alone cannot restore writes outside the recorded hint window. The next lesson covers the repair mechanism.

## Conflict resolution

Without a leader, two clients can update the same key concurrently on different replicas. When the versions meet, which one wins?

### Vector clocks (Dynamo, Riak)
Each version carries a vector of `(node, counter)` pairs.

- If one vector is at least the other in every component and strictly larger in at least one, it **descends** from it, and the older version can be discarded:

```formula
a_x ≥ b_x  ∀ x
a_x > b_x  ∃ x
where
a: one version's vector clock
b: the other version's vector clock
a_x: the counter for node x in clock a (0 if x is missing)
b_x: the counter for node x in clock b (0 if x is missing)
x: a node name that appears in either clock
≥: is greater than or equal to
>: is strictly greater than
∀: "for every": the line must hold for all nodes x
∃: "for at least one": the line must hold for some node x
In words: version a descends from version b when every node's counter in a is at least as big as in b, and at least one is bigger.
```

For example, the vector with A at 3 and B at 1 descends from the vector with A at 2 and B at 1. The A counter increased while B remained unchanged.
- If neither dominates, the writes were **concurrent**. Both versions (siblings) are kept and returned to the client on read, and the **application merges** them, then writes the result with the merged context.

Amazon's shopping basket merged siblings by **union**. Nothing added is ever lost, but a deleted item can occasionally reappear, which the paper accepts as the business trade-off. To stop vector clocks growing without limit, Dynamo truncated the oldest entries beyond about 10, accepting possible loss of causal precision; the paper gives 10 as an example threshold, not a universal setting.

### Last-write-wins (Cassandra)
Each *cell* (column value) carries a write timestamp, and the highest timestamp wins. It's simple, needs no siblings and makes reads cheap. But **concurrent writes are silently lost**, and **clock skew** can make an older write win. If node clocks drift by 200 ms, a write made 100 ms later can lose. Run NTP carefully, model data to avoid concurrent read-modify-write cycles (use per-element columns, counters or collections), or use lightweight transactions.

### CRDTs
Riak added CRDT data types (counters, sets, maps) that converge under their specified merge semantics, which is the best of both worlds for suitable data.

## Key takeaways
- Sloppy quorums change the replica set, so the strict intersection argument no longer applies.
- Cassandra hints do not count towards ordinary QUORUM acknowledgements.
- Vector clocks expose concurrent siblings; last-write-wins can discard a later real-time update.

## Further reading
- [Dynamo: Amazon's highly available key-value store (SOSP 2007)](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)
- [Dynamo architecture (Apache Cassandra docs)](https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html)
- [Vector clock (Wikipedia)](https://en.wikipedia.org/wiki/Vector_clock)
