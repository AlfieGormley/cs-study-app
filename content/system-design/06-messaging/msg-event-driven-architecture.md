---
id: msg-event-driven-architecture
title: Event-driven architecture, outbox and CDC
level: advanced
minutes: 15
summary: Event notification vs event-carried state transfer, event sourcing and CQRS, and how the transactional outbox and change data capture solve the dual-write problem.
---

"Event-driven" is used to describe at least four quite different designs. Martin Fowler's taxonomy separates them, and it is worth learning because each has different coupling, consistency and failure properties. Then we tackle the most important practical problem in event-driven systems: **publishing an event reliably when you change your database**.

## Four patterns under one name

### 1. Event notification

A service emits a small event saying something happened, with little data:

```json
{ "type": "CustomerAddressChanged",
  "customerId": "c-42", "at": "..." }
```

Interested services that need details **call back** to the source (`GET /customers/c-42`).

- Low coupling on the publisher: it does not know who listens.
- But consumers depend on the source being available at callback time, and a popular event can trigger a thundering herd of callbacks.
- It is hard to see the overall flow: behaviour is spread across many listeners.

### 2. Event-carried state transfer

The event carries the **state** consumers need:

```json
{ "type": "CustomerAddressChanged",
  "customerId": "c-42",
  "address": { "line1": "...",
               "postcode": "SW1A 1AA" } }
```

Consumers keep their own local copy of the data they care about.

- Consumers can work when the source is down, with lower latency (local reads).
- But data is duplicated and **eventually consistent**, and every event schema is now a public contract.

### 3. Event sourcing

The **events are the source of truth**. Instead of storing an account's current balance, you store every `Deposited` and `Withdrew` event, and derive the balance by replaying them.

```
stream: account-42
 1 Opened       {}
 2 Deposited    {100}
 3 Withdrew     {30}
 4 Deposited    {50}
 state = 100 − 30 + 50 = 120
```

Benefits:

- A history of recorded domain changes; audit completeness, actor identity, integrity and access controls still require design.
- **Temporal queries**: what was the balance on 1 March?
- New read models can be built later by replaying history.

Costs:

- Replaying long streams is slow, so you take periodic **snapshots** (state at event 10,000) and replay from there.
- Events are immutable, so changing their schema needs **upcasting** (transforming old versions when read) or versioned handlers.
- Personal-data erasure needs a design covering logs and derived copies. Crypto-shredding can make previously encrypted fields inaccessible only when all usable key copies are destroyed; plaintext copies and metadata remain separate concerns. A claim of GDPR compliance for a specific deployment is absent because the necessary legal and technical conditions were not established in this audit.
- Writes usually need **optimistic concurrency** on the stream: append event 5 only if the stream is still at version 4.

Event sourcing is a **storage** pattern inside one service. It does not require a message broker, and the internal events need not be the events you publish to other services.

### 4. CQRS

**Command Query Responsibility Segregation** splits the model used to change data (commands) from the model(s) used to read it (queries).

```
 command ─▶ write model ─▶ events
                              │
              ┌───────────────┤
              ▼               ▼
         read model A    read model B
         (Postgres)      (Elasticsearch)
              ▲               ▲
            query           search
```

Each read model is denormalised for one access pattern. CQRS pairs naturally with event sourcing (projections are built from the event stream) but does not require it.

With asynchronously maintained read stores, the price is **eventual consistency between write and read**: after a command succeeds, a projection may lag. CQRS itself does not require separate databases or asynchronous propagation; separate models can share one transactionally updated store. UIs must handle it, for example by returning the new state from the command, or by waiting for the projection to reach a version.

> [!warning] Use sparingly
> Fowler's advice is that CQRS suits specific bounded contexts with complex domains or very different read and write loads. Applied to a whole system by default, it adds a great deal of complexity for little gain.

## The dual-write problem

Back to the most common real-world need: when an order is saved, publish `OrderPlaced`. The naive code is:

```python
db.insert(order)          # 1
kafka.send("OrderPlaced") # 2
```

These two calls do not share an atomic transaction, so:

- Crash between 1 and 2: the order exists but no event is ever published. Downstream never ships it.
- Reverse the order (publish, then insert) and a failed insert leaves an event for an order that does not exist.
- Even without crashes, two concurrent updates can be written to the database in one order and published in the other.

Distributed transactions (two-phase commit / XA) could fix this in theory, but most brokers do not support them, and they hurt availability. (Coordinating multi-step business processes across services is the job of **sagas**, covered in the distributed systems module; sagas themselves need reliable event publishing, which is what follows.)

## The transactional outbox

The fix is to make the event part of the **same local database transaction** as the state change, by writing it to an `outbox` table:

```sql
BEGIN;
INSERT INTO orders (...) VALUES (...);
INSERT INTO outbox (id, aggregate_id,
                    type, payload)
  VALUES (gen_random_uuid(), 'o-17',
          'OrderPlaced', '{...}');
COMMIT;
```

Either both rows commit or neither does. A separate **relay** process then reads the outbox and publishes to the broker:

```
 app ─txn─▶ [orders | outbox]
                       │
                     relay
                       ▼
                    broker
```

The relay can work in two ways.

| | Polling publisher | Log tailing (CDC) |
|---|---|---|
| How | `SELECT` unsent rows | Read DB's commit log |
| Latency | Polling and processing dependent | Capture, batching and processing dependent |
| DB load | Polling queries and maintenance | Decoding, snapshots and log retention overhead |
| Ordering | Needs explicit coordination | Source order within configured capture stream; downstream ordering still needs care |

Polling has a subtle ordering trap. If the relay remembers "highest `seq` published" and polls `WHERE seq > :last`, it can skip rows. Transaction A takes `seq` 41, transaction B takes 42, and B commits first. The relay publishes 42 and moves its cursor past 41, which commits a moment later and is never sent. Sequence values are handed out at insert time, not commit time. Safer options are a `sent` flag (or deleting rows once published), or log tailing, which sees rows in commit order.

Either way, the relay is **at-least-once**: it may publish and then crash before marking the row sent, so it publishes again. Consumers must deduplicate, typically on the outbox row's `id`, which becomes the event ID.

## Change data capture and Debezium

**Change data capture (CDC)** reads a database's own replication log and can emit captured row changes for configured tables/publications. Filters, logged-table scope, replica identity, snapshots and connector settings determine coverage and available before/after fields.

- **Postgres**: logical decoding of the write-ahead log (WAL) through a replication slot, using the `pgoutput` plugin.
- **MySQL**: the row-based binlog.
- **MongoDB**: change streams.

**Debezium** is the best-known open-source CDC platform. It usually runs as a set of Kafka Connect source connectors: it takes an initial **snapshot** of the tables, then streams changes in commit order, one Kafka topic per table by default, with each event carrying `before`, `after`, the operation and source metadata (log position, transaction ID).

Two ways to use CDC:

1. **Raw table CDC**: stream the `orders` table itself. Zero application changes, but your internal schema becomes a public contract, and you get row changes, not business events.
2. **Outbox + CDC**: stream only the `outbox` table, and use Debezium's **outbox event router** transformation to route each row to a topic based on its `aggregatetype` column and to key it by `aggregateid`. Producers publish deliberate, versioned events; CDC provides the reliable delivery.

The schematic outbox SQL above uses aggregate_id and type; the default Debezium router expects aggregateid and aggregatetype (plus its other required columns). Adapt the schema or explicitly configure field mappings; the sketch is not a ready-to-run router schema.

Option 2 is a common choice for service-to-service events. Option 1 is ideal for feeding search indexes, caches and data warehouses.

> [!tip] Operational gotchas with Postgres CDC
> A replication slot makes Postgres retain WAL until the connector confirms it. If Debezium is down for a day, WAL piles up and can fill the disk. Monitor slot lag (`pg_replication_slots`) and choose a `max_slot_wal_keep_size` that protects disk capacity. Exceeding the limit can invalidate the slot and require connector recovery or a new snapshot; the cap trades retention for disk safety. Also delete or partition old outbox rows; clean them only after durable publication/checkpoint requirements are met and account for future snapshots/recovery. Removing unread business events can make a replacement snapshot unable to recover them.

## Designing good events

- **Name them in the past tense** for facts (`OrderPlaced`), and keep commands (`ShipOrder`) separate.
- **Include an event ID, type, schema version, timestamp and aggregate ID.** CloudEvents standardises an envelope with required `id`, `source`, `specversion` and `type`, plus optional `time`, `subject` and `dataschema`. `specversion` versions the envelope, not your business payload; define aggregate identity and payload version deliberately.
- **Evolve schemas compatibly**: add optional fields, never repurpose or remove required ones. Schema compatibility depends on the encoding and reader behavior. Configure the required backward/forward/transitive checks in the registry and CI; backward-only checks do not protect every old reader or replay.
- **Key events by aggregate ID** so per-entity ordering holds in a partitioned log.
- Decide deliberately between **thin** (notification) and **fat** (state transfer) events. Fat events reduce coupling at runtime but increase coupling at the schema level.

## Key takeaways
- Event notification, event-carried state transfer, event sourcing and CQRS are different patterns with different coupling and consistency trade-offs.
- Event sourcing stores events as the source of truth; it needs snapshots, schema upcasting and a plan for deleting personal data.
- CQRS separates write and read models; asynchronous projections add eventual consistency. Use it selectively.
- Writing to a database and a broker separately (dual write) loses or invents events on failure; the transactional outbox makes the event part of the local transaction.
- CDC tools such as Debezium tail the database log to publish outbox rows or table changes in commit order, at least once.

## Further reading
- [What do you mean by "Event-Driven"? (Martin Fowler)](https://martinfowler.com/articles/201701-event-driven.html)
- [Event Sourcing (Martin Fowler)](https://martinfowler.com/eaaDev/EventSourcing.html)
- [CQRS (Martin Fowler)](https://martinfowler.com/bliki/CQRS.html)
- [Pattern: Transactional outbox (microservices.io)](https://microservices.io/patterns/data/transactional-outbox.html)
- [Reliable microservices data exchange with the outbox pattern (Debezium blog)](https://debezium.io/blog/2019/02/19/reliable-microservices-data-exchange-with-the-outbox-pattern/)
- [Debezium architecture](https://debezium.io/documentation/reference/stable/architecture.html)
