---
id: msg-transactional-outbox-polling
title: Atomic event publication with an outbox
level: advanced
minutes: 4
summary: Close the database/broker dual-write gap and avoid skipping outbox rows with a sequence cursor.
sourceLesson: msg-event-driven-architecture
---

A service that changes state and publishes a fact must keep those actions consistent across crashes. The outbox moves the first durability decision into one local database transaction.

## The dual-write problem

Back to the most common real-world need: when an order is saved, publish `OrderPlaced`. The naive code is:

This is an application-adapter fragment. For the illustrated failure, assume `db.insert` durably commits the order and `kafka.send` publishes separately; a database call inside an uncommitted transaction would have a different failure boundary.

```python
# 1: Commit state in the database adapter.
db.insert(order)          # 1
# 2: Publish separately; a crash can split
# it.
kafka.send("OrderPlaced") # 2
```

These two calls do not share an atomic transaction, so:

- Crash between 1 and 2: the order exists but no event is ever published. Downstream never ships it.
- Reverse the order (publish, then insert) and a failed insert leaves an event for an order that does not exist.
- Even without crashes, two concurrent updates can be written to the database in one order and published in the other.

Distributed transactions (two-phase commit / XA) could coordinate compatible participants, but require support in both systems and can block progress during failures. (Coordinating multi-step business processes across services is the job of **sagas**, covered in the distributed systems module; sagas themselves need reliable event publishing, which is what follows.)

## The transactional outbox

The fix is to make the event part of the **same local database transaction** as the state change, by writing it to an `outbox` table:

This SQL is a schema sketch: supply real order columns and a complete payload before running it. The next CDC unit explains the default Debezium router's different column names.

```sql
BEGIN;
-- Save state and its event in one local
-- txn.
INSERT INTO orders (...) VALUES (...);
INSERT INTO outbox (id, aggregate_id,
                    type, payload)
  VALUES (gen_random_uuid(), 'o-17',
          'OrderPlaced', '{...}');
-- The relay sees only committed rows.
COMMIT;
```

Either both rows commit or neither does. A separate **outbox relay** process then reads the outbox and publishes to the broker:

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

## Key takeaways

- Separate database and publish calls can leave missing events or events for absent state.
- Commit the state and outbox row together, then relay the event at least once using a stable event ID.
- Sequence allocation order is not commit order; a highest-sequence polling cursor can permanently skip a late commit.

## Further reading

- [Pattern: Transactional outbox (microservices.io)](https://microservices.io/patterns/data/transactional-outbox.html)
- [Reliable microservices data exchange with the outbox pattern (Debezium blog)](https://debezium.io/blog/2019/02/19/reliable-microservices-data-exchange-with-the-outbox-pattern/)
