---
id: cache-replication-and-gutter
title: Plan cache failover without assuming durable writes
level: advanced
minutes: 3
summary: Explain asynchronous replication loss and compare replica failover with Facebook’s spare gutter pool.
sourceLesson: cache-distributed
---

Replication can keep a cache available when a node fails. It does not remove stale-read and lost-write risks, so a cache failover plan still needs freshness and backend-load safeguards.

## Replication

Redis supports a **primary with one or more replicas**. Replication is **asynchronous**: the primary acknowledges a write to the client, then streams it to replicas.

```
 client --write--> Primary
        <--ack---    |
                     | async
                     v
                  Replica
```

Failover is handled by **Redis Sentinel** (for non-clustered setups) or by Redis Cluster itself: if a primary is unreachable for long enough, a replica is promoted.

Consequences of asynchronous replication:

- **Acknowledged writes can be lost.** If the primary dies after acking but before the replica receives the write, the promoted replica never had it.
- **Replica reads can be stale.** Reading from replicas spreads load but may return slightly old values.
- **Split brain**: during a network partition, a client still talking to the old primary may write data that is discarded when the partition heals. `min-replicas-to-write` with `min-replicas-max-lag` refuses writes when too few connected replicas meet the lag threshold; it still cannot prove receipt of each write.

WAIT returns the number of replicas that acknowledged this connection’s preceding writes before the requested count or timeout; check that returned count. Receipt is not necessarily disk persistence. Acknowledgements reduce loss risk but do not make Redis strongly consistent or eliminate acknowledged-write loss during failover.

For a pure cache, losing a new insertion causes a miss, but losing an update or invalidation can leave an old value on the promoted replica. Keep freshness safeguards even when cache entries are disposable. Replication's real value for caches is **availability**, avoiding the "cache gone, database flooded" scenario from lesson 1.

Memcached has no replication. Facebook handled failures with a small pool of spare servers called **gutter**, about 1% of the memcached servers in a cluster. When a client gets no response from a server, it retries against gutter; on a gutter miss it reads the database and stores the result in gutter, where entries expire quickly. Facebook chose this over rehashing a failed server's keys across the survivors, because a single key can account for a large share of one server's traffic (the paper cites up to 20%), and moving it could overload its new home and cascade.

The paper reports that gutter cut client-visible failures by 99% and converted 10–25% of failures into hits each day. When a server failed completely, gutter's hit rate typically passed 35% within four minutes.

## Key takeaways
- An asynchronous replica can miss an acknowledged write, and reads from it can be stale.
- WAIT acknowledgements reduce risk only when their returned count is checked; they do not guarantee disk persistence or strong consistency.
- Facebook’s short-lived gutter pool absorbed failed-server traffic without spreading a hot key into an overload cascade.

## Further reading
- [Redis replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/)
- [WAIT — Redis documentation](https://redis.io/docs/latest/commands/wait/)
- [Scaling Memcache at Facebook — full paper PDF](https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf)
