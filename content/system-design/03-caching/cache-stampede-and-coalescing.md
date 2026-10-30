---
id: cache-stampede-and-coalescing
title: Bound duplicate rebuilds when a hot key expires
level: advanced
minutes: 5
summary: Calculate a stampede and use bounded request coalescing with ownership-safe distributed locks.
sourceLesson: cache-failure-modes
---

A cache that works well becomes load-bearing. The database is sized for the miss rate, not the full traffic. So when the cache misbehaves, the failure is rarely gentle: database load follows the miss ratio, so a 99% hit ratio falling to 0% means about **100× the database load**, instantly.

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

Every request that arrives before the first rebuild finishes also misses and starts its own rebuild:

```formula essential
n ≈ r × t_rebuild
where
n: the number of requests that miss and start their own rebuild, assuming requests arrive at a steady rate and none are coalesced
r: the request rate for the key, in requests per second (/s)
t_rebuild: the time one rebuild takes, in seconds (s)
s: seconds
≈: approximately equal to
In words: duplicate rebuilds grow with both the key's popularity and how slow it is to rebuild. At 5,000 requests a second and a 200 ms rebuild, about 1,000 identical queries start at once.
```

The relationship explains the feedback loop that turns a stampede into an outage. A thousand identical expensive queries slow the database, so each rebuild takes longer, so the window grows and even more requests pile in.

> [!analogy] Real-world analogy: one person fetches the takeaway
> An office orders lunch from one shop. If the delivery is late and nobody coordinates, everyone drives to the shop separately and the queue there makes every order slower. Sensible offices send one person while everyone else waits at their desks.
>
> **How it maps:** The shop is the database, the late delivery is the expired key, and each person driving over is a request starting its own rebuild. Sending one person is request coalescing; the rest waiting is the other requests waiting for that one result.
>
> **Where it stops:** Colleagues can see who has gone. Servers coordinate through a lock or lease that can expire while its holder is still working, so the rules for who may publish the result matter (below).

### Fix A: request coalescing (single flight)

Make sure only **one** request rebuilds a given key; the rest wait for its result.

**In-process**, Go's `singleflight` or a per-key future/promise does this per server. With one coalescing group per server, 50 servers allow at most 50 simultaneous rebuilds for the key; later calls can start new flights.

**Across servers**, use a short lock in the cache. The sketch below assumes a small adapter: `cache.set(..., nx=True, ex=10)` maps to Redis `SET key value NX EX 10`, and `publish_if_owner` and `release` are short Lua scripts that act only if the lock still holds this caller's token.

```python
import uuid, time

def get(key, tries=20):
    for _ in range(tries):
        val = cache.get(key)
        if val is not None:
            return val
        token = str(uuid.uuid4())
        # Only one caller wins the lock.
        if cache.set(f"lock:{key}", token,
                     nx=True, ex=10):
            try:
                val = rebuild(key)
                # Publish only while owner.
                publish_if_owner(
                    key, val, token)
                return val
            finally:
                # Delete only our own lock.
                release(f"lock:{key}",
                        token)
        # Losers wait briefly, then retry
        # (or serve a stale copy if kept).
        time.sleep(0.05)
    raise TimeoutError("rebuild busy")
```

Three details matter in practice:

- **Release only your own lock.** If a rebuild takes longer than the lock's 10 s TTL, the lock expires and another caller may take it. A plain `DEL` would then remove *their* lock. Store a random token and delete only if it still matches, atomically.
- **Publish only while you own the lock.** A rebuilder that paused past the lock's expiry may hold an older result than the new owner. Checking the token at publish time stops that late write landing. (In Redis Cluster, keep the lock key and the cached value's key in one hash slot so one script can check both.)
- **Bound the waiting.** Followers should give up after a limit and serve an acceptable stale value or fail with controlled load shedding. Falling back to their own rebuilds would recreate the stampede.

This cuts duplicate work; it is not a fault-tolerant mutual-exclusion guarantee: an asynchronously replicated lock can be lost in a failover, briefly allowing two owners. Facebook's **leases** (the earlier invalidation units) are the same idea built into the cache.

## Key takeaways
- Duplicate rebuilds grow with request rate and rebuild time, and a slowing database lengthens the window: a feedback loop.
- Single-flight combines requests per process; an ownership-safe cache lock can coordinate across servers.
- Publish and release only under current ownership, bound waiting, and avoid falling back to unbounded concurrent rebuilds.

## Further reading
- [singleflight package — Go](https://pkg.go.dev/golang.org/x/sync/singleflight)
- [Distributed locks — Redis](https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/)
- [Thundering herd problem — Wikipedia](https://en.wikipedia.org/wiki/Thundering_herd_problem)
- [Scaling Memcache at Facebook — full paper PDF](https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf)
