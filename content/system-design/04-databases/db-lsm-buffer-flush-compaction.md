---
id: db-lsm-buffer-flush-compaction
title: The LSM write path
level: intermediate
minutes: 2
summary: Trace buffered writes, sorted-file flushes and compaction, and compare the trade-offs with B-trees.
sourceLesson: db-indexing
---

An LSM engine improves write locality by collecting changes and flushing sorted runs. Background merging pays for that write path with additional read, rewrite and space work.

## LSM trees

The **log-structured merge tree** takes the opposite approach: never update in place, always append.

```
 write ─► WAL + memtable (sorted, in RAM)
              │ flush when full
              ▼
 L0: [SST] [SST] [SST]     newest
 L1: [ SST ][ SST ][ SST ]
 L2: [  SST  ][  SST  ]... oldest
     background compaction merges
     and drops overwritten keys
```

1. Writes go to an append-only log (for durability) and an in-memory sorted structure, the **memtable**.
2. When the memtable fills (say 64 MB), it's written out as an immutable sorted file, an **SSTable**.
3. Background **compaction** merges SSTables, discarding overwritten values and deletion markers (*tombstones*).
4. Reads check the memtable, then SSTables from newest to oldest. **Bloom filters** let a read skip files that definitely don't contain the key.

LSM trees power RocksDB, LevelDB, Cassandra, ScyllaDB, HBase, Bigtable, and the storage layers of CockroachDB, TiDB and YugabyteDB.

| | B-tree | LSM tree |
|---|---|---|
| Writes | Random, in place | Sequential, batched |
| Reads | One place to look | Several levels |
| Space | Pages part-empty | Old versions until compacted |
| Latency | Predictable | Compaction spikes |

> [!note] Rule of thumb
> B-trees favour reads and predictable latency; LSM trees favour write throughput and compression. Both are excellent; the details are in the storage internals lesson.

## Key takeaways
- Writes enter a WAL and sorted memtable before flushing to immutable SSTables.
- Compaction merges files and discards obsolete versions and eligible tombstones.
- Measure the write-locality benefit against read work and background compaction cost.

## Further reading
- [RocksDB Overview](https://github.com/facebook/rocksdb/wiki/RocksDB-Overview)
