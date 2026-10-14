---
id: cache-aside-and-read-through
title: Choose who loads a cache miss
level: basic
minutes: 4
summary: Compare application-managed cache-aside with read-through loaders and per-process miss coalescing.
sourceLesson: cache-strategies
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
        # A hit skips both DB and refill.
        return deserialise(cached)
    # A miss reads the source of truth.
    user = db.query(
        "SELECT * FROM users WHERE id=%s",
        user_id)
    if user is not None:
        # Cache successful reads for 300 s.
        redis.set(key, serialise(user),
                  ex=300)
    return user
```

On a write, the application updates the database and then **deletes** the cache key, so the next read reloads it.

Why delete rather than overwrite with the new value? Deleting is idempotent and cheap, and it avoids two concurrent writers racing to `SET` their versions in the wrong order (the older value could land last and stick). The later invalidation units trace the races that remain.

**Strengths**

- Only data that is actually requested gets cached, so memory is not wasted.
- With timeouts, fallback and sufficient origin capacity, cache failure can fall back to the database; otherwise the miss surge can overload it.
- Works with any database and any cache.

**Weaknesses**

- The first read of each key is a miss, which costs three trips (cache, DB, cache).
- Cache logic is spread through application code.
- There is a window where the cache and database disagree, and some interleavings of concurrent reads and writes can leave stale data in the cache for a whole TTL (the later invalidation units).

## Read-through

The cache sits **in line**: the app only talks to the cache, and on a miss the cache itself loads from the database using a loader you configure.

```
 App --> Cache --miss--> DB
     <--       <--------
```

The data flow is the same as cache-aside; the difference is **where the code lives**. Examples include Caffeine's `LoadingCache` in Java, NCache, and DynamoDB Accelerator (DAX), which is a read-through and write-through cache in front of DynamoDB.

Read-through keeps application code simple, and a good library will **coalesce** concurrent misses for the same key into one database query. Note that an in-process library coalesces per process: with 20 app servers, a cold key can still cause up to 20 queries. The cost is coupling: the cache must know how to talk to your database.

## Key takeaways
- Cache-aside keeps the database loader in application code; read-through puts it in the cache or library.
- Load only requested keys and invalidate after database writes, while retaining a TTL and safe fallback capacity.
- A read-through library can combine concurrent misses inside one process; multiple servers can still issue multiple loads.

## Further reading
- [Cache-aside pattern — Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside)
- [Caching strategies — Amazon ElastiCache docs](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/Strategies.html)
