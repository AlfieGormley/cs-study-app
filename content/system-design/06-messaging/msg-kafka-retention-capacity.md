---
id: msg-kafka-retention-capacity
title: Kafka retention, compaction and partition capacity
level: intermediate
minutes: 4
summary: Choose what history survives and size consumer parallelism from measured throughput.
sourceLesson: msg-kafka-log-streaming
---

Kafka’s retained storage is also a recovery resource. Decide whether consumers need a full event history or the latest value for each key, then check that enough partition and storage capacity supports the workload.

## Retention and compaction

Each partition is stored as a series of **segment files** (1 GiB by default). Old data is removed a whole segment at a time according to the topic's `cleanup.policy`.

| Policy | Keeps |
|---|---|
| `delete` | Whole eligible segments removed when configured age or size limits are exceeded; deletion is asynchronous |
| `compact` | At least the latest record for each key |
| `compact,delete` | Latest per key, but also age-limited |

**Log compaction** turns a topic into a durable table of "latest value per key". In the sketch below, k1, k2 and k3 are record keys, a to d are their values, and `k2=null` is a record for k2 with no value:

```
before: k1=a k2=b k1=c k3=d k2=null
after:  k1=c k3=d   (k2 tombstoned)
```

A record with a `null` value is a **tombstone**: it tells compaction to remove the key entirely (after `delete.retention.ms`, default 24 hours, so consumers have a bounded opportunity to see deletion). A rebuilding consumer must catch up within the tombstone-retention window; otherwise it can miss a delete and retain stale state. Compacted topics back Kafka Streams state stores, `__consumer_offsets` itself, and change-data-capture topics that need to be replayable from scratch.

Compaction never touches the **active segment**, and it keeps record offsets unchanged, so offsets in a compacted topic have gaps.

## Why Kafka is fast

- **Sequential I/O.** Appends and reads are sequential, which disks and SSDs handle at hundreds of MB/s.
- **Page cache.** Kafka leans on the operating system's cache rather than its own; consumers near the head of the log read from memory.
- **Zero-copy.** Brokers use `sendfile` to move bytes from page cache to socket without copying through user space (when TLS is not in use).
- **Batching and compression.** Producers batch records per partition (`linger.ms`, `batch.size`) and compress whole batches with lz4 or zstd.

Benchmark payload sizes, replication, compression and consumer work for the intended deployment; there is no universal cluster throughput figure.

## Choosing the number of partitions

Partitions bound consumer parallelism, so size for the slowest consumer. Measure one consumer's processing rate, then divide the target throughput by it:

```formula reference
P ≥ T / c
where
P: the number of partitions
≥: is at least
T: the target throughput of the topic, here 60 megabytes per second (MB/s)
c: the measured processing rate of one consumer, here 5 MB/s
MB: megabytes
s: seconds; "MB/s" means megabytes per second
In words: enough partitions must be available to assign work to the consumers needed at the measured rate; this estimate assumes balanced traffic and sufficient broker and downstream capacity.
```

In the illustrative workload, twelve equally busy consumers would just keep up. Add measured headroom for growth and failures, because adding partitions later remaps keys. Extra partitions alone do not add workers or make an overloaded database faster.

Too many partitions cost broker memory, open files, longer leader elections and slower rebalances. Reliable limits depend on Kafka version, controller/broker resources and workload; test failover and rebalance behaviour at the planned scale.

## Key takeaways

- Retention removes eligible segments asynchronously; compaction preserves current key state and stable offsets.
- Consumers rebuilding a compacted table must observe deletions before tombstones expire.
- Batching, compression, page cache and sequential I/O explain the design; benchmark deployment throughput.
- Size partition parallelism for the slowest consumer with growth headroom, then validate broker and controller costs.

## Further reading

- [Apache Kafka documentation: design](https://kafka.apache.org/documentation/)
- [Kafka log compaction (Confluent docs)](https://docs.confluent.io/kafka/design/log_compaction.html)
- [Kafka consumer design (Confluent docs)](https://docs.confluent.io/kafka/design/consumer-design.html)
- [Apache Kafka (Wikipedia)](https://en.wikipedia.org/wiki/Apache_Kafka)
