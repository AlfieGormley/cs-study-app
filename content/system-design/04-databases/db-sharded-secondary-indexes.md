---
id: db-sharded-secondary-indexes
title: Secondary indexes across shards
level: advanced
minutes: 3
summary: Compare scatter-gather and global indexes, and choose DynamoDB LSI or GSI freshness and capacity deliberately.
sourceLesson: db-partitioning
---

An index on a field other than the shard key can change both query fan-out and write coordination. Distinguish the general local/global layout from DynamoDB's specific meanings of LSI and GSI.

## Secondary indexes on partitioned data

Partitioning by primary key makes primary-key lookups easy. But what about "find all red cars" when cars are partitioned by `car_id`?

### Local (document-partitioned) indexes

Each partition indexes only its own data.

- **Writes**: cheap, local to one partition.
- **Reads**: must ask *every* partition and merge (**scatter-gather**). Tail latency is the slowest partition's latency.
- Used by MongoDB, Cassandra secondary indexes, Elasticsearch.

### Global (term-partitioned) indexes

The index itself is partitioned by the indexed value: all `colour=red` entries live in one index partition.

- **Reads**: go to one index partition.
- **Writes**: one row write may update index partitions on other nodes, so global indexes are usually **updated asynchronously**.
- DynamoDB global secondary indexes are eventually consistent, typically within a fraction of a second.

| | Local index | Global index |
|---|---|---|
| Write cost | One partition | Several |
| Read cost | All partitions | One partition |
| Freshness | Engine-dependent (e.g. search refresh) | Engine-dependent; often async |

### DynamoDB's two kinds of index

DynamoDB offers both, with its own twist on "local":

- A **local secondary index (LSI)** keeps the table's partition key and adds a different sort key. Because you must supply the partition key to query it, it reads one partition, not all of them. It supports strongly consistent reads, but you can have at most **5** per table, they can only be defined **when the table is created**, and each partition-key value's items (table plus LSIs) are capped at **10 GB**.
- A **global secondary index (GSI)** can use any attribute as its keys. The default quota is **20** per table (adjustable), you can add or remove them at any time, but reads are eventually consistent only. Each GSI has its own capacity, and if a GSI can't keep up with writes, DynamoDB throttles writes to the *base table*.

## Fan-out makes tail latency matter

A query waiting for all twenty shards completes at the slowest response. If their timings are independent, all must beat their individual 99th-percentile thresholds for the combined query to do so. Thus a per-shard p99 does not determine the combined p99; the full latency distribution and correlations matter.

## Key takeaways
- Local indexes make non-partition-key reads scatter across shards and wait for the slowest result.
- Global indexes change read routing but can require cross-node asynchronous maintenance.
- DynamoDB LSIs share a partition key and can read strongly; GSIs support other keys with eventual reads.

## Further reading
- [DynamoDB: Global secondary indexes](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GSI.html)
- [DynamoDB: Local secondary indexes](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/LSI.html)
- [research.google: the tail at scale](https://research.google/pubs/the-tail-at-scale/)
