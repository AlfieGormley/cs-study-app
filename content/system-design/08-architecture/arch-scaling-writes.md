---
id: arch-scaling-writes
title: Scaling writes
level: intermediate
minutes: 14
summary: Why writes are harder to scale than reads, and the architectural patterns that help, including sharding, batching, queues as shock absorbers, append-only designs and hot-partition mitigation.
---

In a single-writer system, read replicas offload reads but do not divide ownership of the write stream. That offload can free primary capacity. To address a write bottleneck, reduce work per write, increase resources, or partition write ownership.

This lesson covers the architectural patterns. The database module covers sharding internals (hash vs range partitioning, rebalancing, consistent hashing) in more depth.

## Why a single primary runs out

> [!note] Evidence gap
> Generic primary throughput, disk flush latency and Kafka broker throughput figures are omitted: no representative benchmark environment was supplied. Measure the actual workload.

Potential limits include:

- **Disk durability**: synchronous commits wait for the required durable log position. Group commit can share a flush across transactions; asynchronous commit and replication settings change the acknowledgment policy.
- **Locks and contention**: many transactions updating the same rows serialise.
- **Index maintenance**: applicable secondary indexes add work; partial indexes may exclude a row, and buffering changes physical I/O.
- **Replication**: every write is shipped to every replica.

Vertical scaling (a bigger box) is the first step and is underrated. Beyond that, you need patterns.

## Sharding (horizontal partitioning)

Split data by a **shard key** so each shard (its own primary) owns a subset of keys.

```
        [ router / client lib ]
         user_id % 4
       /      |       |      \
  [Shard0] [Shard1] [Shard2] [Shard3]
   users    users    users    users
   0,4,8..  1,5,9..  2,6,..   3,7,..
```

Four equivalent shards can approach four times one shard's capacity if writes spread evenly and routing, coordination and other shared resources do not become bottlenecks.

The price is paid by queries that don't include the shard key. "Find all messages containing X" or "top 10 users by spend" must ask *every* shard and merge the answers (scatter-gather), so they get slower and more fragile as you add shards. A common answer is to send such queries to a separate system built for them, such as a search index or warehouse fed by CDC.

Choosing the shard key is the critical decision:

- It should spread load evenly (high cardinality, no dominant values).
- The most common queries should hit **one** shard. Shard a chat app by `conversation_id` so that loading a conversation is a single-shard query.
- Cross-shard operations (joins, transactions, global secondary indexes) become expensive or impossible, so pick a key that keeps related data together.

> [!warning] Sharding is a one-way door
> Re-sharding a live system is one of the hardest migrations in engineering. Instagram famously pre-split into thousands of *logical* shards mapped onto a few physical servers, so that later they could move logical shards between machines instead of re-hashing data.

Note also that plain `hash(key) % N` can remap a large fraction of keys when N changes: going from 4 to 5 shards moves about 80% of keys. Logical shards (or consistent hashing) mean adding a server moves only the shards you choose.

## Write batching

Much of a write's cost is fixed overhead: a network round trip, a transaction, an `fsync`. Batching amortises it.

```
# Serial synchronous commits; no grouping
1 insert per txn:   1,000 txns, 1,000 fsyncs
1,000 rows per txn:     1 txn,      1 fsync
```

Examples:

- Multi-row `INSERT ... VALUES (...), (...), ...` or Postgres `COPY` for bulk loads.
- **Group commit**: databases combine several concurrent transactions into one log flush.
- **Kafka producers** batch messages per partition (`linger.ms`, `batch.size`), amortising request costs; added waiting, throughput and end-to-end latency depend on load and batching settings.
- **Client-side aggregation**: instead of writing every page view, count views in memory for 5 seconds and write `+137` once.

The cost is latency and the risk of losing an unflushed batch if the process crashes. Only batch in memory what you can afford to lose, or put a durable log in front.

## Queues as buffers (load levelling)

Traffic is spiky, and databases have a fixed write capacity. A **queue between producers and the database** absorbs bursts so the database can work at a steady rate.

```
 spike: 20k/s        steady: 5k/s
 [API] ---> [ Queue ] ---> [Workers] -> [DB]
             backlog
             grows,
             then drains
```

- The API accepts the request, enqueues it durably, and returns `202 Accepted`.
- Workers pull at a rate the database can sustain.
- If a 2-minute burst runs at 20,000/s and workers drain at 5,000/s, the backlog peaks at (20,000 − 5,000) × 120 = 1.8 million messages and takes another 6 minutes to clear if traffic then drops to zero.

It works when the client doesn't need the result immediately (an order confirmation can arrive by email). It doesn't fix a *sustained* overload: if input exceeds drain rate forever, the queue grows without bound. You need monitoring on queue age and a way to shed load.

## Append-only designs

Updates may require lookup, concurrency control and index maintenance. Append-oriented storage can make I/O more sequential, but durability, indexing, validation and compaction still cost work. Buffered B-tree inserts do not necessarily perform a physical random read and write for every row.

Many write-heavy systems are built on this:

- **LSM-tree storage engines** (Cassandra, RocksDB, ScyllaDB, HBase) buffer writes in memory, flush sorted files sequentially, and merge them in the background (compaction). They trade buffering and sequential flushes against read amplification and compaction work. Compare measured sustained throughput: compaction can stall writes and an LSM engine is not universally faster than a B-tree.
- **Event logs**: Kafka writes every message to the end of a partition log with throughput depending on replication, acknowledgments, message size, batching, storage and network.
- **Event sourcing**: store every change as an immutable event (`ItemAdded`, `ItemRemoved`) and derive current state by replaying or projecting. Retained events can support audit history and projections; completeness, access control and write cost depend on the implementation.
- **Time-series data**: metrics and IoT readings are naturally append-only and partitioned by time.

> [!example] Counters as appends
> Instead of `UPDATE balance = balance - 10` with row locking, a ledger appends `(account, -10, ts)` rows. The balance is a sum, kept current by a projection or periodic snapshot. Independent appends reduce contention and provide an audit trail. A no-overdraft rule still needs atomic balance validation, stream-version concurrency control or preallocated spending rights; appending debits alone does not prevent overspending.

## Hot partitions

Sharding assumes load spreads evenly. Real traffic is skewed: a celebrity's post, a flash-sale product, a single huge tenant. A **hot partition** gets far more traffic than the others and caps the whole system's throughput.

DynamoDB, for example, supports at most 1,000 write units/s and 3,000 read units/s per partition. Units are not generally requests: an ordinary write consumes one unit per 1 KiB, while strongly consistent reads consume one per 4 KiB; transactional operations cost more. A single item receiving 10,000 writes/s will throttle no matter how much total capacity the table has.

Mitigations:

1. **Key salting / write sharding**: spread one logical key across N physical keys.
   ```
   key = "post:42#" + rand(0..9)
   write: one of 10 sub-keys
   read:  sum all 10
   ```
   Writes spread 10 ways; reads must gather 10 items (fine for counters).
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
- Read replicas do not partition writes, though offloading reads can free primary headroom.
- Sharding multiplies write capacity, but only with a shard key that spreads load evenly and keeps common queries on one shard.
- Batching amortises fixed per-write costs (round trips, fsyncs) in exchange for latency and potential loss of unflushed data.
- Queues absorb bursts so databases run at a steady rate, but they can't fix sustained overload.
- Append-oriented structures can improve I/O locality but still incur durability, indexing, validation and compaction costs.
- Hot partitions cap throughput; salt keys, aggregate, or isolate heavy hitters.

## Further reading
- [Azure Architecture Center: Sharding pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/sharding)
- [Azure Architecture Center: Queue-Based Load Leveling](https://learn.microsoft.com/en-us/azure/architecture/patterns/queue-based-load-leveling)
- [AWS: Using write sharding to distribute workloads evenly (DynamoDB)](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-partition-key-sharding.html)
- [Wikipedia: Log-structured merge-tree](https://en.wikipedia.org/wiki/Log-structured_merge-tree)
- [Martin Fowler: Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html)
- [Discord: How Discord stores trillions of messages](https://discord.com/blog/how-discord-stores-trillions-of-messages)
