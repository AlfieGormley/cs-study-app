---
id: cache-change-log-and-own-writes
title: Invalidate from committed changes and preserve own writes
level: intermediate
minutes: 3
summary: Compare CDC-driven invalidation with targeted read-your-writes safeguards across clusters and regions.
sourceLesson: cache-invalidation
---

Writers outside the main application can bypass its invalidation code. A change-log pipeline broadens coverage, while users who just wrote may still need a faster, version-aware read path.

## Change data capture (CDC)

Instead of every writer remembering to invalidate, let the **database's commit log** drive invalidation.

```
 App --> DB --binlog/WAL--> CDC consumer
                              |
                              v
                          DEL keys
```

Facebook's version works slightly differently. SQL statements that modify data are amended to carry the memcache keys to invalidate. A daemon called `mcsqueal` on each database reads the committed statements from the commit log, extracts those deletes, and broadcasts them in batches to every frontend cluster in the region (via `mcrouter`). Because the keys travel with the transaction, lost or misrouted invalidations can simply be replayed from the log.

Today you might use Debezium reading the Postgres WAL or MySQL binlog, publishing to Kafka, with a consumer that maps changed rows to keys and deletes them.

**Benefits**: invalidation can cover committed changes from all configured logged tables regardless of client. Preserve relevant per-key order, include every dependent key and account for filters, publication scope, retention and failed delivery; a pipeline does not automatically provide global commit-order consumption. Consumers can retry failed deletes.

**Costs**: added latency that depends on capture, batching, processing and delivery, more infrastructure, and you must map rows to the cache keys that depend on them, which is hard for cached aggregates or joins.

## Read-your-writes

Users notice staleness most when it's *their own* change. Even if global staleness of a few seconds is fine, the person who just clicked "Save" expects to see it. Options:

- Version-aware write-through with ordering/failure safeguards, or carry the committed version and require reads to return at least that version.
- Invalidate synchronously in the writer's own cluster as well as through the slower CDC pipeline. Facebook's web servers did exactly this for read-after-write within a request's cluster.
- Remember "user 42 wrote at time t" and bypass the cache for that user; a fixed-duration window is a heuristic unless replica lag and stale fills are bounded. A required-version check is stronger.
- Facebook used **remote markers** across regions: before a write from a non-primary region, the client sets a marker that redirects subsequent misses to the primary until replication delivers its removal. The paper notes that concurrent updates can remove a marker too early and eviction can lose it, so this reduces stale-read probability rather than guaranteeing read-your-writes.

> [!tip] A layered recipe
> TTLs on disposable cached values (with TTL jitter) + delete after commit + invalidation-aware leases or retained version metadata + CDC for writes that bypass the app. These address different failure modes under their stated assumptions.

## Key takeaways
- CDC covers configured committed changes only when capture scope, key mapping, ordering, delivery and retention are correct.
- Capture and processing introduce lag; invalidate synchronously or require a committed version for a user’s immediate reread.
- Remote markers redirect misses to the primary while present; concurrent removal and eviction remain consistency risks.

## Further reading
- [Scaling Memcache at Facebook — full paper PDF](https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf)
- [PostgreSQL connector — Debezium](https://debezium.io/documentation/reference/stable/connectors/postgresql.html)
