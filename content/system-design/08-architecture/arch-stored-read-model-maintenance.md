---
id: arch-stored-read-model-maintenance
title: Maintaining stored read models
level: intermediate
minutes: 4
summary: Compare denormalised fields, materialised views and event-fed projections by their maintenance and freshness costs.
sourceLesson: arch-scaling-reads
---

Caches store answers temporarily. A read model deliberately stores a query-shaped representation whose update rules are part of the data design.

## Denormalisation

A normalised schema stores each fact once and **joins at read time**. That's great for correctness, but a hot page that joins five tables does five tables' worth of work on every view.

Denormalisation **duplicates data so reads don't need joins**:

```
Normalised:
 posts(id, author_id, body)
 users(id, name, avatar)
 -> JOIN on every feed view

Denormalised:
 posts(id, author_id, author_name,
       author_avatar, body, like_count)
```

- Reads become a single lookup.
- Writes get more expensive: if a user renames themselves, every copy must be updated, either synchronously or by a background job that consumes `UserRenamed` events.
- Asynchronously maintained copies can be stale for an unbounded period during failure. Transactionally maintained copies can preserve consistency at additional write cost.

Counters are a classic case. `SELECT COUNT(*) FROM likes WHERE post_id = ?` on a post with 2 million likes is slow; a correctly maintained like_count avoids recounting rows, though lookup and write contention still have costs.

NoSQL stores like DynamoDB and Cassandra push you towards this: you model access patterns rather than rely on server-side relational joins. Cassandra often uses query-specific tables; DynamoDB supports both single-table and multiple-table designs, so one table per access pattern is not a universal rule.

## Materialised views

A **materialised view** is a stored, precomputed query result. Unlike a regular view (which is just a saved query run each time), the result is physically stored and must be refreshed.

- **Postgres** `CREATE MATERIALIZED VIEW` and `REFRESH MATERIALIZED VIEW`: refreshes are manual or scheduled and recompute the whole query. A plain refresh locks out readers while it runs; `REFRESH ... CONCURRENTLY` lets reads continue but requires an already populated view and a qualifying unique index covering all rows with plain column keys. It is not invariably slower; relative cost depends on how many rows change.
- Some systems maintain views **incrementally** as source data changes (Oracle fast refresh, ClickHouse incremental materialised views triggered by source inserts rather than arbitrary later source mutations, streaming systems like the Materialize streaming database).
- In microservices the same idea appears as a **read model**: a service consumes events from others and builds a local, query-shaped copy. This is the read side of **CQRS** (Command Query Responsibility Segregation), which separates command and query responsibilities. CQRS can use one database and does not require a normalized write model or denormalized read model.

```
 [Orders]--OrderPlaced--+
 [Users]--UserUpdated---+--> [projector]
 [Ship]--Shipped--------+        |
                                 v
                    order_history_view
                    (one row per order,
                     ready to render)
```

### Preserve the projection's meaning

An older `OrderPlaced` event must not overwrite a later `OrderShipped` status. Define per-entity causal or version rules through the pipeline: identical keys in independent topics do not create a cross-service total order. Complete snapshots can reject older versions; partial events or deltas need gap handling or separate source progress so required changes are not discarded. Write the projection before acknowledging, make duplicate handling idempotent and retain a replay or snapshot repair path. For a one-hour freshness requirement, budget source lag, refresh duration and any downstream cache age together.

## Key takeaways
- Denormalisation avoids read-time joins by maintaining extra copies on the write path or asynchronously.
- Materialised views store query results; refresh and concurrent-read behaviour depend on the engine.
- CQRS separates command and query responsibilities without necessarily requiring separate databases.
- Event-fed read models require defined ordering, durable processing and rebuild paths; a cache cannot repair an older event overwriting newer state.

## Further reading
- [Azure Architecture Center: Materialized View pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/materialized-view)
- [Azure Architecture Center: CQRS pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs)
- [Wikipedia: Denormalization](https://en.wikipedia.org/wiki/Denormalization)
