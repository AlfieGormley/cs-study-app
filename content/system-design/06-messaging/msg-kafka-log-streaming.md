---
id: msg-kafka-log-streaming
title: Log-based streaming: Kafka in depth
level: intermediate
minutes: 18
summary: How Kafka's partitioned, replicated log works: offsets, consumer groups, retention, compaction, ISR replication and exactly what ordering it guarantees.
---

Queues delete messages once they are consumed. Kafka takes a different view: a topic is an **append-only log** that is kept for a configured time, and consumers simply remember **how far they have read**. This one design choice gives Kafka replay, cheap fan-out to many consumers and very high throughput. It also explains most of its sharp edges.

## The log and offsets

A log is an ordered sequence of records. Each record gets a sequential **offset** when it is appended.

```
partition 0
offset: 0   1   2   3   4   5   6
      [ a | b | c | d | e | f | g ]──▶
              ▲           ▲       append
       group B│    group A│
```

- Producers only ever append to the end.
- Records are immutable. You never update offset 3.
- Each consumer group has its own position. Group A is at 5, group B is at 2. Neither affects the other.

Reading does not remove anything, so adding a tenth consumer group costs network and CPU but no extra storage.

## Partitions: the unit of parallelism

A single log on one disk would cap throughput, so a topic is split into **partitions**, each its own independent log spread across brokers.

```
topic: orders (3 partitions)
 P0 [0][1][2][3][4]      broker 1
 P1 [0][1][2]            broker 2
 P2 [0][1][2][3]         broker 3
```

The producer chooses a partition for every record:

- **With a key**: The default Java client uses `toPositive(murmur2(serializedKey)) % numPartitions` when it respects keys. Equal serialized keys share a partition while partition count and partitioning configuration stay fixed; other clients or custom partitioners can differ.
- **Without a key**: the producer's built-in *sticky* behaviour fills a batch for one partition, then moves to another, which gives good batching.

Ordering is guaranteed **only within a partition**. A stable key mapping gives an append order for that key; producer retries and concurrent processing must still preserve the intended business order. There is no ordering between partitions.

> [!warning] Changing partition count breaks key placement
> Adding partitions changes `hash % numPartitions`, so new records for an existing key may land on a different partition from its older records. Ordering per key is broken across the change. Plan partition counts up front (over-provision moderately) for keyed topics.

## Consumer groups

A **consumer group** is a set of consumers that share the work of reading a topic. Kafka assigns each partition to **exactly one consumer in the group**.

```
6 partitions, group with 3 consumers
 C1 ◀── P0, P1
 C2 ◀── P2, P3
 C3 ◀── P4, P5
```

Consequences:

- **Maximum parallelism equals the number of partitions.** A 7th consumer in a 6-partition group sits idle.
- **Different groups each get every record.** This is how Kafka does pub/sub: billing and analytics are separate groups.
- **Rebalancing.** When a consumer joins, leaves or misses heartbeats (session timeout, 45 s by default for the classic Java consumer; the new consumer protocol uses broker-controlled timeouts), or fails to call `poll()` within `max.poll.interval.ms` (default 5 minutes), partitions are reassigned.

### Rebalance protocols

Rebalancing has been redesigned twice, and which protocol you run makes a big difference during deploys:

| Protocol | During a rebalance |
|---|---|
| Classic, eager | Every consumer stops |
| Classic, cooperative | Only moved partitions pause |
| New (KIP-848) | Broker-driven, incremental |

- **Eager** (the original): every consumer revokes all its partitions, then the group reassigns from scratch. A rolling deploy of 30 instances means 30 stop-the-world pauses.
- **Cooperative** (`CooperativeStickyAssignor`): consumers keep the partitions they are allowed to keep; only those that move are paused.
- **The new consumer group protocol** (KIP-848) is generally available from **Kafka 4.0**. The broker's group coordinator computes the assignment and hands out changes to each consumer independently, with no group-wide synchronisation barrier. Brokers enable it by default; clients opt in with `group.protocol=consumer`.

**Static membership** (`group.instance.id`) adds one more trick: a consumer that restarts with the same ID within the session timeout can retain its assignment without an otherwise unnecessary rebalance when the rest of the group and subscriptions remain stable.

### Committing offsets

Consumers record progress by **committing offsets** to an internal topic, `__consumer_offsets`. A committed offset means "the next record I want is N".

- Commit **after** processing for at-least-once. A crash causes reprocessing from the last commit.
- Commit **before** processing for at-most-once. A crash skips records.
- `enable.auto.commit=true` uses a default 5-second auto-commit interval; scheduling details depend on client/protocol, which can commit offsets of records you have not finished processing if you hand work to other threads.

Because a consumer commits a single position per partition, a consumer group has no per-message ack. A strictly sequential handler can be blocked by one slow record. Parallel processing is possible, but contiguous offset commits and required per-key order still need coordination. This is the fundamental difference from a queue, and the ordering lesson covers how to deal with it.

> [!note] Share groups: queues on Kafka
> Kafka 4.0 shipped an early version of **share groups** (KIP-932, "queues for Kafka"), and Kafka 4.2 (2026) made them production-ready. Consumers in a share group cooperatively read the same partitions, each record is locked to one consumer and **acknowledged individually**, and delivery attempts are counted. You can then run more consumers than partitions, at the cost of per-partition ordering. Use them for job-style work; keep consumer groups for ordered streams.

## Retention and compaction

Each partition is stored as a series of **segment files** (1 GiB by default). Old data is removed a whole segment at a time according to the topic's `cleanup.policy`.

| Policy | Keeps |
|---|---|
| `delete` | Whole eligible segments removed when configured age or size limits are exceeded; deletion is asynchronous |
| `compact` | At least the latest record for each key |
| `compact,delete` | Latest per key, but also age-limited |

**Log compaction** turns a topic into a durable table of "latest value per key".

```
before: k1=a k2=b k1=c k3=d k2=null
after:  k1=c k3=d   (k2 tombstoned)
```

A record with a `null` value is a **tombstone**: it tells compaction to remove the key entirely (after `delete.retention.ms`, default 24 hours, so consumers have a bounded opportunity to see deletion). A rebuilding consumer must catch up within the tombstone-retention window; otherwise it can miss a delete and retain stale state. Compacted topics back Kafka Streams state stores, `__consumer_offsets` itself, and change-data-capture topics that need to be replayable from scratch.

Compaction never touches the **active segment**, and it keeps record offsets unchanged, so offsets in a compacted topic have gaps.

## Replication and the ISR

Each partition has a **replication factor** (typically 3). One replica is the **leader**; all reads and writes go through it by default. **Followers** fetch from the leader to stay up to date.

```
P0: leader b1, followers b2, b3
producer ─▶ b1 ──fetch── b2
             └──fetch── b3
```

The **in-sync replica set (ISR)** is the leader plus the followers that have caught up within `replica.lag.time.max.ms` (default 30 s). A record is **committed** when every replica in the ISR has it. The **high watermark** is the offset up to which records are committed; consumers can only read up to it.

Durability comes from combining three settings:

| Setting | Typical safe value |
|---|---|
| `replication.factor` | 3 |
| `min.insync.replicas` | 2 |
| producer `acks` | `all` |

With `acks=all`, the leader acknowledges only when all **current** ISR members have the record. `min.insync.replicas=2` makes the leader **refuse writes** (with `NotEnoughReplicas`) if the ISR shrinks below 2. Together they guarantee an acknowledged write is on at least two brokers. With all three replicas initially healthy and controller quorum available, it tolerates one replica failure without losing acknowledged data and can resume writes after detection/election. Transient write errors or pauses are still possible.

Since **Kafka 3.0** the producer defaults are already safe: `acks=all` and `enable.idempotence=true`. But the broker default for `min.insync.replicas` is still **1**. If both followers fall behind and drop out of the ISR, the ISR is just the leader, and `acks=all` is satisfied by the leader alone. A write acknowledged in that state is guaranteed on only one broker; follower copies may or may not exist, and Kafka replication acknowledgement is not a per-write fsync guarantee. Set `min.insync.replicas=2` explicitly on topics that matter.

With `acks=1` (the default before 3.0), the leader acknowledges as soon as it has written locally. If it dies before followers fetch, the acknowledged write is lost when a follower becomes leader. With `acks=0` the producer does not wait at all.

> [!note] Unclean leader election
> If no ISR replica is available, eligible-leader-replica (ELR) tracking in newer Kafka can identify other safe candidates. Without a safe candidate, Kafka must wait or permit unclean election that risks data loss. `unclean.leader.election.enable` defaults to `false`: Kafka chooses consistency.

Cluster metadata, including which broker leads each partition and the ISR of every partition, is managed by the **KRaft** controller quorum: a small set of controller nodes (typically 3 or 5) that replicate a metadata log among themselves using a Raft-style protocol. One controller is active; brokers follow the metadata log and apply changes. KRaft became production-ready in Kafka 3.3, and **ZooKeeper support was removed entirely in Kafka 4.0** (2025), so clusters must migrate to KRaft on 3.x before upgrading. Like any majority quorum, 3 controllers tolerate one failure and 5 tolerate two.

## Why Kafka is fast

- **Sequential I/O.** Appends and reads are sequential, which disks and SSDs handle at hundreds of MB/s.
- **Page cache.** Kafka leans on the operating system's cache rather than its own; consumers near the head of the log read from memory.
- **Zero-copy.** Brokers use `sendfile` to move bytes from page cache to socket without copying through user space (when TLS is not in use).
- **Batching and compression.** Producers batch records per partition (`linger.ms`, `batch.size`) and compress whole batches with lz4 or zstd.

Universal cluster throughput and an unsourced historical message-count benchmark are absent because no representative measured setup is established here. Benchmark payload sizes, replication, compression and consumer work for the intended deployment.

## Ordering guarantees, precisely

Kafka guarantees that records **in one partition** are stored and delivered in the order the leader appended them. Whether that matches the order your producer *sent* them depends on retries:

- With retries and `max.in.flight.requests.per.connection > 1` and **no** idempotence, batch 1 can fail, batch 2 succeed, then batch 1 succeed on retry: reordered.
- With `enable.idempotence=true` (the default since Kafka 3.0), the broker tracks a producer ID and per-partition sequence numbers, rejects out-of-order batches and drops duplicates. Ordering is preserved with up to 5 in-flight requests (`max.in.flight.requests.per.connection`, default 5).

Idempotence needs `acks=all`. If you set `acks=1` without explicitly enabling idempotence, the producer quietly turns idempotence off; if you enable it explicitly alongside `acks=1`, the producer refuses to start.

So the full guarantee is: **per partition, per producer, in send order, with idempotence on.**

## Choosing the number of partitions

Partitions bound consumer parallelism, so size for the slowest consumer:

1. Target throughput: say 60 MB/s.
2. Measure one consumer's processing rate: say 5 MB/s.
3. Partitions needed ≥ 60 ÷ 5 = 12. Add headroom for growth: 24.

Too many partitions cost broker memory, open files, longer leader elections and slower rebalances. A universal partition-count recommendation is absent because reliable limits depend on Kafka version, controller/broker resources and workload; test failover and rebalance behavior at the planned scale.

## Key takeaways
- A Kafka topic is a set of partitioned, append-only logs; consumers track offsets rather than deleting messages, which enables replay and cheap fan-out.
- Ordering holds only within a partition; keys pick the partition, and changing partition count remaps keys.
- Within a consumer group each partition has one consumer, so partitions cap parallelism; separate groups each see every record.
- `replication.factor=3`, `min.insync.replicas=2` and `acks=all` give durable writes that survive one broker loss; `acks=all` is the producer default since 3.0, but `min.insync.replicas` defaults to 1 and must be set.
- Metadata lives in the KRaft controller quorum (ZooKeeper was removed in 4.0), and the KIP-848 protocol and share groups make rebalances cheaper and queue-style consumption possible.
- Retention deletes old segments; compaction keeps the latest value per key and uses tombstones for deletes.

## Further reading
- [Apache Kafka documentation: design](https://kafka.apache.org/documentation/)
- [Kafka replication design (Confluent docs)](https://docs.confluent.io/kafka/design/replication.html)
- [Kafka log compaction (Confluent docs)](https://docs.confluent.io/kafka/design/log_compaction.html)
- [Kafka consumer design (Confluent docs)](https://docs.confluent.io/kafka/design/consumer-design.html)
- [KIP-848: the next generation of the consumer rebalance protocol](https://cwiki.apache.org/confluence/display/KAFKA/KIP-848%3A+The+Next+Generation+of+the+Consumer+Rebalance+Protocol)
- [KIP-932: Queues for Kafka (share groups)](https://cwiki.apache.org/confluence/display/KAFKA/KIP-932%3A+Queues+for+Kafka)
- [Apache Kafka (Wikipedia)](https://en.wikipedia.org/wiki/Apache_Kafka)
