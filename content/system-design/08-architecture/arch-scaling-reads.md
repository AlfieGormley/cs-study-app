---
id: arch-scaling-reads
title: Scaling reads
level: intermediate
minutes: 13
summary: The toolbox for read-heavy systems, from read replicas and cache layers to denormalisation, materialised views and precomputed results, and the consistency costs of each.
---

Many read-heavy applications, such as feeds and catalogues, benefit from serving copies of data; measure the actual read/write mix instead of assuming a universal ratio. That's good news, because reads are easier to scale than writes: you can **copy data** and serve it from many places.

Every technique in this lesson is a form of the same trade:

> [!note] The core trade
> Do more work (or store more copies) at **write time** so that **read time** is cheap. The costs can include storage, maintenance work and either staleness or stronger coordination to keep copies current.

## Step 0: make each read cheaper

Before adding infrastructure, check the basics:

- **Indexes** that match your query patterns (compare execution plans and measured latency with representative data).
- **Avoid N+1 queries**: fetch 50 posts and their authors in 2 queries, not 51.
- **Return less**: paginate, select only needed columns.
- **Connection pooling**, so the database isn't spending its time on connection setup.

Measure their benefit before adding infrastructure; gains depend on the original bottleneck.

The N+1 pattern is worth spelling out, because ORMs produce it silently:

```
posts = db.query("SELECT * FROM posts"
                 " LIMIT 50")
for p in posts:          # 50 more
    p.author = db.get_user(p.author_id)
# Assume 1 ms per serial round trip:
# 51 round trips = 51 ms (network only)
# vs 2 queries (IN (...)) = ~2 ms
```

## Read replicas

A primary handles all writes and streams its change log to one or more **replicas**, which serve reads.

```
          writes
 app ------------> [ Primary ]
  |                  |  |
  |      replication |  | (async)
  |                  v  v
  +--reads-->  [Rep 1] [Rep 2]
```

- Adds read-serving capacity subject to replication overhead, workload balance and shared bottlenecks. Replica limits depend on the engine and service configuration; check current provider documentation.
- Replicas also give you failover candidates and a place for heavy analytics queries.
- Writes don't scale: every replica must still apply every write.

### Replication lag

With asynchronous replication, visibility can lag without a fixed upper bound; monitor replay progress and failure recovery. That causes anomalies:

- **Read-your-writes violation**: a user edits their profile, the page reloads from a replica and shows the old name.
- **Monotonic reads violation**: two refreshes hit different replicas and data appears to go backwards in time.

Common fixes:

1. Route a user's reads to the **primary for a short window** (say 10 s) after they write. This is a heuristic, not a guarantee when lag can exceed that window.
2. Track the write's log position (for example, Postgres's WAL LSN) and only read from replicas that have caught up to it.
3. **Pin each user to one advancing replica** to reduce backward jumps; carry a minimum observed version across failover or reassignment for a monotonic-read guarantee.

## Caching layers

A cache stores the results of expensive reads in memory, typically Redis or Memcached, or at the edge in a CDN.

```
 client -> [CDN] -> [app + local cache]
                      |
                   [Redis]  hit
                      | miss
                   [ DB ]
```

Layers from the user inwards:

| Layer | Holds | Main considerations |
|---|---|---|
| Browser/CDN | Cacheable responses/assets | Cache policy and network distance |
| In-process | Hot keys | Per-instance freshness and memory |
| Distributed | Shared results | Network, load and consistency |
| Database buffer cache | Hot pages | Query work, locks and I/O |

> [!note] Evidence gap
> Fixed cache and database latency ranges are omitted because no measured environment supports them. The calculation below uses explicit hypothetical inputs.

The arithmetic is why caches matter. With a 95% hit rate, a 0.5 ms cache and a 20 ms database:

```
avg = 0.95*0.5 + 0.05*20.5 = 1.5 ms
DB load = 5% of reads
```

That's 20× less database load. Push the hit rate from 95% to 99% and database load drops another 5×. Another module covers cache patterns, invalidation and stampedes in depth; architecturally, the key points are to cache close to the consumer, choose freshness, invalidation and eviction policies for each kind of data. A TTL is useful in many designs but does not alone bound source-data age; immutable content-addressed data can use different policies.

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
- Some systems maintain views **incrementally** as source data changes (Oracle fast refresh, ClickHouse incremental materialised views triggered by source inserts rather than arbitrary later source mutations, streaming systems like Materialize).
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

## Precomputation

Taken further, you compute the answer **before anyone asks**:

- **Fan-out on write for feeds**: when someone posts, push the post ID into each follower's precomputed timeline (in Redis). Reading a feed becomes one list fetch. Twitter used this approach for most users.
- **Leaderboards**: maintain a Redis sorted set updated on each score change, rather than sorting millions of rows per request.
- **Rollups**: hourly and daily aggregate tables for dashboards instead of scanning raw events.
- **Search autocomplete**: precomputed top-N completions per prefix.

> [!warning] Precomputation has an edge case
> Fan-out on write breaks for celebrities. A user with 50 million followers would trigger 50 million timeline writes per post. Twitter's hybrid approach: fan out on write for normal users, and merge celebrity posts in at read time.

## Choosing a technique

| Problem | First reach for |
|---|---|
| DB CPU from reads | Cache, replicas |
| Expensive joins | Denormalise |
| Expensive aggregates | Materialised view |
| Same answer for all | CDN / precompute |
| Per-user heavy query | Precompute per user |

Usually you combine them: replicas behind a cache, serving denormalised tables, with the heaviest aggregates precomputed.

## Key takeaways
- Read scaling works by copying data; every copy trades freshness and write cost for cheaper reads.
- Read replicas scale reads but not writes, and replication lag breaks read-your-writes unless you route around it.
- Caches cut database load dramatically; a few percentage points of hit rate can be a multiple of database load.
- Denormalisation and materialised views move join and aggregate work from read time to write time.
- Precomputation (feeds, leaderboards, rollups) is the extreme form, and needs special handling for skewed cases like celebrities.

## Further reading
- [AWS: Working with read replicas](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ReadRepl.html)
- [Azure Architecture Center: Materialized View pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/materialized-view)
- [Azure Architecture Center: CQRS pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs)
- [Wikipedia: Denormalization](https://en.wikipedia.org/wiki/Denormalization)
- [System Design Primer](https://github.com/donnemartin/system-design-primer)
