---
id: cache-negative-cache-and-penetration
title: Cache missing records without hiding new records
level: advanced
minutes: 2
summary: Use short-lived negative entries for repeated misses and invalidate them when a missing record is created.
sourceLesson: cache-failure-modes
---

A normal cache stores successful lookups. Repeated requests for absent records still reach the database unless the absence itself is represented in the cache.

## 3. Cache penetration

Requests for keys that **don't exist** in the database are never cached (there is nothing to cache), so every one goes straight to the database. This can be accidental (a bug requesting `user:undefined`) or an attack: someone requests `product:<random>` 50,000 times a second.

### Fix A: negative caching

Cache the absence:

This adapter-based Python fragment illustrates storing a miss marker; it requires a database, cache and marker definition and has no console output.

```python
user = db.find(uid)
if user is None:
    # Cache the absence for later readers.
    cache.set(f"user:{uid}", NULL_MARKER,
              ex=60)
```

Use a **short TTL**, because the item may be created soon. Negative caching works well for repeated misses on the same keys. It does not stop an attacker using fresh random keys every time, since each is a new miss, and it fills the cache with markers.

When the record is created, invalidate its negative entry as part of the write path. Otherwise readers can continue seeing the cached absence until that entry expires. A delayed negative fill can still race with creation and deletion; strict immediate visibility needs the same leases or retained version safeguards as positive values.

## Key takeaways
- Negative caching answers repeated lookups for the same absent key without returning to the database.
- Use a short TTL and invalidate a negative entry when creating that record so new users are not hidden.
- Fresh random keys defeat reuse of negative entries; validation, rate limits and set-membership filtering address different parts of penetration.

## Further reading
- [Cache-aside pattern — Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside)
- [Negative cache — Wikipedia](https://en.wikipedia.org/wiki/Negative_cache)
