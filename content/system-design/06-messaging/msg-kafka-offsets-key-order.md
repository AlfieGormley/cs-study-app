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
- **Without a key**: the producer's built-in sticky partitioner fills a batch for one partition, then moves to another, which gives good batching.

For keyed records, the choice is modular arithmetic: turn the key into a large number with a hash function, then take the remainder after dividing by the number of partitions:

```formula
p = h(k) mod N
p = 19 mod 8 = 3
where
p: the partition the record goes to, numbered from 0 to N − 1
h: the hash function: it turns the key's bytes into a large positive whole number; the default Java client uses murmur2
k: the record's key, for example an account ID
mod: modulo: the remainder after whole-number division; 19 mod 8 = 3 because 19 = 2 × 8 + 3
N: the number of partitions in the topic, here 8
In words: the same key always hashes to the same number, so while the partition count stays the same, every record with that key lands on the same partition.
```

Here 19 stands for whatever hash the key produces. In code, the default Java client writes this as `toPositive(murmur2(serializedKey)) % numPartitions`, where `%` is the modulo operator.

Ordering is guaranteed **only within a partition**. A stable key mapping gives an append order for that key; producer retries and concurrent processing must still preserve the intended business order. There is no ordering between partitions.

> [!warning] Changing partition count breaks key placement
> Adding partitions changes N in the formula above, so new records for an existing key may land on a different partition from its older records. A key hashing to 19 goes to partition 3 with 8 partitions (19 mod 8), but to partition 7 with 12 (19 mod 12). Ordering per key is broken across the change. Plan partition counts up front (over-provision moderately) for keyed topics.

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
