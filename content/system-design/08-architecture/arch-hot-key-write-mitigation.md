---
id: arch-hot-key-write-mitigation
title: Removing hot-key write bottlenecks
level: intermediate
minutes: 4
summary: Diagnose skew, relate DynamoDB write units to item size and compare salting, batching and tenant isolation.
sourceLesson: arch-scaling-writes
---

Partitioned writes scale only when traffic distributes well. This unit follows the skewed item or tenant that violates that assumption; the illustrated pipeline is a design example, not a benchmark.

## Hot partitions

Sharding assumes load spreads evenly. Real traffic is skewed: a celebrity's post, a flash-sale product, a single huge tenant. A **hot partition** gets far more traffic than the others and caps the whole system's throughput.

DynamoDB, for example, supports at most 1,000 write units/s and 3,000 read units/s per partition. Units are not generally requests: an ordinary write consumes one unit per 1 KiB, while strongly consistent reads consume one per 4 KiB; transactional operations cost more. The units a write consumes depend on the item's size, rounded up:

A standard write rounds item size up to whole kibibytes for capacity accounting. A 2.5 KiB item therefore consumes three write units.

So one partition takes at most 1,000 small (≤ 1 KiB) writes a second, or about 333 writes a second of 2.5 KiB items. A single item receiving 10,000 writes/s will throttle no matter how much total capacity the table has.

Mitigations:

1. **Key salting / write sharding**: spread one logical key across several stored keys, here 10. This is illustrative routing pseudocode, not executable Python; choose a salt randomly, update that sub-counter, and sum the sub-counters when reading:

```
key = "post:42#" + rand(0..9)
write: one of 10 sub-keys
read:  sum all 10
```

Reading the total requires combining all partial counters. Separate reads are not automatically a simultaneous snapshot.

Balanced random selection gives each sub-key roughly a tenth of the writes. A capacity gain still requires suitable physical partition placement and spare table capacity; ten logical keys do not guarantee ten independent physical partitions.

2. **Better key choice**: `date` concentrates today's writes on one logical key. Physical splitting depends on the store, sort keys and indexes; do not equate a partition-key value with one permanent physical partition. A well-distributed device_id (or device_id + date) reduces this concentration.
3. **Batch the hot key**: aggregate increments in memory or a stream processor and write once per second.
4. **Isolate big tenants**: move a huge customer onto dedicated shards.
5. **Adaptive splitting**: some systems (DynamoDB's adaptive capacity, Bigtable tablet splitting) split hot ranges automatically. DynamoDB can even move a very hot item onto a partition of its own, but a single *item* can't be split, so it's still capped at one partition's limit.

| Symptom | Likely fix |
|---|---|
| One counter hot | Salt + sum |
| Time-based key hot | Add high-cardinality prefix |
| One tenant hot | Dedicated shard |
| Bursty writes | Queue + steady workers |

## Putting it together

An illustrative write-heavy pipeline might look like this. The 64-partition choice is not a validated capacity recommendation:

```
 apps -> [API, stateless]
            |  batch per request
            v
         [Kafka, 64 partitions]
            |  consumers batch
            v
         [Cassandra / LSM store]
          sharded by device_id
```

Each layer uses a different trick: stateless ingest, a durable append-only log as a buffer, batched consumers, and an LSM store partitioned on a high-cardinality key.

## Key takeaways
- A single hot item can throttle while total table or shard capacity remains idle.
- Capacity units depend on item size and operation type, not simply request count.
- Salting spreads writes but adds read aggregation; adaptive capacity cannot split one item.
- Use higher-cardinality keys, aggregate increments or isolate heavy tenants, then validate the whole pipeline.

## Further reading
- [AWS: Using write sharding to distribute workloads evenly (DynamoDB)](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-partition-key-sharding.html)
- [Discord: How Discord stores trillions of messages](https://discord.com/blog/how-discord-stores-trillions-of-messages)
