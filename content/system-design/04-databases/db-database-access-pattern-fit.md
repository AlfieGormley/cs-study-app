---
id: db-database-access-pattern-fit
title: Choose from access patterns and invariants
level: intermediate
minutes: 4
summary: Estimate workload shape, identify transaction and regional constraints, and use a decision guide as a starting point.
sourceLesson: db-choosing
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

The size estimate is just "how many things, times how big each one is". Treat it as a lower bound: indexes commonly add a large fraction on top, and every replica or backup multiplies it again. The point of the estimate is to rule options in or out quickly, not to size hardware.

## Consistency and transaction needs

- Do you need **multi-row atomic updates**, such as moving money or reserving stock? That points to a relational database or a distributed SQL database (Spanner, CockroachDB, YugabyteDB).
- Can users tolerate **stale reads** for a few seconds (feeds, view counts, recommendations)? Then eventually consistent replicas and caches are fine.
- Are there **invariants across entities** ("username unique", "no double booking")? Unique constraints in one database are far easier than coordinating across a distributed one.
- Do you need writes to keep working in **every region during a partition**? That pushes towards multi-leader or leaderless systems (Cassandra, DynamoDB global tables) and conflict handling.

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

## Check the regional ordering requirement

During an inter-region partition, independent writers cannot coordinate one immediately final strict conversation order. Choose provisional local acceptance with later ordering, or an authoritative ordering region with the resulting latency and partition-availability trade-offs. A named database does not remove that conflict.

For bursty exact-key traffic, DynamoDB on-demand is a candidate, not unlimited capacity: validate key distribution, request sizes, warm throughput, previous peak and configured table/account limits against the rollout.

## Key takeaways
- List queries, item sizes, read/write mix and latency before comparing products.
- Cross-entity invariants favour a store that can enforce them together.
- Independent regional writes cannot immediately agree on one final order during a partition.

## Further reading
- [DynamoDB: NoSQL design best practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-general-nosql-design.html)
- [PostgreSQL: Constraints](https://www.postgresql.org/docs/current/ddl-constraints.html)
- [docs.aws.amazon.com: on demand capacity mode](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/on-demand-capacity-mode.html)
