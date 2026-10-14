---
id: arch-write-ownership-shard-routing
title: Partitioning write ownership
level: intermediate
minutes: 5
summary: Identify single-primary limits and choose shard routing that preserves common query locality.
sourceLesson: arch-scaling-writes
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
- The most common queries should hit **one** shard. Shard a chat app by `conversation_id` so that loading a conversation is a query confined to one shard.
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

## Key takeaways
- Replicas replay writes; reducing work, increasing resources or partitioning ownership addresses a write bottleneck.
- A useful shard key distributes writes while keeping common related-data queries local.
- Scatter-gather and cross-shard coordination are costs of losing locality.
- Changing plain modulo shard count remaps most keys; logical shards or consistent hashing make movement more deliberate.

## Further reading
- [Azure Architecture Center: Sharding pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/sharding)
- [Discord: How Discord stores trillions of messages](https://discord.com/blog/how-discord-stores-trillions-of-messages)
