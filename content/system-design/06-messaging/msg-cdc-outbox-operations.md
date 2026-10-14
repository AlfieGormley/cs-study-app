---
id: msg-cdc-outbox-operations
title: CDC, Debezium and outbox operations
level: advanced
minutes: 3
summary: Use database logs as the relay while keeping business contracts and replication-log retention deliberate.
sourceLesson: msg-event-driven-architecture
---

Instead of polling unsent outbox rows, a relay can tail the database’s committed change log. That removes the polling cursor race, but connector configuration, retained log positions and downstream key ordering still matter.

## Change data capture and Debezium

**Change data capture (CDC)** reads a database's own replication log and can emit captured row changes for configured tables/publications. Filters, logged-table scope, replica identity, snapshots and connector settings determine coverage and available before/after fields.

- **Postgres**: logical decoding of the write-ahead log (WAL) through a replication slot, using the `pgoutput` plugin.
- **MySQL**: the row-based binlog.
- **MongoDB**: change streams.

**Debezium** is the best-known open-source CDC platform. It usually runs as a set of Kafka Connect source connectors: it takes an initial **snapshot** of the tables, then streams changes in commit order, one Kafka topic per table by default, with each event carrying `before`, `after`, the operation and source metadata (log position, transaction ID).

Two ways to use CDC:

1. **Raw table CDC**: stream the `orders` table itself. Zero application changes, but your internal schema becomes a public contract, and you get row changes, not business events.
2. **Outbox + CDC**: stream only the `outbox` table, and use Debezium's **outbox event router** transformation to route each row to a topic based on its `aggregatetype` column and to key it by `aggregateid`. Producers publish deliberate, versioned events; CDC provides the reliable delivery.

The illustrative SQL in the preceding outbox unit uses aggregate_id and type; the default Debezium router expects aggregateid and aggregatetype (plus its other required columns). Adapt the schema or explicitly configure field mappings; the sketch is not a ready-to-run router schema.

Option 2 is a common choice for service-to-service events. Option 1 is ideal for feeding search indexes, caches and data warehouses.

> [!tip] Operational gotchas with Postgres CDC
> A replication slot makes Postgres retain WAL until the connector confirms it. If Debezium is down for a day, WAL piles up and can fill the disk. Monitor slot lag (`pg_replication_slots`) and choose a `max_slot_wal_keep_size` that protects disk capacity. Exceeding the limit can invalidate the slot and require connector recovery or a new snapshot; the cap trades retention for disk safety. Also delete or partition old outbox rows; clean them only after durable publication/checkpoint requirements are met and account for future snapshots/recovery. Removing unread business events can make a replacement snapshot unable to recover them.

## Key takeaways

- CDC captures configured row changes rather than automatically producing domain events.
- An outbox plus CDC exposes deliberate contracts; raw-table CDC suits indexes, caches and warehouse feeds.
- Debezium’s default outbox router column names differ from the illustrative outbox sketch.
- Replication-slot lag and outbox cleanup policies must preserve recovery without exhausting disk.

## Further reading

- [Reliable microservices data exchange with the outbox pattern (Debezium blog)](https://debezium.io/blog/2019/02/19/reliable-microservices-data-exchange-with-the-outbox-pattern/)
- [Debezium architecture](https://debezium.io/documentation/reference/stable/architecture.html)
