---
id: cache-stampede-and-coalescing
title: Bound duplicate rebuilds when a hot key expires
level: advanced
minutes: 5
summary: Calculate a stampede and use bounded request coalescing with ownership-safe distributed locks.
sourceLesson: cache-failure-modes
---

A cache that works well becomes load-bearing. The database is sized for the miss rate, not the full traffic. So when the cache misbehaves, the failure is rarely gentle. The database's load scales with the miss ratio, so a change in hit ratio multiplies its load by:

```formula
x = (1 − h_new) / (1 − h_old)
x = (1 − 0) / (1 − 0.99) = 100
where
x: how many times the database's read load grows
h_old: the hit ratio before the failure, here 0.99 (99%)
h_new: the hit ratio after it, here 0 (an empty or unreachable cache)
In words: database load grows by the ratio of the new miss ratio to the old one.
```

So a 99% hit ratio dropping to 0% means **100× the database load**, instantly.

The following failure-mode units cover these five ways it goes wrong and what large systems do about each.

| Failure | Trigger |
|---|---|
| Stampede | One hot key expires |
| Hot key | One key gets huge traffic |
| Penetration | Requests for keys that don't exist |
| Avalanche | Many keys expire at once, or cache dies |
| Cold start | Empty cache after deploy/restart |

## 1. Cache stampede (thundering herd)

A popular key, say the homepage feed, gets 5,000 requests a second and takes 200 ms to rebuild. It expires.

```
 0 ms       key expires
 0-200 ms   every request misses
            and starts a rebuild
 200 ms     first rebuild finishes
```

How many requests pile in before the first rebuild finishes? Every request that arrives during the rebuild misses:

```formula
n = r × t_rebuild
n = 5,000 /s × 0.2 s = 1,000
where
n: the number of requests that miss and start their own rebuild
r: the request rate for the key, in requests per second (/s)
t_rebuild: the time one rebuild takes, in seconds (s); 200 ms = 0.2 s
s: seconds
ms: milliseconds; 1 ms = 0.001 s
In words: the number of duplicate rebuilds is the request rate multiplied by how long one rebuild takes.
```

About 1,000 requests all run the same expensive query at once. The database slows down, so each rebuild takes longer, so more requests pile up. This feedback loop is what turns a stampede into an outage.

### Fix A: request coalescing (single flight)

Make sure only **one** request rebuilds a given key; the rest wait for its result.

**In-process**, Go's `singleflight` or a per-key future/promise does this per server. With one coalescing group per server and no explicit forgetting, 50 servers allow at most 50 simultaneous rebuilds for the key; later calls can start new flights.

**Across servers**, use a short lock in the cache:

```python
import uuid, time

def get(key, tries=20):
    val = cache.get(key)
    if val is not None:
        return val
    token = str(uuid.uuid4())
    # Only one caller wins the lock
    if cache.set(f"lock:{key}", token,
                 nx=True, ex=10):
        try:
            val = rebuild(key)
            # Publish only while owner.
            publish_if_owner(
                key, val, token)
            return val
        finally:
            # delete only if still ours
            release(f"lock:{key}", token)
    if tries == 0:
        raise TimeoutError("rebuild busy")
    # Losers: wait briefly and retry,
    # or serve a stale copy if you kept one
    time.sleep(0.05)
    return get(key, tries - 1)
```

This is adapter-based pseudocode. publish_if_owner must atomically check the lock token and publish only while ownership is current; release must atomically compare-and-delete. A Redis Cluster implementation must colocate lock and data keys in one hash slot. The atomic lock-token comparison rejects publication after lease expiry on that Redis state. An asynchronously replicated lock can be lost during failover, allowing overlapping owners; this is duplicate-work mitigation, not a fault-tolerant mutual-exclusion proof. It also does not by itself order concurrent database invalidations. The lock TTL stops a crashed rebuilder holding it forever. This illustrative function returns its computed value to the caller even if its publication is rejected after lease expiry; a requirement for the latest value needs an additional version-aware read policy. Two details matter in practice:

- **Release only your own lock.** If a rebuild takes longer than 10 s, the lock expires and another caller may take it. A plain `DELETE` would then remove *their* lock. Store a random token and release with a small Lua script that deletes the key only if it still holds your token.
- **Bound the retries.** Waiters should give up after a limit and serve an acceptable stale value or fail with controlled load shedding; unbounded fallback rebuilds recreate the stampede, rather than spinning forever if the lock holder dies. Facebook's **leases** (the earlier invalidation units) are the same idea built into the cache.

## Key takeaways
- Duplicate rebuilds grow with request rate and rebuild time, creating a feedback loop under overload.
- Single-flight combines requests per process; an ownership-safe cache lock can coordinate across servers.
- Publish and release only under current ownership, bound waiting, and avoid falling back to unbounded concurrent rebuilds.

## Further reading
- [singleflight package — Go](https://pkg.go.dev/golang.org/x/sync/singleflight)
- [Distributed locks — Redis](https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/)
- [Thundering herd problem — Wikipedia](https://en.wikipedia.org/wiki/Thundering_herd_problem)
- [Scaling Memcache at Facebook — full paper PDF](https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf)
