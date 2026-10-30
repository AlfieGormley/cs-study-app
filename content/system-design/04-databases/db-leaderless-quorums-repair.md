---
id: db-leaderless-quorums-repair
title: Leaderless quorums and replica repair
level: intermediate
minutes: 3
summary: Predict quorum overlap and failure tolerance, then restore replicas with hints, read repair and anti-entropy.
sourceLesson: db-replication
---

A leaderless system asks several replicas to take part in each operation. Whether a read sees the latest write depends on how the read and write groups overlap; whether the system keeps working depends on how many replicas remain. Missing writes then need repairing.

## Leaderless replication

Any replica accepts writes. The client (or a coordinator node) sends each write to all *n* replicas and considers it successful when *w* acknowledge; reads query *r* replicas and take the newest value. This is the **Dynamo** style, used by Cassandra, ScyllaDB, Riak and Amazon's original Dynamo.

For a fixed replica set, durable successful writes and no concurrent writes, the quorum condition guarantees that a later read reaches at least one replica that accepted the last successful write. Assume the reconciliation rule recognises that version; overlap alone is not a general latest-value guarantee:

```formula essential
w + r > n
overlap ≥ w + r − n
where
n: the replication factor, the number of replicas that store each key; often 3
w: the write quorum, how many replicas must acknowledge a write before it counts as successful
r: the read quorum, how many replicas a read asks before returning the newest value it sees
overlap: the number of replicas that are in both the write set and the read set, whichever replicas the two operations happen to reach
≥: greater than or equal to
In words: if the replicas you write to and the replicas you read from add up to more than the total, the two groups must share at least one replica, so the read reaches a copy of the latest write.
```

With three replicas, writing to two and reading from two always shares at least one replica, and both reads and writes still succeed with one replica down. Writing to two and reading from one is faster to read but can miss the write entirely.

> [!analogy] Real-world analogy: three clerks and a dated notebook each
> A club keeps its decisions in three clerks' notebooks. A decision counts as recorded once any two clerks have written it down, with the date. To check the latest decision, you ask any two clerks and believe the most recently dated entry. Whichever two you ask, at least one of them recorded it.
>
> **How it maps:** The clerks are the replicas, two recordings is the write quorum, asking two is the read quorum, and "most recently dated" is the version or timestamp the read uses to pick the newest value. Two plus two is more than three, so the groups must overlap.
>
> **Where it stops:** If two decisions are recorded at the same moment, or a substitute clerk takes the note while a regular is away (a sloppy quorum), overlap alone no longer guarantees you see the right one. Clerk clocks can also disagree, which is why real systems need careful version tracking.

The cost of raising *w* or *r* is latency and availability: each request waits for more replicas and fails if too few are up. How quorums behave under failure, and why they're weaker than they look (sloppy quorums, concurrent writes, clock-based conflict resolution), is covered in the consensus module.

Repairing stale replicas:

- **Read repair**: a read that sees a stale replica writes the newer value back.
- **Hinted handoff**: if a replica is down, another node holds its writes ("hints") and passes them on when it recovers.
- **Anti-entropy**: background comparison with Merkle trees to find and fix differences.

| | Single | Multi | Leaderless |
|---|---|---|---|
| Write conflicts | None | Yes | Yes |
| Failover needed | Yes | Per DC | No |
| Write latency | One region | Local | Quorum |

## Compare a storage quorum

In Aurora's simplified durability and recovery model, six storage copies are spread two per availability zone. Four-copy writes still have enough copies after one zone is lost; three-copy recovery reads can continue after a zone and one additional copy are lost. Any four-copy and three-copy sets overlap. This is storage arithmetic, not a statement that every ordinary SQL query reads three copies or that database compute is always available.

## Key takeaways
- Read and write sets overlap when their sizes sum to more than the replica count.
- Larger quorums raise acknowledgement latency and require more surviving replicas.
- Hints, read repair and anti-entropy converge stale replicas; overlap alone is not linearizability.

## Further reading
- [DeCandia et al.: Dynamo, Amazon's highly available key-value store](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)
- [Verbitski et al.: Amazon Aurora design considerations](https://www.amazon.science/publications/amazon-aurora-design-considerations-for-high-throughput-cloud-native-relational-databases)
