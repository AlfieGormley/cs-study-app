---
id: cache-distributed-engine-choice
title: Choose a distributed cache engine
level: advanced
minutes: 3
summary: Compare Redis, Valkey and Memcached by operations, threading, replication and restart behaviour.
sourceLesson: cache-distributed
---

One cache server eventually runs out of memory, network bandwidth or CPU. How much one node can handle depends on instance size, payload, commands and workload, so there is no single per-node figure worth memorising: benchmark your own traffic. If one instance cannot meet the measured requirements, a cluster can partition the key space.

Distributing a cache raises three questions:

1. **Partitioning**: which node holds which key?
2. **Replication**: what happens when a node dies?
3. **Persistence**: does the data survive a restart?

## Redis vs Memcached

Both are in-memory key-value stores whose latency depends on payload, network, commands and load. They make different trade-offs.

| | Memcached | Redis |
|---|---|---|
| Data model | Opaque strings | Strings, hashes, lists, sets, sorted sets, streams |
| Threads | Multi-threaded | Mostly single-threaded commands |
| Persistence | Optional graceful warm restart; not crash-safe durability | RDB snapshots, AOF |
| Replication | None built in | Primary–replica |
| Clustering | Client-side | Redis Cluster |
| String/item size | 1 MiB default item | 512 MiB default string limit |

**Memcached** is deliberately simple. It is a pure cache: if a node dies, its data is gone and the clients rehash to the remaining nodes. Its multi-threaded design scales well across cores on a single large machine. Facebook ran thousands of Memcached servers.

**Redis** is a data structure server. Atomic operations like `INCR`, `ZADD` (leaderboards), `LPUSH` (queues), Lua scripts, pub/sub and streams make it useful far beyond caching. Command execution is single-threaded per instance (network I/O can be threaded since Redis 6), so you scale out by running more instances or shards, not by adding cores.

> [!note] Valkey
> In March 2024 Redis moved new versions from the BSD licence to source-available licences, and a Linux Foundation project forked Redis 7.2 as **Valkey**, which AWS ElastiCache, Google Cloud Memorystore and others offer. Redis 8 (2025) added the open-source AGPLv3 as a licence option. This history is as of late 2026. The two projects are starting to diverge in features, but shared ancestry does not guarantee identical versioned features, threading, durability or managed-service behaviour. Check the chosen engine and service version.

**Rule of thumb:** choose Memcached for a simple, large, multi-threaded look-aside cache of blobs. Choose Redis when you need data structures, atomic operations, replication or persistence.

## Key takeaways
- Measure node limits from your payload, commands and workload before deciding to partition.
- Memcached serves simple blobs with multiple threads; Redis adds atomic data structures, replication and persistence.
- Engine features and licences evolve; choose from required operations and deployed versions rather than universal performance figures.

## Further reading
- [Choosing between Redis/Valkey and Memcached — ElastiCache](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/SelectEngine.html)
- [Redis licences](https://redis.io/legal/licenses/)
- [Valkey](https://valkey.io/)
- [Warm restart — Memcached](https://docs.memcached.org/features/restart/)
