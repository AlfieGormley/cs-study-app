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

The router in the diagram picks a shard with the remainder after division:

```formula
s = u mod N
s = 42 mod 4 = 2
where
s: the shard number the row lives on, from 0 to N − 1
u: the shard key, here the numeric user ID (user_id); user 42 in the example
N: the number of shards, here 4
mod: modulo: the remainder after dividing u by N (42 ÷ 4 = 10 remainder 2)
In words: divide the user ID by the number of shards; the remainder says which shard owns that user.
```

In code this is written `user_id % 4`. Real systems usually apply it to a *hash* of the key rather than the raw ID, so that keys that happen to follow a pattern still spread evenly.

Four equivalent shards can approach four times one shard's capacity if writes spread evenly and routing, coordination and other shared resources do not become bottlenecks.

The price is paid by queries that don't include the shard key. "Find all messages containing X" or "top 10 users by spend" must ask *every* shard and merge the answers (scatter-gather), so they get slower and more fragile as you add shards. A common answer is to send such queries to a separate system built for them, such as a search index or warehouse fed by CDC.

Choosing the shard key is the critical decision:

- It should spread load evenly (high cardinality, no dominant values).
- The most common queries should hit **one** shard. Shard a chat app by `conversation_id` so that loading a conversation is a single-shard query.
- Cross-shard operations (joins, transactions, global secondary indexes) become expensive or impossible, so pick a key that keeps related data together.

> [!warning] Sharding is a one-way door
> Re-sharding a live system is one of the hardest migrations in engineering. Instagram famously pre-split into thousands of *logical* shards mapped onto a few physical servers, so that later they could move logical shards between machines instead of re-hashing data.

Note also that plain `hash(key) % N` (the same remainder rule, applied to a hash of the key) can remap a large fraction of keys when N changes. A key stays put only if its remainder happens to be the same for both shard counts. For hashes spread evenly, the share of keys that has to move when you add one shard is:

```formula
F_moved = N / (N + 1)
F_moved = 4 / (4 + 1) = 0.8 = 80 %
where
F_moved: the fraction of all keys whose shard changes, between 0 and 1
N: the number of shards before the change, here 4 (going to 5)
%: per cent; 0.8 = 80 %
In words: adding one shard to N moves almost everything, about N out of every N + 1 keys; going from 4 to 5 shards moves about 80 % of keys.
```

That holds because, out of every 20 consecutive hash values, only the 4 whose remainders are 0, 1, 2 and 3 under both rules stay (20 is the first number divisible by both 4 and 5). Logical shards (or consistent hashing) mean adding a server moves only the shards you choose.

## Write batching

Much of a write's cost is fixed overhead: a network round trip, a transaction, an `fsync`. Batching amortises it.

Suppose each commit has to wait for its own `fsync` (no grouping by the database). Then the number of flushes depends only on how many rows you put in each transaction:

```formula
F = R / B
F = 1000 / 1 = 1000 fsyncs
F = 1000 / 1000 = 1 fsync
where
F: the number of transactions, and so of fsync flushes to disk
R: the number of rows to write, here 1,000
B: rows per transaction (the batch size): 1 in the first case, 1,000 in the second
fsync: one forced flush of the log to durable storage, the slow fixed cost of a commit
fsyncs: plural of fsync
In words: 1,000 one-row transactions pay for 1,000 disk flushes; one 1,000-row transaction pays for one.
```

Each row still has to be written, so the saving is the fixed per-commit cost, not all of the work.

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

For example, take a 2-minute burst at 20,000 messages a second while workers drain 5,000 a second. During a burst, the queue grows by the difference between what arrives and what workers remove:

```formula
B = (A − D) × T
B = (20000 − 5000) /s × 120 s
B = 1800000
where
B: the peak backlog at the end of the burst, in messages
A: the arrival rate during the burst, here 20,000 messages per second (/s)
D: the drain rate: how many messages per second the workers finish, here 5,000/s
T: how long the burst lasts, in seconds (s): 2 minutes = 120 s
s: seconds
/s: per second
In words: 15,000 extra messages a second for 120 seconds piles up 1.8 million messages.
```

If traffic then drops to zero, the time to clear it is the backlog divided by the drain rate:

```formula
T_drain = B / D
T_drain = 1800000 / (5000 /s)
T_drain = 360 s
where
T_drain: time to empty the queue, in seconds (s): 360 s = 6 minutes
B: the backlog, 1.8 million messages
D: the drain rate, 5,000 messages per second (/s)
s: seconds
In words: 1.8 million messages at 5,000 a second take 6 minutes to clear.
```

If traffic doesn't drop to zero, use the spare rate instead: drain time is B divided by (D − arrival rate), which is why a queue barely below capacity takes a very long time to recover.

It works when the client doesn't need the result immediately (an order confirmation can arrive by email). It doesn't fix a *sustained* overload: if input exceeds drain rate forever, the queue grows without bound. You need monitoring on queue age and a way to shed load.

## Append-only designs

Updates may require lookup, concurrency control and index maintenance. Append-oriented storage can make I/O more sequential, but durability, indexing, validation and compaction still cost work. Buffered B-tree inserts do not necessarily perform a physical random read and write for every row.

Many write-heavy systems are built on this:

- **LSM-tree storage engines** (Cassandra, RocksDB, ScyllaDB, HBase) buffer writes in memory, flush sorted files sequentially, and merge them in the background (compaction). They trade buffering and sequential flushes against read amplification and compaction work. Compare measured sustained throughput: compaction can stall writes and an LSM engine is not universally faster than a B-tree.
- **Event logs**: Kafka writes every message to the end of a partition log with throughput depending on replication, acknowledgments, message size, batching, storage and network.
- **Event sourcing**: store every change as an immutable event (`ItemAdded`, `ItemRemoved`) and derive current state by replaying or projecting. Retained events can support audit history and projections; completeness, access control and write cost depend on the implementation.
- **Time-series data**: metrics and IoT readings are naturally append-only and partitioned by time.

> [!example] Counters as appends
> Instead of `UPDATE balance = balance - 10` with row locking, a ledger appends `(account, -10, ts)` rows (ts is the timestamp). The balance is a sum, kept current by a projection or periodic snapshot. Independent appends reduce contention and provide an audit trail. A no-overdraft rule still needs atomic balance validation, stream-version concurrency control or preallocated spending rights; appending debits alone does not prevent overspending.

Reading a balance from a ledger means adding the entries up, usually starting from the last saved snapshot so you don't sum the whole history every time:

```formula
balance = S + Σ e_i
balance = 100 + (−10) + 25 + (−5) = 110
where
balance: the account's current balance, in the account's currency (e.g. pounds, £)
S: the balance recorded in the latest snapshot, here £100
e_i: one ledger entry written after that snapshot: negative for a debit, positive for a credit
i: counts through the entries, 1, 2, 3, …
Σ: sigma, "the sum of": add up every e_i
In words: the balance is the last snapshot plus every change since; here £100 − £10 + £25 − £5 = £110.
```

## Hot partitions

Sharding assumes load spreads evenly. Real traffic is skewed: a celebrity's post, a flash-sale product, a single huge tenant. A **hot partition** gets far more traffic than the others and caps the whole system's throughput.

DynamoDB, for example, supports at most 1,000 write units/s and 3,000 read units/s per partition. Units are not generally requests: an ordinary write consumes one unit per 1 KiB, while strongly consistent reads consume one per 4 KiB; transactional operations cost more. The units a write consumes depend on the item's size, rounded up:

```formula
U = ⌈S / 1 KiB⌉
U = ⌈2.5 KiB / 1 KiB⌉ = ⌈2.5⌉ = 3
where
U: write units consumed by one standard write
S: the item's size, in kibibytes (KiB); here 2.5 KiB
KiB: kibibyte, 1,024 bytes
⌈ ⌉: ceiling: round up to the next whole number
In words: every started kibibyte of item costs one write unit, so a 2.5 KiB item costs 3.
```

So one partition takes at most 1,000 small (≤ 1 KiB) writes a second, or about 333 writes a second of 2.5 KiB items. A single item receiving 10,000 writes/s will throttle no matter how much total capacity the table has.

Mitigations:

1. **Key salting / write sharding**: spread one logical key across several physical keys, here 10:

```
key = "post:42#" + rand(0..9)
write: one of 10 sub-keys
read:  sum all 10
```

Writes spread 10 ways; reads must gather 10 items (fine for counters):

```formula
C = c_0 + c_1 + ... + c_9
where
C: the true count for post 42
c_0: the count stored under sub-key post:42#0
c_1: the count under post:42#1
...: and so on for the remaining sub-keys
c_9: the count under post:42#9
In words: the real total is the sum of the 10 partial counters.
```

Each sub-key gets about a tenth of the writes, so ten sub-keys lift the cap about tenfold, at the cost of 10 reads per lookup.

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
