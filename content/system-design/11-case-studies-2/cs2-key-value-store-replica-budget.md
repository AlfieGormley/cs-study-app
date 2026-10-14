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

## Back-of-the-envelope

Start with storage. Each key is kept on several nodes; the number of copies is the **replication factor** (RF). Assume 100 TB (terabytes) of logical data, meaning the data as the application sees it, and three replica copies:

```formula
D = L × RF
D = 100 TB × 3 = 300 TB
where
D: raw data stored across the whole cluster
L: logical data, one copy of everything; here 100 TB
RF: replication factor, the number of copies of each key; here 3
TB: terabytes, 10^12 bytes
In words: three copies of 100 TB is 300 TB on disk.
```

Each node has an 8 TB SSD (solid-state drive), but you keep about half free for SSTable compaction and headroom, so only about 4 TB is usable:

```formula
n = D / u
n = 300 TB / 4 TB = 75 nodes
where
n: the minimum number of nodes for capacity alone
D: raw data to store; 300 TB
u: usable space per node; 8 TB × 50% = 4 TB
TB: terabytes
nodes: servers in the cluster
In words: 300 TB at 4 TB a node needs at least 75 nodes; plan for about 100 to allow growth and losing a rack.
```

Now traffic. Assume 1 M (one million) operations a second, 70% reads. Every logical read asks 2 replicas (a read consistency level of 2) and every logical write is sent to all 3 replicas:

```formula
r = 700,000/s × 2 = 1,400,000/s
w = 300,000/s × 3 = 900,000/s
p = (r + w) / n
p = 2,300,000/s / 100 ≈ 23,000/s
where
r: replica reads per second (700,000 logical reads, each asking R = 2 replicas)
w: replica writes per second (300,000 logical writes, each sent to RF = 3 replicas)
p: replica operations per node per second
n: nodes in the cluster; here 100
s: seconds
≈: approximately equal to
In words: a million client operations become about 2.3 million replica operations, about 23,000 a second for each of 100 nodes.
```

What matters:

- The 23k/node estimate counts logical replica operations, not equal-cost disk I/Os. Payloads, digests, compaction, caching and skew determine actual capacity; benchmark rather than assuming NVMe makes it comfortable.

> **Content gap:** no reproducible throughput benchmark or universal partition-size threshold is supplied. Storage and traffic figures are scenario assumptions. Product details below describe the cited Cassandra 5.0 documentation and historical Dynamo/DynamoDB papers, not every future release.
- **Headroom for compaction** is a real sizing factor. Size-tiered compaction can temporarily need as much free space again as the data being compacted.
- At 100 nodes, plan for routine failures rather than assuming a failure-free fleet. Failure handling is normal operation, not an edge case.

## Key takeaways
- Logical storage expands by replication factor before compaction headroom.
- Logical client requests can create several replica operations.
- Benchmark skew, payloads, compaction and failure headroom rather than inferring capacity from SSD labels.

## Further reading
- [Dynamo: Amazon's highly available key-value store (SOSP 2007)](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)
- [Amazon's Dynamo (Werner Vogels)](https://www.allthingsdistributed.com/2007/10/amazons_dynamo.html)
- [Dynamo architecture (Apache Cassandra docs)](https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html)
- [Compaction (Apache Cassandra docs)](https://cassandra.apache.org/doc/latest/cassandra/managing/operating/compaction/index.html)
