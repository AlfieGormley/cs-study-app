---
id: arch-batching-fixed-write-costs
title: Amortising fixed write costs with batches
level: intermediate
minutes: 3
summary: Separate per-commit overhead from per-row work and decide what batching can safely delay.
sourceLesson: arch-scaling-writes
---

Sharding changes who owns writes. Batching instead reduces fixed overhead for the same owner.

## Write batching

Much of a write's cost is fixed overhead: a network round trip, a transaction, an `fsync`. Batching amortises it.

A batch shares the commit overhead across its rows. Group commit can also share flushes across transactions, so one flush per transaction is only a simplified model.

Each row still has to be written, so the saving is the fixed per-commit cost, not all of the work.

Examples:

- Multi-row `INSERT ... VALUES (...), (...), ...` or Postgres `COPY` for bulk loads.
- **Group commit**: databases combine several concurrent transactions into one log flush.
- **Kafka producers** batch messages per partition (`linger.ms`, `batch.size`), amortising request costs; added waiting, throughput and end-to-end latency depend on load and batching settings.
- **Client-side aggregation**: instead of writing every page view, count views in memory for 5 seconds and write `+137` once.

The cost is latency and the risk of losing an unflushed batch if the process crashes. Only batch in memory what you can afford to lose, or put a durable log in front.

## Key takeaways
- Batching amortises fixed transaction, request or flush costs while still doing per-row work.
- Group commit shares a log flush across independent transactions; it differs from one large client transaction.
- Producer waiting and in-memory aggregation trade latency and crash exposure for fewer requests.
- Use measured throughput and durable buffering where losing the pending batch is unacceptable.

## Further reading
- [Wikipedia: Log-structured merge-tree](https://en.wikipedia.org/wiki/Log-structured_merge-tree)
