---
id: cache-cold-start-warming
title: Bring a cold cache online within backend capacity
level: advanced
minutes: 4
summary: Calculate a safe traffic ramp and compare pre-warming, peer fills, persistence and shadow traffic.
sourceLesson: cache-failure-modes
---

An empty cache behaves like a failed cache until useful keys are filled. Treat a restart, new region or key-format migration as a backend-load event and choose the traffic share from measured misses.

## 5. Cold starts and warming

A new cache cluster, a restart without persistence, or a new region all start **empty**. With a database sized for a 1% miss rate, sending full production traffic to a cold cache is a self-inflicted avalanche.

Warming strategies:

1. **Gradual traffic shift**: route 1%, then 5%, 25%, 100% of traffic to the new cache over minutes, so it fills while the database copes.
2. **Pre-warm from data**: load the most-requested keys, say the top 100,000 (from access logs or the old cluster's `--hotkeys`) before taking traffic.
3. **Warm from a peer**: Facebook's **cold cluster warm-up** let a new cluster's clients read misses from a warm cluster's cache instead of the database, bringing cold clusters to full capacity in a few hours instead of a few days. To avoid copying a value that had just been invalidated, deletes in the cold cluster carried a two-second *hold-off* that made later `add`s fail; a failed `add` told the client to read the database instead. The paper records that an invalidation delayed beyond the two-second hold-off can still cause inconsistency; this timing safeguard was an operational trade-off, not a consistency guarantee.
4. **Persistence**: Redis RDB/AOF restores a node warm after restart.
5. **Shadow traffic**: mirror reads to the new cache before it serves users.

How big can each traffic step be? At each step, the new cache passes the database its share of the traffic multiplied by its current miss ratio; traffic not yet moved is still served as before. So send only as much traffic to a cold cache as the database can absorb in misses, and step up as the hit ratio climbs. For example, if spare database capacity is 2% of full traffic, sending 5% of traffic to a new cache that is hitting 60% of the time (missing 40%) uses that whole allowance. Include the old cluster’s misses, warming work and other queries when comparing total load with capacity. In practice, leave headroom rather than stepping exactly at capacity.

> [!warning] Deploys can flush caches
> Changing the cache key format (say, adding a field to the serialised object and bumping `v2` to `v3` in every key) makes every existing entry unreachable. That is a full flush on deploy. Roll it out gradually or run both versions side by side.

## Putting it together

```
 request
   |
 input validation / rate limit
   |
 Bloom filter (penetration)
   |
 local cache, 2s TTL (hot keys)
   |
 Redis (TTL + jitter, XFetch,
        stale-while-revalidate)
   |
 single-flight rebuild (stampede)
   |
 DB behind circuit breaker
```

Each layer defends against a different failure. You won't need all of them for every service, but you should know which one you are relying on.

## Key takeaways
- Ramp traffic as the hit ratio rises, accounting for both the new cluster’s misses and traffic still served elsewhere.
- Pre-warming, peer fills, saved state and mirrored reads can reduce cold-start load, with correctness safeguards for copied values.
- A key-prefix change makes old entries unreachable; stage the transition or serve both key versions.

## Further reading
- [Scaling Memcache at Facebook — full paper PDF](https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf)
- [Redis persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)
- [Cache warming — AWS](https://docs.aws.amazon.com/whitepapers/latest/database-caching-strategies-using-redis/cache-warming.html)
