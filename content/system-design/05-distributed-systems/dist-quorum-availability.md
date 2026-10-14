---
id: dist-quorum-availability
title: Quorum availability and data-centre scope
level: intermediate
minutes: 3
summary: Calculate unavailable-replica tolerance and understand what LOCAL_QUORUM covers.
sourceLesson: dist-quorums
---

The preceding lesson introduced N replicas per key, W write acknowledgements and R read responses. Choosing those counts also determines which failures an operation can tolerate.

| N | W | R | Behaviour |
|---|---|---|---|
| 3 | 2 | 2 | Balanced; tolerates 1 down |
| 3 | 3 | 1 | Fast reads; writes need all |
| 3 | 1 | 3 | Fast writes; reads need all |
| 3 | 1 | 1 | No overlap; stale reads |

Fault tolerance: a write still succeeds as long as W replicas are up, and a read as long as R are up, so the number that may be down is whatever is left over.

```formula
F_w = N − W
F_r = N − R
F_w = 3 − 2 = 1
F_r = 3 − 2 = 1
where
F_w: how many replicas can be down while writes still succeed
F_r: how many replicas can be down while reads still succeed
N: the number of replicas that store the key; here 3
W: the replicas that must acknowledge a write; here 2
R: the replicas that must respond to a read; here 2
In words: each operation can lose every replica it doesn't need. Raising W or R buys overlap at the cost of tolerating fewer failures.
```

With 3 replicas and 2 responses for each operation, you tolerate one failure for both. With 3 write acknowledgements and 1 read response instead, reads tolerate two failures but writes tolerate none.

Cassandra's `QUORUM` is a majority of the replicas:

```formula
Q = ⌊N / 2⌋ + 1
Q = ⌊3 / 2⌋ + 1 = 1 + 1 = 2
where
Q: the quorum size, the number of replicas that must respond
N: the total replication factor (replicas per key) across all data centres; here 3
⌊ ⌋: floor: round down to the nearest whole number, so ⌊1.5⌋ = 1
In words: a quorum is just over half the replicas, so two quorums always share at least one replica.
```

So `QUORUM` is 2 of 3 replicas, or 3 of 5. Using it for both reads and writes satisfies both overlap conditions above. `LOCAL_QUORUM` counts only replicas in the coordinator's data centre, avoiding cross-region latency, but it also means the overlap guarantee only holds for reads and writes made in the **same** data centre.

## Key takeaways
- A write can lose replicas it does not need to acknowledge, and a read can lose replicas it does not need to answer.
- Majority quorums trade lower failure tolerance for intersections between operations.
- LOCAL_QUORUM intersects reads and writes inside the same data centre; another region can remain behind.

## Further reading
- [Dynamo: Amazon's Highly Available Key-value Store (SOSP 2007)](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)
- [Cassandra Dynamo architecture](https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html)
- [Quorum (distributed computing) (Wikipedia)](https://en.wikipedia.org/wiki/Quorum_%28distributed_computing%29)
