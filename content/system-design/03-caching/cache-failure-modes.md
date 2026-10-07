---
id: cache-failure-modes
title: Cache failure modes
level: advanced
minutes: 15
summary: Stampedes, hot keys, penetration, avalanches and cold starts — how caches take systems down, and the coalescing, early-expiry, Bloom-filter and warming techniques that stop them.
---

A cache that works well becomes load-bearing. The database is sized for the miss rate, not the full traffic. So when the cache misbehaves, the failure is rarely gentle: a 99% hit ratio dropping to 0% means **100× the database load**, instantly.

This lesson covers the five classic ways it goes wrong and what large systems do about each.

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
 t=0     key expires
 t=0-200ms  5000/s * 0.2s = 1000
            requests miss, all rebuild
 t=200ms first rebuild finishes
```

About 1,000 requests all run the same expensive query at once. The database slows down, so each rebuild takes longer, so more requests pile up. This feedback loop is what turns a stampede into an outage.

### Fix A: request coalescing (single flight)

Make sure only **one** request rebuilds a given key; the rest wait for its result.

**In-process**, Go's `singleflight` or a per-key future/promise does this per server. With 50 servers, you get at most 50 rebuilds instead of 1,000.

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

This is adapter-based pseudocode. publish_if_owner must atomically check the lock token and publish only while ownership is current; release must atomically compare-and-delete. A Redis Cluster implementation must colocate lock and data keys in one hash slot. This handles lease expiry but does not by itself order concurrent database invalidations. The lock TTL stops a crashed rebuilder holding it forever. Two details matter in practice:

- **Release only your own lock.** If a rebuild takes longer than 10 s, the lock expires and another caller may take it. A plain `DELETE` would then remove *their* lock. Store a random token and release with a small Lua script that deletes the key only if it still holds your token.
- **Bound the retries.** Waiters should give up after a limit and serve an acceptable stale value or fail with controlled load shedding; unbounded fallback rebuilds recreate the stampede, rather than spinning forever if the lock holder dies. Facebook's **leases** (lesson 4) are the same idea built into the cache.

### Fix B: serve stale while refreshing

Store the value with a **soft** expiry inside it and a longer **hard** TTL on the key. After the soft expiry, one request refreshes in the background while everyone else keeps getting the slightly stale value. This is `stale-while-revalidate` applied to your application cache, so readers with a retained eligible stale value can avoid waiting; after hard expiry, eviction or loss they still miss.

### Fix C: probabilistic early expiration (XFetch)

Instead of everyone noticing expiry at the same instant, each request independently decides to refresh **a little early**, with a probability that rises as expiry approaches. From Vattani, Chierichetti and Lowenstein (VLDB 2015):

```python
import math, random, time

def should_refresh(expiry, delta, beta=1.0):
    # delta: how long a rebuild takes (s)
    # -log(rand) is exponential, mean 1
    early = delta * beta * -math.log(
        1.0 - random.random())
    return time.time() + early >= expiry
```

With 5,000 requests a second, one of them almost certainly refreshes shortly before expiry, making expiry less likely under load; refresh failure or unlucky sampling can still let it expire. Rarely-read keys almost never refresh early, so you don't waste work on them. `beta > 1` refreshes earlier; `beta < 1` later. No locks or coordination needed.

## 2. Hot keys

Sometimes a single key gets an enormous share of traffic: a celebrity's profile, a flash-sale product, a live match score. Partitioning doesn't help, because one key lives on **one** node. If that node handles 100k ops/s and the key gets 300k ops/s, it saturates regardless of cluster size.

Fixes:

- **Local (in-process) cache** in front of Redis with a 1–5 s TTL. With 100 app servers, with per-server coalescing and no early eviction, Redis sees roughly 100 fills per TTL period for that key, rather than 300,000 a second.
- **Key replication / splitting**: store copies as `score:match9#0` to `score:match9#9` and have readers pick a random suffix. Load spreads over up to 10 nodes; writers update all copies.
- **Read replicas** for the shard holding the hot key.
- **Detect them**: Redis has `redis-cli --hotkeys` (with LFU policy) and per-key monitoring in managed services. You can't fix what you can't see.

> [!example] Hot keys at Twitter-scale
> A celebrity with 100 million followers tweets. Every timeline render that includes the tweet reads the same tweet object. Systems like this keep hot objects in process-local caches on every front-end server, precisely because one cache shard cannot serve that traffic.

## 3. Cache penetration

Requests for keys that **don't exist** in the database are never cached (there is nothing to cache), so every one goes straight to the database. This can be accidental (a bug requesting `user:undefined`) or an attack: someone requests `product:<random>` 50,000 times a second.

### Fix A: negative caching

Cache the absence:

```python
user = db.find(uid)
if user is None:
    cache.set(f"user:{uid}", NULL_MARKER,
              ex=60)
```

Use a **short TTL**, because the item may be created soon. Negative caching works well for repeated misses on the same keys. It does not stop an attacker using fresh random keys every time, since each is a new miss, and it fills the cache with markers.

### Fix B: Bloom filter

A **Bloom filter** is a compact bit array that answers "is this key possibly in the set?" with **no false negatives** and a tunable false-positive rate. Put every valid id into it; check it before touching the cache or database.

```
 request id
     |
 Bloom: "definitely not"? --> 404
     | "maybe"
 cache --> DB
```

Sizing: about **9.6 bits per element** for a 1% false-positive rate. 100 million ids ≈ 120 MB. A random invalid id is rejected 99% of the time without any database work.

Caveats: standard Bloom filters can't delete entries (use a counting filter or Cuckoo filter, or rebuild periodically), and new ids must be included before they become visible, or a negative result must fall back to the source while coverage is uncertain. A stale filter can otherwise reject a valid new id.

Also: **validate input** (reject malformed ids at the edge) and **rate-limit** clients that generate many misses.

## 4. Cache avalanche

An avalanche is a mass miss: many keys at once, rather than one hot key.

**Cause 1: synchronised expiry.** A job warms 1 million keys at 09:00 with `ex=3600`. At 10:00 they all expire together.

Fix: **TTL jitter**.

```python
jitter = random.randint(0, base_ttl // 10)
ttl = base_ttl + jitter
```

A 10% spread over an hour turns one cliff into a gentle slope over six minutes.

**Cause 2: the cache tier fails.** A Redis cluster goes down, or a network partition cuts it off. All traffic falls to the database.

Fixes:

- **High availability**: replicas and automatic failover, spread across availability zones.
- **Circuit breakers and load shedding**: when the database is struggling, fail fast or serve degraded responses rather than queueing every request.
- **Rate-limit misses**: cap concurrent database rebuilds per key or per service.
- **Multi-level caching**: an in-process cache can carry the hottest keys for a while.
- **A gutter pool** (lesson 6): Facebook sent traffic for failed memcached servers to a small pool of spare servers with short TTLs, so a few failed nodes did not become a database flood.

## 5. Cold starts and warming

A new cache cluster, a restart without persistence, or a new region all start **empty**. With a database sized for a 1% miss rate, sending full production traffic to a cold cache is a self-inflicted avalanche.

Warming strategies:

1. **Gradual traffic shift**: route 1%, then 5%, 25%, 100% of traffic to the new cache over minutes, so it fills while the database copes.
2. **Pre-warm from data**: load the top N keys (from access logs or the old cluster's `--hotkeys`) before taking traffic.
3. **Warm from a peer**: Facebook's **cold cluster warm-up** let a new cluster's clients read misses from a warm cluster's cache instead of the database, bringing cold clusters to full capacity in a few hours instead of a few days. To avoid copying a value that had just been invalidated, deletes in the cold cluster carried a two-second *hold-off* that made later `add`s fail; a failed `add` told the client to read the database instead.
4. **Persistence**: Redis RDB/AOF restores a node warm after restart.
5. **Shadow traffic**: mirror reads to the new cache before it serves users.

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
- A stampede happens when one hot key expires; fix it with request coalescing, serve-stale-while-refreshing or probabilistic early expiration.
- Hot keys overload one shard regardless of cluster size; use local caches or split the key across copies.
- Penetration is misses for non-existent keys; use negative caching, Bloom filters, validation and rate limits.
- Avalanches are mass misses; add TTL jitter, HA replicas, circuit breakers and load shedding.
- Never point full traffic at a cold cache; warm it gradually, from data or from a peer.

## Further reading
- [Optimal Probabilistic Cache Stampede Prevention (VLDB 2015)](https://cseweb.ucsd.edu/~avattani/papers/cache_stampede.pdf)
- [Cache stampede — Wikipedia](https://en.wikipedia.org/wiki/Cache_stampede)
- [Bloom filter — Wikipedia](https://en.wikipedia.org/wiki/Bloom_filter)
- [Thundering herd problem — Wikipedia](https://en.wikipedia.org/wiki/Thundering_herd_problem)
- [singleflight package — Go](https://pkg.go.dev/golang.org/x/sync/singleflight)
- [Scaling Memcache at Facebook — full paper PDF](https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf)
