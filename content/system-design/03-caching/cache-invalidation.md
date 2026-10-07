---
id: cache-invalidation
title: Invalidation and consistency
level: intermediate
minutes: 13
summary: Why caches serve stale data, the race conditions between database and cache writes, and the tools that tame them — delete over update, versioning, leases and change data capture.
---

> There are only two hard things in Computer Science: cache invalidation and naming things. — Phil Karlton

A cache holds a copy. The moment the original changes, the copy is wrong. **Invalidation** is how you bring the copy back in line, and it is hard because the cache and the database are two separate systems with no shared transaction. Any sequence of operations across them can be interleaved with other requests, or fail halfway.

This lesson is about the cache-aside world (app, Redis, database), which is where most of these bugs live.

## The options for keeping a cache fresh

1. **Expire it (TTL).** Bound the lifetime of a cached copy after insertion. Data can be older than one TTL if a delayed read or lagging replica refills the cache.
2. **Delete it on write.** The writer removes the key; the next read reloads.
3. **Update it on write.** The writer sets the new value in the cache.
4. **Let the database tell you.** Stream the database's change log and invalidate from that.

Nearly every production design is TTL plus one of the others. TTL limits the residence of one copy; repeated stale refills can extend the age of data served.

## Stale reads are the normal case

Even a perfect design has a short window where the cache is stale:

```
 t1  writer: UPDATE row (commit)
 t2  reader: GET key -> old value
 t3  writer: DEL key
```

Between t1 and t3 readers see the old value. The window depends on request timing, failures and invalidation delivery; whether it is tolerable is a product requirement. The real problems are races that leave stale data in the cache **indefinitely** (until TTL).

## Race 1: update-on-write with concurrent writers

Two requests update the same user at almost the same time, and each writes the DB then sets the cache.

```
 A: UPDATE name='Ann'
 B: UPDATE name='Bea'      (DB = Bea)
 B: SET cache 'Bea'
 A: SET cache 'Ann'        (cache = Ann)
```

The database says `Bea`, the cache says `Ann`, and it stays wrong until the TTL. Network delays make A's cache write arrive after B's even though A's database write came first.

**This is why deleting is preferred over updating.** Deletes are idempotent and commutative: two deletes in either order leave the same result (an empty key), and the next reader loads the true value.

## Race 2: the cache-aside read/write race

Delete-on-write still has a race, involving a slow reader.

```
 Reader R                Writer W
 GET -> miss
 SELECT -> old value
                         UPDATE -> new
                         DEL key
 SET key = old value
```

R read the old row before W committed, but its `SET` lands after W's `DEL`. The cache now holds the old value with a fresh TTL, and nobody will delete it again.

This interleaving is possible even without an exceptional pause; its frequency depends on the workload. Pauses and network delays widen the opportunity. Facebook's memcache paper calls a write like R's a **stale set**: a value put into the cache that no longer reflects the latest data.

### Mitigations

- **Short TTLs** bound how long the bad value survives.
- **Delayed double delete**: delete, then delete again after a delay longer than a typical read (say 500 ms). It narrows the window but is a heuristic, not a guarantee.
- **Leases** (below) fix it properly.
- **Versioned writes** (below) make stale sets lose.

## Versioning

Store a version with each cached value (a database-ordered row version or other strictly increasing per-record revision). Only allow a cache write if it is **newer** than what is there.

```python
# Atomic "set if newer" (Redis Lua)
SET_IF_NEWER = """
local cur = redis.call('HGET', KEYS[1], 'v')
if cur and
   tonumber(cur) >= tonumber(ARGV[1]) then
  return 0
end
redis.call('HSET', KEYS[1],
  'v', ARGV[1], 'data', ARGV[2])
redis.call('EXPIRE', KEYS[1], ARGV[3])
return 1
"""
```

The Lua example assumes non-negative integer versions no greater than 2^53 − 1, which `tonumber` can compare exactly, and retained version metadata. With these assumptions, Race 1 is fixed: A's late write of version 7 is rejected because B already wrote version 8. Versioning alone does not fix Race 2 after a delete, because the key is empty and any version is "newer" than nothing. A tombstone can retain the new version floor, but its comparison metadata must survive until older fills are impossible or rejected by another authority. Expiry/eviction loses that protection. A tombstone-aware script must permit equal-version data to replace that tombstone; the simple strict-greater script below does not do so.

A different form of versioning is **versioned keys**: include a version in the key name, such as `user:42:v8`. The writer bumps the version (stored somewhere cheap); readers build the key from the current version, and old keys simply age out via TTL. Fingerprinted asset URLs are the HTTP version of this.

## Leases (Facebook memcache)

Facebook's 2013 paper *Scaling Memcache at Facebook* introduced **leases** to fix both stale sets and thundering herds.

1. On a miss, memcached gives the client a **lease token** for that key.
2. The client reads the database and calls `set` with the token.
3. If the key was **deleted** in the meantime, the token is invalidated and the `set` is rejected.

```
 R: get -> miss, token=T1
 R: SELECT -> old
 W: UPDATE, DELETE key (T1 voided)
 R: set(key, old, T1) -> REJECTED
```

The stale set in Race 2 simply fails. The paper compares this to load-link/store-conditional on a CPU: the write only succeeds if nothing touched the key in between.

Leases also tame **thundering herds**. By default Facebook's servers handed out at most one token per key every 10 seconds. Other clients that missed were told to wait briefly and retry; the token holder usually set the value within a few milliseconds, so the retry tended to hit. Over a week of measurements on keys particularly prone to herds, the paper reports peak database query rates falling from 17K/s without leases to 1.3K/s with them.

A refinement lets readers accept **stale values**: a deleted item is kept briefly in a side structure, and a miss can return it marked as stale. Applications that can tolerate slightly old data carry on without waiting.

Leases were Facebook's own extension, but modern memcached (1.6+) offers similar ideas through its *meta commands*, which can tell one client it has "won" the right to recache a key while others are served a stale value.

## Change data capture (CDC)

Instead of every writer remembering to invalidate, let the **database's commit log** drive invalidation.

```
 App --> DB --binlog/WAL--> CDC consumer
                              |
                              v
                          DEL keys
```

Facebook's version works slightly differently. SQL statements that modify data are amended to carry the memcache keys to invalidate. A daemon called `mcsqueal` on each database reads the committed statements from the commit log, extracts those deletes, and broadcasts them in batches to every frontend cluster in the region (via `mcrouter`). Because the keys travel with the transaction, lost or misrouted invalidations can simply be replayed from the log.

Today you might use Debezium reading the Postgres WAL or MySQL binlog, publishing to Kafka, with a consumer that maps changed rows to keys and deletes them.

**Benefits**: invalidation can cover committed changes from all configured logged tables regardless of client. Preserve relevant per-key order, include every dependent key and account for filters, publication scope, retention and failed delivery; a pipeline does not automatically provide global commit-order consumption. Consumers can retry failed deletes.

**Costs**: added latency that depends on capture, batching, processing and delivery, more infrastructure, and you must map rows to the cache keys that depend on them, which is hard for cached aggregates or joins.

## Read-your-writes

Users notice staleness most when it's *their own* change. Even if global staleness of a few seconds is fine, the person who just clicked "Save" expects to see it. Options:

- Version-aware write-through with ordering/failure safeguards, or carry the committed version and require reads to return at least that version.
- Invalidate synchronously in the writer's own cluster as well as through the slower CDC pipeline. Facebook's web servers did exactly this for read-after-write within a request's cluster.
- Remember "user 42 wrote at time t" and bypass the cache for that user; a fixed-duration window is a heuristic unless replica lag and stale fills are bounded. A required-version check is stronger.
- Facebook used **remote markers** across regions: after a write in a non-primary region, a marker tells subsequent reads to go to the primary database until replication catches up.

## Delete vs update: summary

| | Delete on write | Update on write |
|---|---|---|
| Concurrent writers | Safe | Can leave old value |
| Next read | Miss | Hit |
| Expensive values | Recompute on read | Recompute on write |
| Hot keys | Herd risk on miss | No miss |

Delete is the safe default. Update (with versioning) is worth it for hot keys where a miss would cause a stampede.

> [!tip] A layered recipe
> TTL on everything (with jitter) + delete after commit + leases or versioning for correctness + CDC for writes that bypass the app. Each layer catches the failures of the one above it.

## Key takeaways
- Cache and database share no transaction, so interleavings and partial failures create stale entries.
- Prefer **delete** over **update** on write: deletes commute, updates can land out of order.
- The cache-aside read/write race can resurrect old data after a delete; leases tied to invalidation, or version checks with retained metadata, can reject it.
- **Leases** reject stale sets and also throttle thundering herds.
- **CDC** can cover configured write paths through the commit log, provided capture scope, mappings, delivery and retention are correct.
- Always keep a TTL as the last line of defence.

## Further reading
- [Scaling Memcache at Facebook (NSDI 2013)](https://www.usenix.org/conference/nsdi13/technical-sessions/presentation/nishtala)
- [Scaling Memcache at Facebook — full paper PDF](https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf)
- [TwoHardThings — Martin Fowler](https://martinfowler.com/bliki/TwoHardThings.html)
- [Cache-aside pattern — Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside)
- [Client-side caching and invalidation — Redis docs](https://redis.io/docs/latest/develop/use/client-side-caching/)
