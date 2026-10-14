---
id: arch-batching-fixed-write-costs
title: Amortising fixed write costs with batches
level: intermediate
minutes: 3
summary: Separate per-commit overhead from per-row work and decide what batching can safely delay.
sourceLesson: arch-scaling-writes
---

Sharding changes who owns writes. Batching instead reduces fixed overhead for the same owner. The following flush calculation explicitly assumes no database group commit.

## Write batching

Much of a write's cost is fixed overhead: a network round trip, a transaction, an `fsync`. Batching amortises it.

Suppose each commit has to wait for its own `fsync` (no grouping by the database). Then the number of flushes depends only on how many rows you put in each transaction:

```formula
F = ⌈R / B⌉
F = 1000 / 1 = 1000 fsyncs
F = 1000 / 1000 = 1 fsync
where
F: the number of transactions, and so of fsync flushes to disk
R: the number of rows to write, here 1,000
B: rows per transaction (the batch size): 1 in the first case, 1,000 in the second
fsync: one forced flush of the log to durable storage, the slow fixed cost of a commit
fsyncs: plural of fsync
⌈ ⌉: ceiling: round up to a whole transaction
In words: 1,000 one-row transactions pay for 1,000 disk flushes; one 1,000-row transaction pays for one.
```

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
