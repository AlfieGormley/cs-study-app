---
id: msg-entity-order-hot-keys
title: Per-entity ordering and hot-key capacity
level: advanced
minutes: 4
summary: Choose the smallest ordered entity, then diagnose skew and shard limits.
sourceLesson: msg-ordering-backpressure
---

Two problems dominate real messaging systems once they are past the prototype stage. First, **ordering**: some messages must be applied in sequence, yet you want hundreds of consumers in parallel. Second, **flow control**: producers and consumers run at different speeds, and something has to give. This unit starts with ordering and hot keys. Later units cover flow control and the operational signal that ties them together: **consumer lag**.

## How much ordering do you need?

Global ordering (every message in one sequence) requires a common sequencing/coordination point, though ordered execution and replication can still use multiple machines. That rarely scales. Almost every real requirement is **per-entity ordering**: events for one account, one order, or one device must be in order, but events for different entities are independent.

```
acct A: open ─▶ deposit ─▶ close
acct B: open ─▶ withdraw
  (A and B may interleave freely)
```

The tool for this is a **partition key** (Kafka, Kinesis) or a **message group ID** (SQS FIFO, Azure Service Bus sessions). All messages with the same key go to the same ordered lane, and different keys spread across lanes.

| System | Ordered unit | Parallelism |
|---|---|---|
| Kafka | Partition | Partitions per group |
| Kinesis | Shard | Shards |
| SQS FIFO | Message group | Number of groups |
| Service Bus | Session | Number of sessions |

For sustained provisioned-shard sizing without record aggregation, a Kinesis shard supports 1 MB/s **or** 1,000 records per second of writes, whichever comes first, and shared GetRecords reads have a 2 MB/s shard limit (enhanced fan-out has per-consumer capacity), so you size shards on both bytes and record count and take the larger answer:

```formula
S = ⌈max(W / (1 MB/s), R / (1000/s))⌉
S = ⌈max(2 MB/s / (1 MB/s),
         4000/s / (1000/s))⌉
S = ⌈max(2, 4)⌉ = 4
where
S: the minimum number of shards
⌈ ⌉: ceiling: round up to the next whole number, because you cannot have part of a shard
max: the larger of the values inside the brackets
W: the bytes written per second, here 4,000 records of 500 bytes, which is 2 MB/s
R: the records written per second, here 4,000
MB: megabytes; "MB/s" means megabytes per second
s: seconds; "/s" means per second
In words: work out how many shards the byte rate needs and how many the record rate needs, and provision the larger number.
```

Small records hit the record limit first and large records hit the byte limit first. Both limits apply to each shard, so a hot partition key can overload one shard even when the stream's average is fine.

SQS FIFO is notable: it does not lock a whole partition. A single receive can return multiple messages in group order-17; additional receives for that group wait until the in-flight messages are deleted or visible again, but any other group can be served. So parallelism scales with the number of **active groups**, not a fixed partition count.

## Hot keys and skew

Hashing spreads keys evenly only if traffic per key is even. It rarely is. If one celebrity account produces 30% of events, the partition holding that key gets 30% of the load, and its consumer becomes the bottleneck no matter how many others you add.

Mitigations:

- **Pick a finer key.** Order by `conversationId` rather than `userId` if that is what ordering really needs.
- **Salt the hot key.** Spread `celebrity-1` across `celebrity-1#0`…`#7`, accepting that ordering is now only within each sub-key, and merge downstream.
- **Separate topic.** Route known heavy hitters to a dedicated, bigger pipeline.

## Key takeaways

- Per-entity lanes allow unrelated entities to run in parallel.
- Provisioned Kinesis shards must satisfy both byte-rate and record-rate limits.
- A hot key stays on one lane; finer keys, salting or dedicated pipelines can remove that bottleneck.
- Salt only when the required order permits it, and combine partial aggregates without counting an update twice.

## Further reading

- [Amazon SQS FIFO queues (AWS docs)](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/FIFO-queues.html)
- [Kafka consumer (Confluent docs)](https://docs.confluent.io/platform/current/clients/consumer.html)
