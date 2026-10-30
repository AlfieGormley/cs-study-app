---
id: rel-th-copy-consistency
title: Copy consistency and correctness
level: advanced
minutes: 3
sourceLesson: rel-th-denormalisation
summary: Keeping copies correct: same transaction, triggers, CDC and batch refresh, plus reconciliation and stock safety.
---

## Keeping copies consistent

Every denormalisation needs an answer to "what updates the copy, and how stale may it be?"

| Mechanism | Staleness | Main risk |
|---|---|---|
| Same transaction | one transaction commit | slower writes |
| Trigger | one transaction commit | hidden logic |
| CDC / outbox | asynchronous; often seconds, unbounded during failures | lag, ordering |
| Batch refresh | minutes+ | stale reads |

- **Application code in the same transaction** is explicit, but every code path that writes the source must remember the copy. One forgotten admin script causes drift.
- **Enabled triggers** automatically run for their configured events, but uncovered operations or disabled triggers can still leave gaps; they are also invisible to someone reading the application, can cascade, and add lock contention.
- **Change data capture** (reading the write-ahead log, for example with Debezium) or a transactional outbox propagates changes asynchronously to other tables, search indexes or services. Writes stay fast, readers see eventual consistency.
- **Batch rebuilds** (materialised view refresh, nightly jobs) are simple and self-healing, at the cost of staleness.

Whatever you choose, add a **copy reconciliation check**: a periodic query comparing the copy with the source, such as counts that disagree with `COUNT(*)`. Drift happens, through bugs, manual fixes and restores, and you want to find it before customers do.

## The trade-off in one picture

```
            normalised   denormalised
reads       more joins   fewer joins
writes      one place    many places
integrity   by schema    by your code
change      easy         harder
storage     less         more
```

Denormalise when reads vastly outnumber writes to the copied data, the read path is measured to be the bottleneck, and some staleness is acceptable or the sync can be transactional. Avoid it for data that changes often and is copied widely (a username copied into millions of messages), or where a stale value causes real harm (balances, stock).

## Atomic maintenance still needs a protocol

“Same transaction” means the source and copy commit or roll back together when every relevant write uses that protocol. Under PostgreSQL Read Committed, two separate reads can still see different committed snapshots; use one statement or a suitable transaction snapshot when comparing copies. A read-modify-write counter based on an earlier unlocked read can lose increments. An atomic relative update, or appropriate locking, avoids that race. Multi-row maintenance can deadlock when transactions lock parents in different orders; choose a consistent order and handle retries.

For stock, keep one authoritative non-null count per product with a non-negative check. Decrement it in the same transaction as creating the order, and require exactly one row to be updated; a missing row must fail the order too. A refreshed dashboard copy cannot enforce no-oversell, however often it refreshes.

An outbox makes the data change and event record atomic inside PostgreSQL; it does not make a later search-index write part of that transaction. Retried delivery can duplicate events, consumers must be idempotent, and per-entity ordering or version checks prevent a **stale database update** replacing a newer one. Lag can be unbounded during failures. Reconciliation and replay remain necessary.

## Key takeaways

- One transaction commit, consistent reading and asynchronous delivery are separate guarantees.
- Correctness-critical stock needs an authoritative transaction protocol; lagging copies suit reports.

## Further reading

- [PostgreSQL 18: refresh materialised views](https://www.postgresql.org/docs/18/sql-refreshmaterializedview.html)
- [PostgreSQL 18: generated columns](https://www.postgresql.org/docs/18/ddl-generated-columns.html)
- [AWS: transactional outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)
