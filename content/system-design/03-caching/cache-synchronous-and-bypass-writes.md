---
id: cache-synchronous-and-bypass-writes
title: Choose write-through or write-around
level: basic
minutes: 3
summary: Handle partial failures in synchronous cache writes and avoid filling a cache with write-only records.
sourceLesson: cache-strategies
---

A write policy decides which stores receive an update before it is acknowledged. It must also handle ordering, failures and the cached copy that was already present.

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

## Write-around

Writes go **straight to the database**, bypassing the cache. The cache is only filled on reads (usually by cache-aside), and any existing cached copy is invalidated.

This suits data that is written once and rarely read soon afterwards, such as logs, audit records, or uploads. It avoids filling the cache with data nobody asks for. The cost is that a read straight after a write is a miss.

Strictly, "update the DB then delete the key" in cache-aside is write-around plus invalidation, and that is the most common combination in practice.

## Comparing them

The table includes write-back, which the next unit covers in detail: it acknowledges a write once the cache has it and updates the database later.

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

## Key takeaways
- Write-through waits for required database and cache writes; concurrency and partial failures still need a policy.
- Write-around stores writes in the database, invalidates an existing copy and fills the cache on a later read.
- Avoid populating a cache with millions of writes that almost nobody reads; choose policies from the access pattern.

## Further reading
- [Cache-aside pattern — Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside)
- [Caching best practices — AWS](https://aws.amazon.com/caching/best-practices/)
- [System Design Primer — caching section](https://github.com/donnemartin/system-design-primer)
