---
id: cache-distributed
title: Distributed caching
level: advanced
minutes: 14
summary: Redis versus Memcached, spreading keys across nodes with consistent hashing and hash slots, and what replication and persistence do (and don't) protect you from.
---

One cache server eventually runs out of memory, network bandwidth or CPU. Capacity depends on instance size, payload, commands and workload. A universal per-node capacity figure is absent because no representative benchmark is established here. If one instance cannot meet measured requirements, a cluster can partition the key space.

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
| String/item size | 1 MiB default item | 512 MiB string |

**Memcached** is deliberately simple. It is a pure cache: if a node dies, its data is gone and the clients rehash to the remaining nodes. Its multi-threaded design scales well across cores on a single large machine. Facebook ran thousands of Memcached servers.

**Redis** is a data structure server. Atomic operations like `INCR`, `ZADD` (leaderboards), `LPUSH` (queues), Lua scripts, pub/sub and streams make it useful far beyond caching. Command execution is single-threaded per instance (network I/O can be threaded since Redis 6), so you scale out by running more instances or shards, not by adding cores.

> [!note] Valkey
> In 2024 Redis moved from the BSD licence to source-available licences, and the Linux Foundation forked Redis 7.2 as **Valkey**, which AWS ElastiCache, Google Cloud Memorystore and others now offer. Redis 8 (2025) added the open-source AGPLv3 as a licence option. The two projects are starting to diverge in features, but for system design purposes they behave largely the same.

**Rule of thumb:** choose Memcached for a simple, large, multi-threaded look-aside cache of blobs. Choose Redis when you need data structures, atomic operations, replication or persistence.

## Partitioning

### The naive approach: hash mod N

```
node = hash(key) % N
```

This spreads keys evenly, but it falls apart when N changes. Going from 4 to 5 nodes, a key stays put only if `hash % 4 == hash % 5`, which is true for about **1 in 5** keys. So **80%** of keys suddenly live on a different node, and all of them miss at once. For a cache, that is a self-inflicted stampede on the database.

### Consistent hashing

Map both nodes and keys onto a ring (for example, the range 0 to 2³²). A key belongs to the **first node clockwise** from its position.

```
        0
     N1 .  k1
   .         .
 k3            N2
   .         .
     N3 . k2
```

- k1 → N2, k2 → N3, k3 → N1.
- Add a node N4 between N3 and N1: only the keys between N3 and N4 move, about 1/(N+1) of the total.
- Remove N2: only N2's keys move, to the next node clockwise.

The problem with one point per node is uneven arcs: one node may own 40% of the ring. The fix is **virtual nodes**: each physical node is placed on the ring at 100–200 points. Arc sizes average out, and when a node fails its load is spread across many survivors rather than dumped on one neighbour.

Memcached clients typically use the **ketama** consistent hashing algorithm. Amazon's Dynamo and Cassandra use the same idea for databases.

### Redis Cluster: hash slots

Redis Cluster uses a fixed set of **16,384 hash slots**:

```
slot = CRC16(key) % 16384
```

Each primary owns a set of slots. Adding a node means **migrating some slots** to it, key by key, while the cluster keeps serving. Clients cache the slot map and send each command straight to the right node.

- If a client uses an out-of-date map, the node replies `MOVED <slot> <host:port>`: the slot now lives elsewhere *permanently*, so the client updates its map.
- While a slot is mid-migration, a key that has already moved gets an `ASK` redirect: the client retries that one command on the target node (preceded by `ASKING`) but does *not* update its map, because the migration hasn't finished.

A fixed slot count is what makes this cheap. Moving a node's share means reassigning a few thousand slot numbers, not recomputing a ring for every key.

Multi-key operations (`MGET`, transactions, Lua) only work if all keys are in the same slot. **Hash tags** force that: only the part inside `{}` is hashed, so `{user:42}:profile` and `{user:42}:cart` share a slot.

> [!warning] Hash tags create hot slots
> Putting too much under one tag (`{global}:...`) piles all of it on a single node, recreating the bottleneck you sharded to escape.

## Replication

Redis supports a **primary with one or more replicas**. Replication is **asynchronous**: the primary acknowledges a write to the client, then streams it to replicas.

```
 client --write--> Primary
        <--ack---    |
                     | async
                     v
                  Replica
```

Failover is handled by **Redis Sentinel** (for non-clustered setups) or by Redis Cluster itself: if a primary is unreachable for long enough, a replica is promoted.

Consequences of asynchronous replication:

- **Acknowledged writes can be lost.** If the primary dies after acking but before the replica receives the write, the promoted replica never had it.
- **Replica reads can be stale.** Reading from replicas spreads load but may return slightly old values.
- **Split brain**: during a network partition, a client still talking to the old primary may write data that is discarded when the partition heals. `min-replicas-to-write` limits the damage by making the primary refuse writes if too few replicas are connected.

WAIT returns the number of replicas that acknowledged this connection’s preceding writes before the requested count or timeout; check that returned count. Receipt is not necessarily disk persistence. Acknowledgements reduce loss risk but do not make Redis strongly consistent or eliminate acknowledged-write loss during failover.

For a pure cache, losing a new insertion causes a miss, but losing an update or invalidation can leave an old value on the promoted replica. Keep freshness safeguards even when cache entries are disposable. Replication's real value for caches is **availability**, avoiding the "cache gone, database flooded" scenario from lesson 1.

Memcached has no replication. Facebook handled failures with a small pool of spare servers called **gutter**, about 1% of the memcached servers in a cluster. When a client gets no response from a server, it retries against gutter; on a gutter miss it reads the database and stores the result in gutter, where entries expire quickly. Facebook chose this over rehashing a failed server's keys across the survivors, because a single key can account for a large share of one server's traffic (the paper cites up to 20%), and moving it could overload its new home and cascade.

The paper reports that gutter cut client-visible failures by 99% and converted 10–25% of failures into hits each day. When a server failed completely, gutter's hit rate typically passed 35% within four minutes.

## Persistence

Memcached is ordinarily a volatile cache; optional warm restart preserves data over supported graceful restarts, not arbitrary crashes. Redis offers two persistence mechanisms:

| Mode | How | Loss on crash |
|---|---|---|
| RDB | Periodic snapshot via `fork()` | Since last snapshot |
| AOF `everysec` | Log every write, fsync 1/s | About 1 s |
| AOF `always` | fsync each write | Minimal; slow |
| None | Memory only | Everything |

**RDB** snapshots are compact and fast to load, but the `fork()` uses copy-on-write: under heavy writes, memory usage can nearly double while the snapshot runs. Leave headroom (do not run Redis at 95% of RAM with RDB enabled).

**AOF** (append-only file) logs every write command, and is periodically rewritten to stay compact. Many deployments use both: AOF for durability, RDB for backups and fast restarts.

Why would a cache want persistence? **Warm restarts.** A 200 GB cache that restarts empty can take hours to refill and floods the database while doing so. Loading a saved state can reduce refill pressure, but restart and refill durations require measurement.

## Topology choices

| Option | Good for |
|---|---|
| Single node + replica | Workload fits one node |
| Client-side sharding | Memcached fleets |
| Redis Cluster | Large, self-managing |
| Proxy (mcrouter, Envoy) | Many clients, simple config |

A proxy layer hides the topology from clients and pools connections, which matters when thousands of app instances would otherwise each open connections to every node. Facebook's **mcrouter** is a proxy of this kind for Memcached; it also routes invalidations and can replicate writes to pools of servers. Twemproxy (from Twitter) and Envoy's Redis proxy play the same role, and modern Memcached ships its own built-in proxy.

## Key takeaways
- Memcached: simple, multi-threaded, no built-in primary–replica durability; optional graceful warm restart is not crash-safe persistence. Redis: data structures, replication, persistence, clustering.
- `hash % N` remaps most keys when N changes; consistent hashing moves only about 1/N.
- Virtual nodes even out load and spread a failed node's keys across many survivors.
- Redis Cluster uses 16,384 hash slots with `MOVED` redirects; hash tags co-locate keys but can create hot slots.
- Redis replication is asynchronous: failover can lose acknowledged writes.
- Persistence in a cache is mostly about warm restarts; RDB `fork()` needs memory headroom.

## Further reading
- [Redis Cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/)
- [Redis replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/)
- [Redis persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)
- [Consistent hashing — Wikipedia](https://en.wikipedia.org/wiki/Consistent_hashing)
- [Choosing between Redis/Valkey and Memcached — ElastiCache](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/SelectEngine.html)
- [Scaling Memcache at Facebook — full paper PDF](https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf)
