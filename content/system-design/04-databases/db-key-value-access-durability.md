---
id: db-key-value-access-durability
title: Key-value access, expiry and durability
level: basic
minutes: 3
summary: Design exact-key and DynamoDB keyed access while checking session expiry, hot-item limits and Redis persistence.
sourceLesson: db-nosql-families
---

"NoSQL" isn't one thing. It's a loose label for databases that drop part of the relational model, usually joins, a fixed schema or multi-row transactions, in exchange for something else: horizontal scale, a more natural data shape, or speed on one access pattern.

The useful way to think about each family: **what does it make cheap, and what does it make expensive?**

## Key-value stores

The simplest model: a mapping from keys to values, whether embedded on one host or distributed. You `GET(key)`, `PUT(key, value)` and `DELETE(key)`. In a pure key-value model the value is opaque; products such as Redis and DynamoDB also understand structured values and offer additional operations.

- **Examples**: Redis (in memory), Amazon DynamoDB, Riak, etcd, RocksDB (embedded).
- **Cheap**: lookups by exact key. Actual latency depends on deployment, payload, consistency, load and network distance.
- **Expensive**: anything else. "Find all users in Leeds" means scanning everything unless you build your own index.

> [!analogy] Real-world analogy: a cloakroom ticket
> At a theatre cloakroom you hand over a ticket and the attendant walks straight to the matching hook. Asking "please find every blue coat" would mean checking every hook by hand.
>
> **How it maps:** The ticket number is the key, the coat is the value and the hook position is where the store keeps it. `GET(key)` is handing over the ticket; a query on a property of the values is the blue-coat search, which needs a full scan unless you maintain a separate index.
>
> **Where it stops:** A distributed key-value store spreads its hooks across many machines and keeps copies, and products such as Redis and DynamoDB understand some value structure. The comparison also says nothing about durability: coats do not vanish in a power cut, but an in-memory store's data can.

Check durability before treating an in-memory store as a system of record. Redis by default only snapshots to disk periodically (RDB), so a crash loses everything since the last snapshot. Its append-only file with `appendfsync everysec` narrows that to about a second of writes.

DynamoDB extends the model a little. Each item has a **partition key** (PK, hashed to pick a partition) and an optional **sort key** (SK), and items with the same partition key are stored together, sorted by sort key. That lets you do range queries *within* one partition:

```
PK = USER#42      SK = ORDER#2026-09-01
PK = USER#42      SK = ORDER#2026-09-14
PK = USER#42      SK = PROFILE
```

A `Query(PK = USER#42, SK begins_with ORDER#)` returns that user’s orders in normalized date-key order; results larger than the Query page limit require pagination. This is the basis of *single-table design*: you model access patterns first, then shape keys to serve them.

> [!note] DynamoDB in numbers
> DynamoDB targets single-digit millisecond service latency for common operations, rather than guaranteeing every request latency; items are at most 400 KB, partitions of up to 10 GB, and each partition serving up to 3,000 read units and 1,000 write units per second. DynamoDB splits busy partitions automatically, but it can't split a single hot *item*, so hot keys hit those limits long before the table does. Switching to on-demand billing doesn't lift them.

## Expiry, ordering and another lookup

Redis never returns an expired key: it deletes one when a client next touches it, and also samples keys in the background to remove expired ones nobody reads. DynamoDB TTL deletes expired items asynchronously, typically within a few days, and reads can still return them until then, so check the session expiry timestamp in the application before accepting it. Cleanup timing is not an authentication deadline.

For newest-first DynamoDB orders, use one fixed-width timestamp format and timezone in the sort key, and Query with `ScanIndexForward=false`. A lookup by order id needs another key mapping, such as a global secondary index (GSI); its reads are eventually consistent. A GSI is an extra index with its own keys, not a way to scan the table cheaply.

A strongly consistent read of an item up to 4 KB uses one read unit; an eventually consistent read uses half. So one hot small item can serve at most about 3,000 strongly consistent or 6,000 eventually consistent reads per second, whatever the table's total capacity or billing mode. A read cache can help when stale values are acceptable, but it changes the freshness guarantee.

## Key takeaways
- Exact-key lookups suit sessions and other known access patterns.
- DynamoDB partition and sort keys support ordered queries within a key; an index supports a different lookup.
- Expiry cleanup and crash durability need explicit checks rather than assumptions.

## Further reading
- [Amazon DynamoDB Developer Guide: What is DynamoDB?](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html)
- [docs.aws.amazon.com: Query](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Query.html)
- [docs.aws.amazon.com: TTL](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/TTL.html)
- [Redis: Persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)
