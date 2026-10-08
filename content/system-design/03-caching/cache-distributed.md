---
id: cache-distributed
title: Distributed caching
level: advanced
minutes: 15
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

The simplest way to pick a node is to turn the key into a number and take the remainder after dividing by the number of nodes:

```formula
node = hash(key) mod N
where
node: the index of the node that holds the key, a whole number from 0 to N − 1
hash: a hash function, which turns the key (a string) into a large, evenly spread whole number
key: the cache key, such as user:42
mod: modulo, the remainder after whole-number division; 17 mod 4 = 1; written % in most programming languages
N: the number of cache nodes
In words: hash the key and use the remainder after dividing by the node count as the node number.
```

In code this is `hash(key) % N`. For example, a key whose hash is 1,000,003 goes to node 1,000,003 mod 4 = 3 in a four-node cluster.

This spreads keys evenly, but it falls apart when N changes. Going from 4 to 5 nodes, a key stays put only if its hash leaves the same remainder when divided by 4 as when divided by 5. The pair of remainders repeats every 20 numbers (20 is the smallest number divisible by both 4 and 5), and they match only for hashes that leave a remainder of 0, 1, 2 or 3 when divided by 20: 4 cases in 20. In general, growing from N to N + 1 nodes:

```formula
f_stay = 1 / (N + 1)
f_move = N / (N + 1)
f_move = 4 / (4 + 1) = 0.8
where
f_stay: the fraction of keys that keep their node
f_move: the fraction of keys that move to a different node
N: the number of nodes before adding one, here 4
In words: adding one node to N under hash-mod-N moves all but one key in N + 1, so the bigger the cluster, the worse it gets.
```

So about **1 in 5** keys stay, and **80%** of keys suddenly live on a different node, all of them missing at once. For a cache, that is a self-inflicted stampede on the database.

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
- Add a node N4 between N3 and N1: only the keys between N3 and N4 move.
- Remove N2: only N2's keys move, to the next node clockwise.

When the points are evenly spread, the new node ends up with an equal share of the ring, and that share is all that moves:

```formula
f_move ≈ 1 / (N + 1)
f_move ≈ 1 / (4 + 1) = 0.2
where
f_move: the fraction of keys that move when one node is added
N: the number of nodes before adding one, here 4
≈: approximately equal to; exact only when every node owns an equal arc of the ring
In words: adding a node takes over just its fair share of keys, about one in N + 1, instead of almost all of them.
```

Going from 4 to 5 nodes moves about 20% of keys, against 80% for hash mod N. Removing a node moves only that node's share, about 1 / N of the keys.

The problem with one point per node is uneven arcs: one node may own 40% of the ring. The fix is **virtual nodes**: each physical node is placed on the ring at 100–200 points. Arc sizes average out, and when a node fails its load is spread across many survivors rather than dumped on one neighbour.

Memcached clients typically use the **ketama** consistent hashing algorithm. Amazon's Dynamo and Cassandra use the same idea for databases.

### Redis Cluster: hash slots

Redis Cluster uses a fixed set of **16,384 hash slots**:

```formula
slot = CRC16(key) mod 16384
where
slot: the hash slot number, from 0 to 16,383
CRC16: a 16-bit cyclic redundancy check, a fast checksum function that turns the key into a number from 0 to 65,535; Redis uses the XMODEM variant
key: the cache key, or only the part inside {} when the key contains a hash tag
mod: modulo, the remainder after whole-number division; written % in code
16384: the fixed number of slots, 2 to the power 14
In words: checksum the key and take the remainder after dividing by 16,384 to get its slot.
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

**RDB** snapshots are compact and fast to load, but the `fork()` uses copy-on-write: under heavy writes, memory usage can nearly double while the snapshot runs. Every memory page the parent changes during the snapshot gets copied, so:

```formula
M_peak ≈ M × (1 + f)
M_peak ≈ 26 GB × (1 + 0.3) = 33.8 GB
where
M_peak: the peak memory used during the snapshot, in gigabytes (GB)
M: the memory the dataset uses normally, here 26 GB
f: the fraction of memory pages written to while the snapshot runs, between 0 and 1; here 0.3 (30%)
GB: gigabytes; 1 GB = 1,000,000,000 bytes
≈: approximately equal to
In words: the snapshot costs extra memory equal to the share of pages modified while it runs; if every page is touched, memory doubles.
```

A 26 GB dataset on a 32 GB machine fits normally, but with 30% of pages rewritten during the snapshot it needs about 33.8 GB and can be killed for running out of memory. Leave headroom (do not run Redis at 95% of RAM with RDB enabled).

**AOF** (append-only file) logs every write command, and is periodically rewritten to stay compact. Many deployments use both: AOF for durability, RDB for backups and fast restarts.

Why would a cache want persistence? **Warm restarts.** A 200 GB cache that restarts empty can take hours to refill and floods the database while doing so. Loading a saved state can reduce refill pressure, but restart and refill durations require measurement.

## Topology choices

| Option | Good for |
|---|---|
| Single node + replica | Workload fits one node |
| Client-side sharding | Memcached fleets |
| Redis Cluster | Large, self-managing |
| Proxy (mcrouter, Envoy) | Many clients, simple config |

A proxy layer hides the topology from clients and pools connections, which matters when thousands of app instances would otherwise each open connections to every node. Each node holds one pool per client that connects to it:

```formula
C_node = I × P
C_node = 2,000 × 4 = 8,000
C_node = 20 × 4 = 80
where
C_node: the connections one cache node must hold open
I: the number of clients connecting directly to the node: 2,000 app instances without a proxy, or 20 proxies with one
P: the connections each client keeps open to each node (its pool size), here 4
In words: without a proxy every app instance connects to every node; with one, only the proxies do, so the count per node falls a hundredfold here.
```

Facebook's **mcrouter** is a proxy of this kind for Memcached; it also routes invalidations and can replicate writes to pools of servers. Twemproxy (from Twitter) and Envoy's Redis proxy play the same role, and modern Memcached ships its own built-in proxy.

## Key takeaways
- Memcached: simple, multi-threaded, no built-in primary–replica durability; optional graceful warm restart is not crash-safe persistence. Redis: data structures, replication, persistence, clustering.
- Hash mod N remaps most keys when the node count changes; consistent hashing moves only about one node's share.
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
