---
id: arch-write-ownership-shard-routing
title: Partitioning write ownership
level: intermediate
minutes: 4
summary: Identify single-primary limits and choose shard routing that preserves common query locality.
sourceLesson: arch-scaling-writes
---

In a single-writer system, read replicas offload reads but do not divide ownership of the write stream. That offload can free primary capacity. To address a write bottleneck, reduce work per write, increase resources, or partition write ownership.

This lesson covers the architectural patterns. The database module covers sharding internals (hash vs range partitioning, rebalancing, consistent hashing) in more depth.

## Why a single primary runs out

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

The diagram uses the remainder after division to choose an owner. The code spelling is `user_id % 4`; real systems commonly hash the key first to avoid patterns in raw identifiers.

Changing the divisor in modulo routing changes the destination of many existing keys. Adding one physical server therefore needs a migration plan, not just a new divisor.

Four equivalent shards can approach four times one shard's capacity if writes spread evenly and routing, coordination and other shared resources do not become bottlenecks.

The price is paid by queries that don't include the shard key. "Find all messages containing X" or "top 10 users by spend" must ask *every* shard and merge the answers (scatter-gather), so they get slower and more fragile as you add shards. A common answer is to send such queries to a separate system built for them, such as a search index or warehouse fed by CDC.

Choosing the shard key is the critical decision:

- It should spread load evenly (high cardinality, no dominant values).
- The most common queries should hit **one** shard. Shard a chat app by `conversation_id` so that loading a conversation is a query confined to one shard.
- Cross-shard operations (joins, transactions, global secondary indexes) become expensive or impossible, so pick a key that keeps related data together.

> [!warning] Resharding needs a migration plan
> Re-sharding a live system moves data while requests continue. Many small logical shards mapped onto fewer physical servers let operators move selected logical shards without changing the key-to-logical-shard mapping.

Changing plain hash-modulo routing can remap most keys. Logical shards or consistent hashing limit which assignments change, but affected data still needs safe transfer, routing updates and write-ownership cutover.

## Key takeaways
- Replicas replay writes; reducing work, increasing resources or partitioning ownership addresses a write bottleneck.
- A useful shard key distributes writes while keeping common related-data queries local.
- Scatter-gather and cross-shard coordination are costs of losing locality.
- Changing plain modulo shard count remaps most keys; logical shards or consistent hashing make movement more deliberate.

## Further reading
- [Azure Architecture Center: Sharding pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/sharding)
- [Discord: How Discord stores trillions of messages](https://discord.com/blog/how-discord-stores-trillions-of-messages)
