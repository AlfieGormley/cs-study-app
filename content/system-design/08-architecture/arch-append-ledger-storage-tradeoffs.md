---
id: arch-append-ledger-storage-tradeoffs
title: Choosing append-oriented storage and ledgers
level: intermediate
minutes: 3
summary: Explain sequential write benefits while retaining compaction costs and balance invariants.
sourceLesson: arch-scaling-writes
---

Queues buffer work; append-oriented storage changes how the durable work is organised. Evaluate the actual read/write workload and invariant requirements rather than assuming appends are universally faster.

## Append-only designs

Updates may require lookup, concurrency control and index maintenance. Append-oriented storage can make I/O more sequential, but durability, indexing, validation and compaction still cost work. Buffered B-tree inserts do not necessarily perform a physical random read and write for every row.

Many write-heavy systems are built on this:

- **LSM-tree storage engines** (Cassandra, RocksDB, ScyllaDB, HBase) buffer writes in memory, flush sorted files sequentially, and merge them in the background (compaction). They trade buffering and sequential flushes against read amplification and compaction work. Compare measured sustained throughput: compaction can stall writes and an LSM engine is not universally faster than a B-tree.
- **Event logs**: Kafka writes every message to the end of a partition log with throughput depending on replication, acknowledgments, message size, batching, storage and network.
- **Event sourcing**: store every change as an immutable event (`ItemAdded`, `ItemRemoved`) and derive current state by replaying or projecting. Retained events can support audit history and projections; completeness, access control and write cost depend on the implementation.
- **Time-series data**: metrics and IoT readings are naturally append-only and partitioned by time.

> [!example] Counters as appends
> Instead of `UPDATE balance = balance - 10` with row locking, a ledger appends `(account, -10, ts)` rows (ts is the timestamp). The balance is a sum, kept current by a projection or periodic snapshot. Independent appends reduce contention and provide an audit trail. A no-overdraft rule still needs atomic balance validation, stream-version concurrency control or preallocated spending rights; appending debits alone does not prevent overspending.

Reading a balance from a ledger means adding the entries up, usually starting from the last saved snapshot so you don't sum the whole history every time:

Start with the last balance snapshot and apply every later credit and debit exactly once. The ledger preserves the history; the invariant check still needs an atomic decision.

## Key takeaways
- Append-oriented designs improve locality without removing durability, indexing or validation work.
- LSM storage exchanges buffered writes and sequential flushes for read amplification and compaction work.
- Event sourcing retains changes and derives current state through projections or snapshots.
- A ledger is not overdraft prevention: validate and apply debits atomically or allocate exclusive spending rights.

## Further reading
- [Wikipedia: Log-structured merge-tree](https://en.wikipedia.org/wiki/Log-structured_merge-tree)
- [Martin Fowler: Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html)
