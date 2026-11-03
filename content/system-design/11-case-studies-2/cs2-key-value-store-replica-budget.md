---
id: cs2-key-value-store-replica-budget
title: Leaderless-store capacity
level: advanced
minutes: 4
summary: Budget replicated storage and replica operations without assuming equal-cost disk work.
sourceLesson: cs2-key-value-store
---

The 2007 Amazon Dynamo paper is one of the most influential papers in distributed systems. Amazon needed a store where "add to basket" remains available through many node and network failures, subject to reachable replicas and capacity. The answer was a **leaderless**, **eventually consistent** key-value store that combines about a dozen techniques. Cassandra, Riak and ScyllaDB all follow its design.

(Note that Amazon's *DynamoDB* service is a different design: its 2022 architecture paper describes leader-based Multi-Paxos replication per partition.)

This case study is a tour of those techniques, and why each one is needed.

## Requirements

### Functional
- `put(key, value, context)` and `get(key) -> (value(s), context)`.
- Values are opaque blobs, usually under 1 MB.
- Optional TTL per key.

### Non-functional
- **Availability-oriented**: accept writes where enough suitable nodes remain reachable; chosen quorum levels can sacrifice availability during partitions.
- **Tunable consistency** per request: from "fast, maybe stale" to "read your writes".
- **Predictable tail latency**: the Dynamo paper framed SLAs at the 99.9th percentile, not the average.
- **Incremental scalability**: add a node and it takes a fair share of the data, with no big-bang resharding.
- **No single point of failure**: every node is equal (symmetric, decentralised).

## Capacity has several independent limits

Replication multiplies the physical copies of logical data. Compaction, indexes, commit logs and repair need additional space. A disk that can just hold today's live files may not have room to merge them or recover a failed peer.

For example, a hypothetical 100 TB logical dataset with three copies needs 300 TB for those copies before other overhead. If a design reserves half of each disk for compaction and headroom, that is a scenario policy to validate against the chosen strategy, not a universal Cassandra rule.

| Limit | What to measure |
|---|---|
| Storage | Replicas, overhead, growth and temporary compaction space |
| Foreground work | Payloads, caching, replica contacts and retries |
| Skew | Hot keys and uneven partition sizes |
| Recovery | Streaming, repair and remaining capacity after failures |

## Replica operations are not equal-cost disk I/O

A logical write sent to several replicas creates several storage-side operations. A read can request full data from one replica and digests from others, or trigger speculative requests and repair. These operations have different CPU, network and disk costs.

Do not divide a fleet total evenly over nodes and declare it a throughput benchmark. Check the busiest replica owners, actual consistency levels, cache behaviour, compaction load and disk synchronization policy. Spare capacity must cover the intended failure domain as well as growth.

This case study combines historical Dynamo ideas with cited Cassandra behaviour. Its workload and headroom inputs are illustrative; they do not establish a universal node count or a future product guarantee.

## Key takeaways
- Logical storage expands by replication factor before compaction headroom.
- Logical client requests can create several replica operations.
- Benchmark skew, payloads, compaction and failure headroom rather than inferring capacity from SSD labels.

## Further reading
- [Dynamo: Amazon's highly available key-value store (SOSP 2007)](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)
- [Amazon's Dynamo (Werner Vogels)](https://www.allthingsdistributed.com/2007/10/amazons_dynamo.html)
- [Dynamo architecture (Apache Cassandra docs)](https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html)
- [Compaction (Apache Cassandra docs)](https://cassandra.apache.org/doc/latest/cassandra/managing/operating/compaction/index.html)
- [DynamoDB 2022 architecture paper](https://www.usenix.org/system/files/atc22-elhemali.pdf)
