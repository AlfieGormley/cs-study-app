---
id: db-polyglot-outbox-handoff
title: Polyglot stores and durable handoff
level: intermediate
minutes: 3
summary: Keep one source of truth per fact and derive search, caches and analytics through CDC or an outbox.
sourceLesson: db-choosing
---

Several stores can serve different access paths, but each fact still needs one authoritative owner. Durable handoff connects that owner to derived views without relying on two independent application writes.

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
- Specialist stores can serve locations, history, search and analytics alongside transactional data.
- Ad-hoc dual writes can diverge after a partial failure.
- CDC or an outbox needs reliable delivery and duplicate handling; external effects need an idempotency protocol.

## Further reading
- [debezium.io: outbox event router](https://debezium.io/documentation/reference/stable/transformations/outbox-event-router.html)
- [Resend: Idempotency keys](https://resend.com/docs/dashboard/emails/idempotency-keys)
- [Martin Fowler: Polyglot Persistence](https://martinfowler.com/bliki/PolyglotPersistence.html)
