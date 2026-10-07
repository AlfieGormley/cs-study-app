---
id: db-choosing
title: Choosing a database
level: intermediate
minutes: 13
summary: Pick a database from access patterns, consistency needs, scale and operational cost, and know when to use several.
---

"Which database should we use?" is one of the most common system design questions, and "it depends" is only a good answer if you can say *on what*. This lesson gives you a repeatable way to decide.

## Start with access patterns

Write down how the data is read and written before thinking about products.

- **What are the queries?** By primary key? By ranges? Ad-hoc filters? Full-text? Multi-hop relationships? Aggregates over millions of rows?
- **What's the read/write ratio?** 100:1 read-heavy (a catalogue) and 1:10 write-heavy (telemetry) want different engines.
- **How big is each item and the whole dataset?** 1 KB rows × 100 million = 100 GB before indexes and overhead. Even 10 TB can fit on some machines; assess working-set memory, I/O, growth and recovery time rather than treating a data size as a universal single-node limit.
- **What latency is needed?** Sub-millisecond (in-memory), single-digit ms (OLTP), seconds (analytics).
- **Are the queries known up front?** Key-value and wide-column stores need them known; relational and search engines tolerate ad-hoc ones.

> [!example] Back-of-envelope
> 20 million users × 50 orders each × 500 bytes = 500 GB of orders. Peak 2,000 writes/s and 20,000 reads/s. That is a candidate for a Postgres primary with read replicas and a cache. Benchmark the actual transactions, indexes, contention and recovery requirements before deciding whether one primary has enough headroom.

## Consistency and transaction needs

- Do you need **multi-row atomic updates**, such as moving money or reserving stock? That points to a relational database or a distributed SQL database (Spanner, CockroachDB, YugabyteDB).
- Can users tolerate **stale reads** for a few seconds (feeds, view counts, recommendations)? Then eventually consistent replicas and caches are fine.
- Are there **invariants across entities** ("username unique", "no double booking")? Unique constraints in one database are far easier than coordinating across a distributed one.
- Do you need writes to keep working in **every region during a partition**? That pushes towards multi-leader or leaderless systems (Cassandra, DynamoDB global tables) and conflict handling.

## Scale

Be honest about it. A single well-run relational primary is a useful starting point; measure whether it meets this workload’s availability, throughput and recovery needs.

| Scale signal | Typical answer |
|---|---|
| Workload fits a measured single-node budget | One relational primary |
| Read-heavy beyond that | Replicas + cache |
| Writes beyond one node | Shard or distributed DB |
| Global low-latency writes | Multi-region store |

Scaling triggers worth acting on: cache misses cause unacceptable measured I/O or latency, write throughput nears the primary's limit even after tuning, or backups and restores take too long to meet recovery targets.

## Operational cost

The database you can *run well* beats the theoretically better one you can't.

- **Managed or self-hosted?** RDS, Aurora, Cloud SQL, DynamoDB, Atlas and Astra automate parts of patching, backups and failover; you still own configuration, recovery testing, access control and application behavior, at a price premium (and with some loss of control).
- **Team expertise.** Operating Cassandra well (repairs, compaction tuning, tombstones) is a real skill. Postgres knowledge is widespread.
- **Ecosystem.** Drivers, ORMs, migration tools, monitoring, backups, CDC connectors.
- **Cost model.** DynamoDB on-demand charges per request, and provisioned charges per capacity unit-hour, which can be cheaper for steady, predictable traffic; compare current regional rates, utilization and commitments rather than assuming a fixed saving. Aurora charges for instances plus storage, and either per I/O or a higher flat rate on its I/O-Optimized configuration. Self-hosted charges in engineer time.
- **Lock-in.** DynamoDB's API is proprietary; Postgres-compatible services let you move between providers.

> [!warning] Résumé-driven development
> Choosing a distributed database for a 50 GB dataset adds operational complexity. It can still be justified by regional availability, locality or throughput requirements; small size alone neither requires nor rules it out. Start simple, measure, and move when the numbers demand it.

## A decision guide

```
Need multi-entity transactions
or ad-hoc queries?
 ├─ yes ─► Relational (Postgres/MySQL)
 │          outgrown one node?
 │           └─► Vitess/Citus or
 │               distributed SQL
 └─ no ─► What is the access pattern?
    ├ key lookup, huge scale ► DynamoDB
    ├ huge write volume      ► Cassandra
    ├ nested aggregates      ► MongoDB
    ├ multi-hop relations    ► Neo4j
    ├ metrics over time      ► Timescale
    ├ full-text relevance    ► Elastic
    └ analytics, billions     ► Columnar
```

Treat it as a starting point, not a rule. Postgres alone covers several of these branches (`jsonb`, full-text search, PostGIS, TimescaleDB) for moderate scale.

## Polyglot persistence

Large systems usually use several stores, each for what it does best. This is called **polyglot persistence**.

```
         ┌──────────────┐
writes ─►│   Postgres   │ source
         └──────┬───────┘ of truth
                │ CDC (Debezium)
                ▼
         ┌──────────────┐
         │    Kafka     │
         └─┬─────┬────┬─┘
           ▼     ▼    ▼
      Elastic  Redis  Warehouse
      (search) (cache)(analytics)
```

Typical example, an online shop:

- **Postgres**: orders, payments, inventory (transactions).
- **Redis**: sessions, carts, rate limits, hot product cache.
- **Elasticsearch / OpenSearch**: product search with facets.
- **S3 + a columnar warehouse** (Snowflake, BigQuery, Redshift, ClickHouse): analytics.

### The costs of polyglot persistence

- **Keeping stores in sync.** Never "dual write" from the application (write to Postgres, then to Elasticsearch): if the second write fails, the stores silently diverge. Instead, make one store the source of truth and derive the others from its change log (CDC), or use the transactional **outbox** pattern: write the event to an `outbox` table in the *same* transaction as the data, and have a relay publish it. These commonly use at-least-once delivery, conditional on reliable capture, retention and retries. Consumers must handle duplicates and ordering. A processed-event record only deduplicates an effect atomically when both are in the same transaction; external email or payment calls need a provider-supported idempotency protocol and reconciliation.
- **More things to operate**: backups, upgrades, monitoring, on-call for each.
- **Consistency gaps**: derived stores lag the source. Design the UX to tolerate it (e.g. a new product appears in search a second later).

> [!tip] One source of truth per fact
> For each piece of data, name the system of record. Everything else is a derived, rebuildable view. If you can't rebuild your search index from scratch, it has quietly become a source of truth.

## Worked choice: a ride-hailing app

1. **Trips, payments, driver accounts**: transactional, relational. Postgres (or Aurora), sharded by city if needed.
2. **Driver locations**: millions of updates per minute, only the latest matters, queried by geography. Redis with geospatial indexes, or an in-memory grid service.
3. **Trip history for riders**: a key-value or wide-column store keyed by rider id, sorted by time, because it's write-once and read by key.
4. **Surge pricing analytics**: stream processing into a columnar store.
5. **Glue**: CDC from the trip database into Kafka feeds history, analytics and search.

## Key takeaways
- Choose from access patterns first: queries, read/write mix, data size, latency, and whether queries are known up front.
- Transactions and cross-entity invariants point to relational or distributed SQL; tolerance of staleness opens up eventually consistent stores.
- Measure how long one relational primary plus replicas and caching meets the actual service objectives.
- Operational cost and team expertise are first-class criteria; managed services trade money for time.
- Polyglot persistence uses the right store for each job, but derive secondary stores from one source of truth via CDC or an outbox, never ad-hoc dual writes.

## Further reading
- [Martin Fowler: Polyglot Persistence](https://martinfowler.com/bliki/PolyglotPersistence.html)
- [The System Design Primer](https://github.com/donnemartin/system-design-primer)
- [DynamoDB: NoSQL design best practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-general-nosql-design.html)
- [Wikipedia: NoSQL](https://en.wikipedia.org/wiki/NoSQL)
- [microservices.io: Transactional outbox](https://microservices.io/patterns/data/transactional-outbox.html)
- [DynamoDB: Capacity modes](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/capacity-mode.html)
