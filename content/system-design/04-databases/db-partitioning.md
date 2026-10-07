---
id: db-partitioning
title: Partitioning and sharding
level: advanced
minutes: 16
summary: Range versus hash partitioning, consistent hashing, hot spots, secondary indexes on sharded data, rebalancing and resharding.
---

Replication gives you copies of the same data. **Partitioning** splits data into subsets; **sharding** distributes them among nodes. Systems use different physical units: MongoDB chunks/shards, Elasticsearch shards, HBase regions and Bigtable tablets. Cassandra virtual nodes own token ranges and are not the same thing as CQL partitions. You partition when one machine can't hold the data or absorb the write rate.

The goal is to spread data *and load* evenly. A partition that gets far more than its share is a **hot spot**, and it caps the throughput of the entire system.

In practice, each partition is also replicated, so a node holds replicas of several partitions:

```
        P1      P2      P3
Node A: lead    foll    -
Node B: foll    lead    foll
Node C: -       foll    lead
```

## Range partitioning

Assign contiguous ranges of the key to each partition, like volumes of an encyclopaedia: A–C, D–F, and so on.

```
 key range        partition
 [a ... f)    ──►   P1
 [f ... m)    ──►   P2
 [m ... t)    ──►   P3
 [t ... ∞)    ──►   P4
```

- **Pro**: range scans are efficient. "All events between 09:00 and 10:00" touches the partitions overlapping that range; the number depends on boundaries and data volume.
- **Con**: hot spots when writes cluster in one range. If the key is a timestamp, *all* of today's writes go to the last partition while the others sit idle.
- Boundaries are usually chosen automatically, splitting a partition when it grows too big according to engine-specific policies and thresholds; verify these for the deployed version.

Fix for time-ordered hot spots: prefix the key with something that spreads load, e.g. `sensor_id + timestamp`, so writes from different sensors land in different ranges. Range queries then need one query per sensor.

## Hash partitioning

Apply a hash function to the key and assign ranges of the *hash* to partitions. A good hash spreads even sequential keys uniformly.

```
partition = hash(key) mod N   ← naive
```

- **Pro**: even distribution, no clustering.
- **Con**: range queries on the key are gone: adjacent keys are scattered. Cassandra's compromise is a *compound* key: hash the partition key, then keep rows sorted by the clustering columns within each partition.

> [!warning] Never use hash mod N directly
> If N changes from 10 to 11, a key stays put only if `hash mod 10 = hash mod 11`, which is true for about 1 in 11 keys. Adding one node moves ~91% of the data.

## Consistent hashing

Place both nodes and keys on a ring of hash values (say 0 to 2⁶⁴). Each key belongs to the first node clockwise from it.

```
            0
        N1 ●
      /       \
  k3 ·         · k1
    |           |
 N3 ●           ● N2
      \       /
        · k2
  k1 → N2, k2 → N3, k3 → N1
```

When a node joins, it takes over keys only from its clockwise neighbour; when one leaves, its keys move to the next node. Only about **1/N** of keys move.

Plain consistent hashing gives uneven ranges, and a newly added node only relieves one neighbour. The fix is **virtual nodes**: each physical node owns many small points on the ring (Cassandra historically used 256 per node, now 16 by default with a smarter allocation algorithm). Load evens out, and a new node can take small slices from many existing nodes, rather than necessarily every node.

Used by Amazon Dynamo, Cassandra, Riak, and the client-side sharding in many cache libraries (such as memcached clients using the "ketama" scheme). A related approach used by Redis Cluster is a fixed set of **16,384 hash slots** assigned to nodes.

Redis Cluster only allows a multi-key command (`MGET`, a transaction, a Lua script) when all its keys are in the same slot. **Hash tags** make that possible: only the part inside `{...}` is hashed, so `{user42}:cart` and `{user42}:profile` always share a slot.

## Hot spots and skew

Even with perfect hashing, a single hot *key* lands on one partition. A celebrity with 100 million followers, or a viral product during a sale, can overload it.

Mitigations:

- **Key splitting (salting)**: write to `key#0` … `key#9` (random suffix), creating ten logical keys that can spread load; they are not guaranteed to occupy ten physical partitions. Reads gather across those keys. Only do this for the few known-hot keys.
- **Caching** the hot key's reads in front of the database.
- **Adaptive capacity**: DynamoDB automatically shifts capacity to busy partitions and splits them, even isolating frequently accessed items on their own partitions. A single item still can't exceed one partition's limits (about 3,000 RCU / 1,000 WCU per second).

## Secondary indexes on partitioned data

Partitioning by primary key makes primary-key lookups easy. But what about "find all red cars" when cars are partitioned by `car_id`?

### Local (document-partitioned) indexes

Each partition indexes only its own data.

- **Writes**: cheap, local to one partition.
- **Reads**: must ask *every* partition and merge (**scatter-gather**). Tail latency is the slowest partition's latency.
- Used by MongoDB, Cassandra secondary indexes, Elasticsearch.

### Global (term-partitioned) indexes

The index itself is partitioned by the indexed value: all `colour=red` entries live in one index partition.

- **Reads**: go to one index partition.
- **Writes**: one row write may update index partitions on other nodes, so global indexes are usually **updated asynchronously**.
- DynamoDB global secondary indexes are eventually consistent, typically within a fraction of a second.

| | Local index | Global index |
|---|---|---|
| Write cost | One partition | Several |
| Read cost | All partitions | One partition |
| Freshness | Engine-dependent (e.g. search refresh) | Engine-dependent; often async |

### DynamoDB's two kinds of index

DynamoDB offers both, with its own twist on "local":

- A **local secondary index (LSI)** keeps the table's partition key and adds a different sort key. Because you must supply the partition key to query it, it reads one partition, not all of them. It supports strongly consistent reads, but you can have at most **5** per table, they can only be defined **when the table is created**, and each partition-key value's items (table plus LSIs) are capped at **10 GB**.
- A **global secondary index (GSI)** can use any attribute as its keys. The default quota is **20** per table (adjustable), you can add or remove them at any time, but reads are eventually consistent only. Each GSI has its own capacity, and if a GSI can't keep up with writes, DynamoDB throttles writes to the *base table*.

## Rebalancing

Over time, data grows, nodes are added, and load shifts. **Rebalancing** moves partitions between nodes. Goals: even load afterwards, keep serving during the move, and move as little data as possible.

Strategies:

- **Fixed number of partitions**: create many more partitions than nodes up front (e.g. 1,000 partitions on 10 nodes), and move whole partitions when nodes join. Elasticsearch shards, Riak, Couchbase vBuckets and Redis Cluster slots work this way. Choose the count carefully: too few limits future growth; too many adds overhead. (Elasticsearch fixes an index's primary shard count at creation; changing it later means reindexing or the split API.)
- **Dynamic partitioning**: split a partition when it exceeds a size threshold, merge when it shrinks in engines that support those operations. Initial partition counts and split/merge policies vary; pre-split only when appropriate for that engine.
- **Proportional to nodes**: a fixed number of partitions per node (Cassandra's vnodes).

> [!tip] Keep a human in the loop
> Fully automatic rebalancing plus automatic failure detection can cascade: a slow node is declared dead, its data is moved, the move overloads others, and they're declared dead too. Many operators require a person to approve rebalancing.

## Request routing

Something must know which node holds which partition:

1. Any node accepts a request and forwards it (Cassandra's gossip-based coordinator).
2. A routing tier knows the map (MongoDB's `mongos`, Vitess's `vtgate`), often backed by ZooKeeper or etcd.
3. The client knows the map (Redis Cluster clients, with `MOVED` redirects when it's stale).

## Resharding a relational database

Postgres and MySQL don't shard natively, so teams shard at the application layer or use **Vitess** (YouTube, Slack, GitHub), **Citus** (Postgres), or a distributed SQL database (CockroachDB, Spanner, YugabyteDB, TiDB).

Moving from N to 2N shards online usually looks like:

1. Create the new shards and start **backfilling** them from a snapshot.
2. Capture ongoing changes reliably (for example CDC from the snapshot position), with replay, ordering and reconciliation; unrelated application dual writes can diverge.
3. **Verify**: compare row counts and checksums.
4. **Cut over reads**, then writes, shard by shard, with a quick rollback path.
5. Clean up the moved data from the old shards.

Pick the **shard key** to keep each request on one shard. For a SaaS product, `tenant_id` is the classic choice: every query includes it, and cross-tenant joins are rare. Tenant sizes are usually very skewed, though, so map tenants to shards through a **directory** (lookup table) rather than a formula: then a giant tenant can be moved to a dedicated shard on its own. Cross-shard transactions need distributed commit protocols, covered in the distributed transactions module.

## Key takeaways
- Partition when data or write volume exceeds one machine; the goal is even load, not just even data.
- Range partitioning keeps range scans fast but risks hot spots; hash partitioning spreads load but loses range queries.
- Consistent hashing with virtual nodes moves only about 1/N of the keys when membership changes; never use hash mod N.
- Local secondary indexes mean scatter-gather reads; global ones mean multi-partition, often asynchronous writes.
- Choose a shard key that keeps each request on one shard, and treat rebalancing and resharding as careful, observable operations.

## Further reading
- [Wikipedia: Consistent hashing](https://en.wikipedia.org/wiki/Consistent_hashing)
- [DynamoDB: Designing partition keys to distribute your workload](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-partition-key-design.html)
- [DynamoDB: Global secondary indexes](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GSI.html)
- [DynamoDB: Local secondary indexes](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/LSI.html)
- [Redis Cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/)
- [MongoDB: Sharding](https://www.mongodb.com/docs/manual/sharding/)
- [Vitess documentation](https://vitess.io/docs/)
