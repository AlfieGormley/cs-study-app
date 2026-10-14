---
id: arch-search-cdc-versioned-rebuilds
title: Keeping derived search indexes repairable
level: intermediate
minutes: 3
summary: Use reliable change capture, version barriers and coordinated rebuilds instead of independent dual writes.
sourceLesson: arch-search-systems
---

The previous unit described a search cluster. Its documents are derived copies, so its reliability also depends on a recoverable path from committed database state.

## Keeping search in sync with the source of truth

The search index is a **derived copy**, not the source of truth. Your database is. The hard part of search architecture is keeping the copy current.

### Option 1: Dual writes (avoid)

```
 app -> write DB
 app -> write Elasticsearch
```

If the second write fails, or two concurrent updates reach ES in the opposite order to the DB, the index silently diverges. There's no transaction across both.

### Option 2: Change data capture (CDC) via a log

```
 [DB] --WAL/binlog--> [Debezium]
                          |
                       [Kafka]
                          |
                   [indexer workers]
                          |
                   [Elasticsearch]
```

- CDC can capture committed changes in source order, provided the snapshot/log handoff is correct and required logs are retained. Monitor connector errors, replication slots and retention; parallel consumers must preserve per-key order or reject stale versions.
- Kafka buffers changes within configured durability and retention limits; monitor lag before records expire.
- Make indexing idempotent and version-aware: map each complete row snapshot to a strictly increasing supported integer version and use `version_type=external`. Equal as well as older versions are rejected; handle a known duplicate conflict deliberately. Deletes need durable tombstones or another replay strategy because delete-version retention expires. A raw PostgreSQL LSN string is not directly a supported integer version.

An alternative is the **transactional outbox**: write an event row in the same DB transaction, and a relay publishes it.

### Option 3: Periodic reindex

For smaller datasets or as a safety net, rebuild the index from the database periodically. A common pattern is to **build a new index in the background and atomically switch an alias** (`products` → `products_v2`), supporting a cutover without intentionally stopping reads. Coordinate snapshot/live-change ordering, catch up before switching, and keep the old index current if rollback is required.

> [!tip] Plan for full rebuilds from day one
> You'll change analysers, mappings and ranking many times. Changing index-time analysis requires reindexing existing documents. Some search-time analyser or synonym changes can be applied without rebuilding the stored index. Design so you can always rebuild the index from the source of truth (CDC from a snapshot, or a bulk export) and cut over with an alias.

## Key takeaways
- The database remains authoritative; independent database and search writes can diverge or arrive out of order.
- CDC or an outbox needs retained logs, monitored progress and ordering or supported external versions.
- Durable delete barriers prevent old replayed updates from resurrecting removed documents.
- Build and catch up a replacement index before alias cutover, and keep rollback data current.

## Further reading
- [Debezium architecture](https://debezium.io/documentation/reference/stable/architecture.html)
