---
id: msg-kafka-consumer-progress-groups
title: Kafka consumer groups, progress and rebalances
level: intermediate
minutes: 4
summary: Separate partition ownership from completed work, and choose consumer or share groups for the workload.
sourceLesson: msg-kafka-log-streaming
---

A group’s assignment says who should read a partition; its committed offset says where recovery resumes. Those are distinct from what a worker thread has actually finished.

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

- **Eager rebalancing** (the original): every consumer revokes all its partitions, then the group reassigns from scratch. A rolling deploy of 30 instances means 30 stop-the-world pauses.
- **Cooperative rebalancing** (`CooperativeStickyAssignor`): consumers keep the partitions they are allowed to keep; only those that move are paused.
- **The new consumer group protocol** (KIP-848) is generally available from **Kafka 4.0**. The broker's group coordinator computes the assignment and hands out changes to each consumer independently, with no group-wide synchronisation barrier. Brokers enable it by default; clients opt in with `group.protocol=consumer`.

**Static membership** (`group.instance.id`) adds one more trick: a consumer that restarts with the same ID within the session timeout can retain its assignment without an otherwise unnecessary rebalance when the rest of the group and subscriptions remain stable.

### Committing offsets

Consumers record progress by **committing offsets** to an internal topic, `__consumer_offsets`. A committed offset of 1,043 means "the next record I want is offset 1,043".

- Commit **after** processing for at-least-once. A crash causes reprocessing from the last commit.
- Commit **before** processing for at-most-once. A crash skips records.
- `enable.auto.commit=true` uses a default 5-second auto-commit interval; scheduling details depend on client/protocol, which can commit offsets of records you have not finished processing if you hand work to other threads.

Because a consumer commits a single position per partition, a consumer group has no per-message ack. A strictly sequential handler can be blocked by one slow record. Parallel processing is possible, but contiguous offset commits and required per-key order still need coordination. This is the fundamental difference from a queue, and the ordering lesson covers how to deal with it.

> [!note] Share groups: queues on Kafka
> Kafka 4.0 shipped an early version of **share groups** (KIP-932, "queues for Kafka"), and Kafka 4.2 (2026) made them production-ready. Consumers in a share group cooperatively read the same partitions, each record is locked to one consumer and **acknowledged individually**, and delivery attempts are counted. You can then run more consumers than partitions, at the cost of per-partition ordering. Use them for job-style work; keep consumer groups for ordered streams.

## Key takeaways

- A conventional consumer group assigns each partition to one consumer, so extra consumers can sit idle.
- Commit the next offset after completed processing; polling into a worker pool does not mean that work is done.
- Incremental rebalance protocols and stable membership reduce unnecessary assignment pauses.
- Kafka 4.2 share groups provide per-record acquisition and acknowledgement for independent jobs.

## Further reading

- [Kafka consumer design (Confluent docs)](https://docs.confluent.io/kafka/design/consumer-design.html)
- [KIP-848: the next generation of the consumer rebalance protocol](https://cwiki.apache.org/confluence/display/KAFKA/KIP-848%3A+The+Next+Generation+of+the+Consumer+Rebalance+Protocol)
- [KIP-932: Queues for Kafka (share groups)](https://cwiki.apache.org/confluence/display/KAFKA/KIP-932%3A+Queues+for+Kafka)
- [Kafka 4.2 consumer configuration](https://kafka.apache.org/42/configuration/consumer-configs/)
