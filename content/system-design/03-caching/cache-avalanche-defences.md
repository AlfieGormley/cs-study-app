---
id: cache-avalanche-defences
title: Spread mass expiry and protect the database
level: advanced
minutes: 3
summary: Use TTL jitter for synchronised misses and layer capacity limits when the whole cache tier fails.
sourceLesson: cache-failure-modes
---

An avalanche affects many keys at once. TTL jitter addresses synchronised expiry; a cache outage also needs enough remaining capacity, controlled misses or degraded responses.

## 4. Cache avalanche

An avalanche is a mass miss: many keys at once, rather than one hot key.

**Cause 1: synchronised expiry.** A job warms 1 million keys at 09:00 with `ex=3600`. At 10:00 they all expire together.

Fix: **TTL jitter**. Give each key its base TTL plus a random extra, chosen separately for every write, so keys written together expire at different times. A common choice is up to 10% of the base TTL.

This Python fragment requires `random` and `base_ttl` from its caller. It produces a random TTL and has no console output:

```python
# Sample each write independently.
jitter = random.randint(0, base_ttl // 10)
# The extra delay spreads batch expiry.
ttl = base_ttl + jitter
```

With a one-hour base TTL the TTL jitter is up to 360 s, so the expiries spread over six minutes. That turns one cliff into a slope: a million keys expiring over six minutes is a few thousand expiries a second instead of a million at once, and only keys that are read again cause a reload. Check that the remaining reload rate fits the database; TTL jitter spreads the work, it does not remove it.

**Cause 2: the cache tier fails.** A Redis cluster goes down, or a network partition cuts it off. All traffic falls to the database.

Fixes:

- **High availability**: replicas and automatic failover, spread across availability zones.
- **Circuit breakers and load shedding**: when the database is struggling, fail fast or serve degraded responses rather than queueing every request.
- **Rate-limit misses**: cap concurrent database rebuilds per key or per service.
- **Multi-level caching**: an in-process cache can carry the hottest keys for a while.
- **A gutter pool** (the earlier replication and gutter unit): Facebook sent traffic for failed memcached servers to a small pool of spare servers with short TTLs, so a few failed nodes did not become a database flood.

## Key takeaways
- Random TTL jitter spreads a batch’s expiry times; only keys requested again cause reloads.
- Replica availability, local caches and spare cache pools can absorb part of a tier failure.
- Compute residual database traffic and shed or cap misses when it exceeds sustainable capacity.

## Further reading
- [Using load shedding to avoid overload — AWS Builders’ Library](https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/)
- [Scaling Memcache at Facebook — full paper PDF](https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf)
- [Key eviction — Redis docs](https://redis.io/docs/latest/develop/reference/eviction/)
