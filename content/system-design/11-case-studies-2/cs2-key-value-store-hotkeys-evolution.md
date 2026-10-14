---
id: cs2-key-value-store-hotkeys-evolution
title: Leaderless hot keys and regional trade-offs
level: advanced
minutes: 3
summary: Identify replica-local hotspots and compare Cassandra techniques with historical Dynamo.
sourceLesson: cs2-key-value-store
---

## High-level architecture

Follow the arrows as data paths; the drawing is not a deployment specification.

```
        client (or smart driver)
                 |
                 v
     +-----------------------+
     | any node: coordinator |
     +-----------------------+
       /         |         \
      v          v          v
 +---------+ +---------+ +---------+
 |replica A| |replica B| |replica C|
 |commitlog| |commitlog| |commitlog|
 |memtable | |memtable | |memtable |
 |SSTables | |SSTables | |SSTables |
 +---------+ +---------+ +---------+
   ^   gossip, hints, Merkle repair  ^
   +---------------------------------+
```

Token-aware client drivers send each request straight to a replica for the key, saving a network hop.

## Bottlenecks and trade-offs

- **Hot keys**: one key's load lands on its N replicas (typically 3), however many nodes you have. Mitigate with client-side caching, or by splitting the key into sub-keys.
- **Large partitions** (in Cassandra's wide-row model): oversized partitions can hurt compaction, repair and memory use; no universal 100MB cliff applies. Bucket by time or hash to keep partitions small.
- **LWW vs vector clocks**: LWW is simpler but loses concurrent writes. Vector clocks expose concurrency but push merge correctness onto applications; truncation can lose causal information.
- **Repair cost**: Merkle repair is I/O heavy. Incremental repair, or tools such as Cassandra Reaper, schedule it in small slices.
- **Consistency choice is per request**, so teams must actually understand the required read and write counts and the home-replica set.

## Evolving at 10x

- **1 PB, 1,000 nodes**: vnodes let new nodes stream small ranges from many peers in parallel. Limit concurrent streaming so bootstrapping doesn't hurt foreground latency.
- **Multiple regions**: replicate per data centre (`NetworkTopologyStrategy`, for example 3 replicas in each of 2 regions), and use `LOCAL_QUORUM` for latency, with asynchronous cross-region replication.
- **Stronger guarantees** where needed: Paxos-based lightweight transactions for compare-and-set (classic Cassandra Paxos takes four round trips, and newer versions cut that), or move those entities to a consensus-based store. Check the deployed Cassandra release for available transaction protocols; the historical DynamoDB paper provides a separate example of leader-based partitions.
- **Operational automation**: scheduled repair, node replacement, compaction tuning and capacity forecasting become a platform team's main job.

## One key can dominate a large fleet

A token ring partitions keys, not individual requests to one key. Even a hundred-node cluster can concentrate a viral configuration's read traffic on its three replicas. A client-side cache with a bounded freshness policy, shared read caches or separately versioned replicated copies can reduce that traffic. Choose invalidation and access-control rules appropriate to the value; adding tokens or unrelated nodes alone does not create more authoritative replicas for that key.

Splitting a key into sub-keys is useful when the workload can be split semantically, such as per-source counters or time buckets. It changes the read and merge contract, so it cannot be applied mechanically to an opaque indivisible value. If a value must have a conditional single winner, select an actual compare-and-set or consensus protocol rather than assuming ordinary read/write quorum overlap supplies one.

> **Content gap:** no reproducible throughput benchmark or universal partition-size threshold is supplied. Storage and traffic figures are scenario assumptions. Product details below describe the cited Cassandra 5.0 documentation and historical Dynamo/DynamoDB papers, not every future release.

## Key takeaways
- Adding unrelated nodes does not spread one key beyond its replica set.
- Regional consistency, repair and bootstrap policies need deployment-specific review.
- Dynamo, Cassandra and DynamoDB differ in conflict, hint and replication protocols.

## Further reading
- [Dynamo: Amazon's highly available key-value store (SOSP 2007)](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)
- [Amazon's Dynamo (Werner Vogels)](https://www.allthingsdistributed.com/2007/10/amazons_dynamo.html)
- [Dynamo architecture (Apache Cassandra docs)](https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html)
- [Compaction (Apache Cassandra docs)](https://cassandra.apache.org/doc/latest/cassandra/managing/operating/compaction/index.html)
