---
id: msg-kafka-offsets-key-order
title: Kafka offsets, partitions and key ordering
level: intermediate
minutes: 4
summary: Follow an append-only log and keep one entity’s records in an ordered partition.
sourceLesson: msg-kafka-log-streaming
---

Queues delete messages once they are consumed. Kafka takes a different view: a topic is an **append-only log** that is kept for a configured time, and consumers simply remember **how far they have read**. This one design choice gives Kafka replay, cheap fan-out to many consumers and very high throughput. It also explains most of its sharp edges.

## The log and offsets

A log is an ordered sequence of records. Each record gets a sequential number, its **Kafka offset** (usually just called its offset), when it is appended.

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

- **With a key**: the producer hashes the key and uses the remainder after dividing by the partition count (the formula below). Equal serialized keys share a partition while partition count and partitioning configuration stay fixed; other clients or custom partitioners can differ.
- **Without a key**: the built-in Java producer stays with one partition until at least `batch.size` bytes have been produced there before it can switch. Keeping records together improves batching.

For keyed records, hashing gives a repeatable placement while the partition count and partitioner stay fixed. The optional reference shows how the default Java client's remainder-based mapping works:

```formula reference
p = h(k) mod N
where
p: the partition the record goes to, numbered from 0 to N − 1
h: the hash function: it turns the key's bytes into a large positive whole number; the default Java client uses murmur2
k: the record's key, for example an account ID
mod: modulo: the remainder after whole-number division; 19 mod 8 = 3 because 19 = 2 × 8 + 3
N: the number of partitions in the topic, here 8
In words: the same key always hashes to the same number, so while the partition count stays the same, every record with that key lands on the same partition.
```

In code, the default Java client writes this as `toPositive(murmur2(serializedKey)) % numPartitions`, where `%` is the modulo operator.

Ordering is guaranteed **only within a partition**. A stable key mapping gives an append order for that key; producer retries and concurrent processing must still preserve the intended business order. There is no ordering between partitions.

> [!warning] Changing partition count breaks key placement
> Adding partitions changes the placement rule, so new records for an existing key may land on a different partition from its older records. The two partitions can be consumed at different speeds, allowing a newer event to overtake an older one. Plan partition counts up front with measured headroom; resizing needs a migration barrier or another explicit ordering protocol.

> [!analogy] Real-world analogy: readers with separate bookmarks
> Several people read copies of the same book at different speeds, each keeping their own bookmark.
>
> **How it maps:** A partition log is the ordered book, and a consumer group's offset is its bookmark. Moving one bookmark does not move another, and reading a page does not erase it.
>
> **Where it stops:** Kafka can remove old records under retention or compaction. A topic also has several independent partition logs, so there is no single page order across the whole topic.

## Ordering guarantees, precisely

Kafka guarantees that records **in one partition** are stored and delivered in the order the leader appended them. Whether that matches the order your producer *sent* them depends on retries:

- With retries and `max.in.flight.requests.per.connection > 1` and **no** idempotence, batch 1 can fail, batch 2 succeed, then batch 1 succeed on retry: reordered.
- With `enable.idempotence=true` (the default since Kafka 3.0), the broker tracks a producer ID and per-partition sequence numbers, rejects out-of-order batches and drops duplicates. Ordering is preserved with up to 5 in-flight requests (`max.in.flight.requests.per.connection`, default 5).

Idempotence needs `acks=all`. If you set `acks=1` without explicitly enabling idempotence, the producer quietly turns idempotence off; if you enable it explicitly alongside `acks=1`, the producer refuses to start.

So the full guarantee is: **per partition, per producer, in send order, with idempotence on.**

## Key takeaways

- Offsets identify immutable records inside one partition; reading them does not delete them.
- Stable key mapping places one entity’s records together, while increasing partition count can remap it.
- Producer idempotence preserves retry order within the supported in-flight limit; business order still requires one ordered producer stream and ordered application processing.

## Further reading

- [Apache Kafka documentation: design](https://kafka.apache.org/documentation/)
- [Kafka 4.2 producer configuration](https://kafka.apache.org/42/configuration/producer-configs/)
