---
id: cache-hot-key-relief
title: Relieve a single overloaded cache key
level: advanced
minutes: 3
summary: Estimate local-cache fills and compare copied keys, read replicas and hot-key detection.
sourceLesson: cache-failure-modes
---

Adding ordinary shards spreads different keys, but leaves one exceptionally popular key on one owner. To relieve it, distribute reads for that value while meeting its staleness requirement.

## 2. Hot keys

Sometimes a single key gets an enormous share of traffic: a celebrity's profile, a flash-sale product, a live match score. Partitioning doesn't help, because one key lives on **one** node. If that node handles 100k ops/s and the key gets 300k ops/s, it saturates regardless of cluster size.

Fixes:

- **Local (in-process) cache** in front of Redis with a 1–5 s TTL. Each server goes back to Redis about once per TTL for that key, so Redis load now depends on the number of servers, not on the read rate. With 100 app servers and a 1 s TTL, that is roughly 100 reads a second instead of 300,000, assuming per-server miss coalescing and no early eviction. The price is up to one local TTL of extra staleness.
- **Key replication / splitting**: store copies as `score:match9#0` to `score:match9#9` and have readers pick a random suffix. Load spreads over up to 10 nodes; writers update all copies. If the 10 copies really do land on 10 different nodes, each gets about a tenth of the reads: 300,000 reads a second becomes about 30,000 a second per node.
- **Read replicas** for the shard holding the hot key.
- **Detect them**: `redis-cli --hotkeys` works when an LFU eviction policy is set, Redis 8.6 added `HOTKEYS` commands that track and report the keys using the most CPU time or network bytes, and managed services offer per-key monitoring. Tooling changes between versions (this list is as of late 2026). You can't fix what you can't see.

> [!example] Hot keys at Twitter-scale
> As an illustrative workload, suppose a celebrity with 100 million followers posts. Every timeline render that includes the tweet reads the same tweet object. Process-local caches can absorb repeated reads of the object when the allowed staleness fits; this is a design illustration, not a measured description of Twitter’s deployed system.

## Key takeaways
- One hot key can saturate one shard even when the rest of the cluster is idle.
- Per-process caches reduce Redis fills to roughly one per server per TTL when coalescing and retention assumptions hold.
- Copied keys or read replicas can spread reads, but copies need coordinated updates and suitable freshness guarantees.

## Further reading
- [Redis anti-patterns](https://redis.io/tutorials/redis-anti-patterns-every-developer-should-avoid/)
- [Redis CLI hot-key detection](https://redis.io/docs/latest/develop/tools/cli/)
