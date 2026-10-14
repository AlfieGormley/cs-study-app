---
id: dist-redlock-timing
title: Redlock validity and the fencing debate
level: advanced
minutes: 4
summary: Calculate Redlock’s remaining validity and assess its timing assumptions for correctness-sensitive work.
sourceLesson: dist-leases-locks
---

Redlock extends an expiring Redis lock across independent servers. Its validity calculation is useful to understand, but the preceding distinction between ownership tokens and fencing tokens remains central.

## Redlock and why it's controversial

Redlock is an algorithm proposed by Salvatore Sanfilippo (antirez), Redis's creator, for a lock that survives a Redis node failing. It uses N independent Redis masters (typically 5), with no replication between them:

1. Read the current time (call it T1).
2. Try `SET resource token NX PX ttl` on all 5 instances, with a short per-node timeout. Here ttl is the lock's time to live: how long each instance keeps the key before deleting it.
3. Read the time again (T2). The lock is held only if a majority of instances (at least 3 of 5) succeeded **and** acquiring took less than the ttl.
4. The client may use the lock only for the remaining validity time, worked out below.
5. On failure, release on all instances.

```formula
T_acq = T_2 − T_1
n_ok ≥ ⌊N / 2⌋ + 1
T_acq < ttl
V = ttl − T_acq − D
V = 10 s − 0.2 s − 0.1 s = 9.7 s
where
T_1: the client's clock reading before it starts acquiring
T_2: the client's clock reading after the last instance has answered
T_acq: how long acquisition took, in seconds (s)
n_ok: how many instances accepted the lock
N: the number of independent Redis instances; typically 5
⌊ ⌋: floor: round down to a whole number, so a majority of 5 is 3
ttl: the key's time to live on each instance; here 10 s
D: an allowance for clock drift between the instances; here 0.1 s
V: the validity time, how long the client may treat the lock as held
s: second
In words: the lock counts only if a majority agreed and the acquisition didn't eat the whole ttl, and what's left of the ttl, minus a drift allowance, is how long the client may use it.
```

The safety of this calculation rests on clocks: if an instance's clock runs fast or jumps, its copy of the key expires earlier than V assumes. That is the heart of the critique below.

### Kleppmann's critique (2016)

1. **No fencing tokens.** Redlock returns a random value, not a monotonically increasing number, so a resource can't tell an old holder from a new one. Process pauses still cause two holders, as in the diagram above.
2. **It depends on timing assumptions.** Safety relies on bounded network delay, bounded pauses and clocks that don't jump. If a Redis node's clock jumps forward (NTP step, admin change), its key expires early:

```
C1 locks A, B, C   (3 of 5)
C's clock jumps forward
  -> C expires C1's key
C2 locks C, D, E   (3 of 5)
Both C1 and C2 think they hold it
```

A node crashing and restarting without persisted keys (or with `fsync` every second) has the same effect.

His conclusion: Redlock is too heavy for efficiency locks (one Redis is fine) and not safe enough for correctness locks (use ZooKeeper or etcd with fencing).

### Antirez's response

Antirez argued that:

- the random token can be used for compare-and-set at the resource in some cases;
- Redlock's step 3 detects long delays *during acquisition*;
- clock jumps can be avoided operationally by slewing rather than stepping, so the timing assumptions are reasonable;
- every lock with auto-release has the GC pause problem, including ZooKeeper's.

The last point is true, and it's exactly why fencing tokens are the real answer: they make safety independent of timing. Redlock's problem is that it doesn't produce one.

> [!tip] Practical guidance
> For efficiency only, a single Redis `SET NX PX` is fine. For correctness, use etcd, ZooKeeper or Consul, *plus* fencing tokens at the resource, *plus* idempotency where the resource can't check tokens. Or partition work by key, as Kafka consumer groups do, and enforce sequencing or fencing at external storage so a stale consumer cannot reorder writes during a rebalance.

## Key takeaways
- Redlock requires a majority of independent Redis instances and subtracts acquisition time and drift allowance from the TTL.
- Clock jumps, restarts and pauses can undermine the timing assumptions; a random ownership token does not order grants.
- The debate distinguishes acquisition checks from resource fencing: stale work must be rejected where it acts.

## Further reading
- [How to do distributed locking (Martin Kleppmann)](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html)
- [Is Redlock safe? (antirez's reply)](http://antirez.com/news/101)
- [Distributed locks with Redis (Redis docs)](https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/)
