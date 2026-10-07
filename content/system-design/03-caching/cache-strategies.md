---
id: cache-strategies
title: Caching strategies
level: basic
minutes: 11
summary: Cache-aside, read-through, write-through, write-back and write-around — how data flows between app, cache and database, and what each costs.
---

Once you have decided to cache, you have to decide **who loads the cache, and what happens on a write**. These choices are called caching strategies (or patterns). They differ in who is responsible for the cache, how fresh the data is, and what can be lost when something crashes.

Read strategies decide how data gets *into* the cache. Write strategies decide what happens when data *changes*. Real systems combine one of each.

## Cache-aside (lazy loading)

This is the most common pattern, and the default for Redis and Memcached. The application talks to both the cache and the database. The cache knows nothing about the database.

```
 read(key):
   1. GET key from cache ---- hit --> return
   2. miss: SELECT from DB
   3. SET key in cache (with TTL)
   4. return value
```

The following uses application-specific database and serialization adapters; it illustrates control flow rather than a complete library integration.

```python
def get_user(user_id):
    key = f"user:{user_id}"
    cached = redis.get(key)
    if cached is not None:
        return deserialise(cached)
    user = db.query(
        "SELECT * FROM users WHERE id=%s",
        user_id)
    if user is not None:
        redis.set(key, serialise(user),
                  ex=300)
    return user
```

On a write, the application updates the database and then **deletes** the cache key, so the next read reloads it.

Why delete rather than overwrite with the new value? Deleting is idempotent and cheap, and it avoids two concurrent writers racing to `SET` their versions in the wrong order (the older value could land last and stick). Lesson 4 looks at the races that remain.

**Strengths**

- Only data that is actually requested gets cached, so memory is not wasted.
- With timeouts, fallback and sufficient origin capacity, cache failure can fall back to the database; otherwise the miss surge can overload it.
- Works with any database and any cache.

**Weaknesses**

- The first read of each key is a miss, which costs three trips (cache, DB, cache).
- Cache logic is spread through application code.
- There is a window where the cache and database disagree, and some interleavings of concurrent reads and writes can leave stale data in the cache for a whole TTL (lesson 4).

## Read-through

The cache sits **in line**: the app only talks to the cache, and on a miss the cache itself loads from the database using a loader you configure.

```
 App --> Cache --miss--> DB
     <--       <--------
```

The data flow is the same as cache-aside; the difference is **where the code lives**. Examples include Caffeine's `LoadingCache` in Java, NCache, and DynamoDB Accelerator (DAX), which is a read-through and write-through cache in front of DynamoDB.

Read-through keeps application code simple, and a good library will **coalesce** concurrent misses for the same key into one database query. Note that an in-process library coalesces per process: with 20 app servers, a cold key can still cause up to 20 queries. The cost is coupling: the cache must know how to talk to your database.

## Write-through

On every write, the data is written to the cache **and** to the database synchronously, before the write is acknowledged.

```
 write(key, v):
   App --> Cache --> DB
   ack only after both succeed
```

**Strengths**

- Acknowledging both writes can make read-after-write fresh when ordering and failure handling are correct. Two independent writes alone do not prevent concurrent writers leaving a stale cache value.
- Nothing is lost if the cache crashes, because the database already has it.

**Weaknesses**

- The acknowledgement waits for the required writes; total latency depends on their ordering and possible overlap.
- Data that is written but never read still fills the cache (often fixed by pairing with a TTL).
- If the DB write succeeds and the cache write fails (or the reverse), you need a rule for which one wins. In practice, write to the DB first and treat the cache as best-effort.

## Write-back (write-behind)

Writes go to the cache only, and are acknowledged immediately. The cache flushes them to the database **later**, asynchronously, often in batches.

```
 write --> Cache (ack)
             |  later, batched
             v
             DB
```

This is how CPU caches, the operating system page cache, and database buffer pools work: a "dirty" page is written to disk later.

**Strengths**

- Very low write latency.
- Absorbs bursts and **coalesces** repeated writes. A counter incremented 1,000 times a second can be flushed once a second as a single write.

**Weaknesses**

- **Data loss.** If the cache node dies before flushing, the acknowledged writes are gone, unless the cache itself is durable (replicated, with a write-ahead log).
- The database is behind the cache, so anything reading the database directly (reports, other services) sees old data.
- Ordering and failure handling of the flush are hard to get right.

> [!warning] Write-back changes your source of truth
> With write-back, the cache temporarily *is* the source of truth for recent writes. You need the durability guarantees of a database from it. Use it only where its measured loss window (including delayed or failed flushes) is tolerable (view counters, analytics) or where the cache is genuinely durable.

## Write-around

Writes go **straight to the database**, bypassing the cache. The cache is only filled on reads (usually by cache-aside), and any existing cached copy is invalidated.

This suits data that is written once and rarely read soon afterwards, such as logs, audit records, or uploads. It avoids filling the cache with data nobody asks for. The cost is that a read straight after a write is a miss.

Strictly, "update the DB then delete the key" in cache-aside is write-around plus invalidation, and that is the most common combination in practice.

## Refresh-ahead

A fifth pattern tackles the miss that happens when a popular key expires. With **refresh-ahead**, the cache reloads an entry *before* it expires, once it has been read close to the end of its life. For example, with a 60 s TTL and a refresh factor of 0.8, a read after 48 s returns the current value immediately and triggers a background reload.

- Successful timely refreshes hide expiry for hot keys; slow or failed refreshes can still lead to a miss.
- Keys nobody reads near expiry are left to expire, so cold data is not refreshed for nothing.
- If the predictions are poor, you pay for reloads that nobody uses.

Caffeine's `refreshAfterWrite` is an example. Lesson 7 shows a probabilistic version that also prevents stampedes.

## Comparing them

| Strategy | Write latency | Fresh after write | Risk |
|---|---|---|---|
| Write-through | High (2 writes) | With ordering | Concurrent writes / failures |
| Write-back | Very low | Cache yes, DB no | Data loss on crash |
| Write-around | DB only | Miss on next read | Read-after-write miss |

| Read strategy | Code lives in | Notes |
|---|---|---|
| Cache-aside | Application | Simple, resilient, most common |
| Read-through | Cache / library | Cleaner code, can coalesce misses |

## Choosing in practice

1. **Default to cache-aside with delete-on-write and a TTL.** It is a practical default when staleness is acceptable. TTL bounds entry residence rather than source-data age; failures still require safe fallback, origin capacity and reliable refill.
2. Use **read-through** when a library gives it to you cheaply (Caffeine, DAX) and you want built-in miss coalescing.
3. Add **write-through** when reads straight after writes are common and must hit, such as a user editing then viewing their profile.
4. Use **write-back** only for high-volume, loss-tolerant writes, or when the cache layer is designed to be durable.
5. Use **write-around** for write-heavy, read-rarely data.

> [!example] A social feed counter
> Likes on a viral post may arrive at 20,000 per second. A single PostgreSQL row may become a contention bottleneck; benchmark the actual transaction path. Instead, `INCR post:123:likes` in Redis (write-back) and flush the total to Postgres every few seconds. Whether any lost likes are acceptable is a product decision. Restore the baseline from durable state after cache loss and handle flush ordering/idempotency; blindly persisting a reset or old total can lose previously saved counts.

## Key takeaways
- Read strategies: **cache-aside** (app loads on miss) and **read-through** (cache loads on miss).
- Write strategies: **write-through** (cache and DB synchronously), **write-back** (cache now, DB later), **write-around** (DB only).
- Cache-aside with delete-on-write and a TTL is the robust default.
- Write-back gives the lowest latency and coalesces writes, but risks losing acknowledged data.
- Write-through can improve read-after-write freshness when ordering, invalidation and partial failures are handled; it also maintains entries that may never be read.
- Refresh-ahead aims to reload hot keys before expiry, reducing waits when refreshes finish in time.

## Further reading
- [Caching strategies — Amazon ElastiCache docs](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/Strategies.html)
- [Cache-aside pattern — Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside)
- [Caching best practices — AWS](https://aws.amazon.com/caching/best-practices/)
- [Cache (computing): writing policies — Wikipedia](https://en.wikipedia.org/wiki/Cache_(computing))
- [System Design Primer — caching section](https://github.com/donnemartin/system-design-primer)
