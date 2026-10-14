---
id: db-rebalancing-tenant-cutovers
title: Rebalancing and tenant cutovers
level: advanced
minutes: 3
summary: Plan partition movement, routing and a verified migration while isolating unusually large tenants.
sourceLesson: db-partitioning
---

Moving data is a live operation with a routing change at its end. Keep capture, verification and rollback visible, and choose a layout that can move unusually large tenants independently.

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

Doubling the shard count online (say from 8 to 16) usually looks like:

1. Create the new shards and start **backfilling** them from a snapshot.
2. Capture ongoing changes reliably (for example CDC from the snapshot position), with replay, ordering and reconciliation; unrelated application dual writes can diverge.
3. **Verify**: compare row counts and checksums.
4. **Cut over reads**, then writes, shard by shard, with a quick rollback path.
5. Clean up the moved data from the old shards.

Pick the **shard key** to keep each request on one shard. For a SaaS product, `tenant_id` is the classic choice: every query includes it, and cross-tenant joins are rare. Tenant sizes are usually very skewed, though, so map tenants to shards through a **directory** (lookup table) rather than a formula: then a giant tenant can be moved to a dedicated shard on its own. Cross-shard transactions need distributed commit protocols, covered in the distributed transactions module.

## Coordinate the final switch

For the tenant migration here, keep reads available while copying, then briefly queue that tenant's writes at cutover. Drain and reconcile captured changes before switching its write routing. Do not allow unrelated dual writes to pretend they form an atomic cutover. A dedicated tenant shard can itself need a second partition key if that tenant eventually outgrows one machine.

## Key takeaways
- Partition-count choices affect future growth and movement overhead.
- Coordinators, routing tiers or clients maintain the partition map.
- Backfill, capture changes, verify and coordinate cutover; tenant directories let outliers move independently.

## Further reading
- [Vitess documentation](https://vitess.io/docs/)
- [Citus: Choosing a distribution column](https://docs.citusdata.com/en/stable/sharding/data_modeling.html)
- [www.elastic.co: index modules](https://www.elastic.co/docs/reference/elasticsearch/index-settings/index-modules)
