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

> [!analogy] Real-world analogy: a notebook and a filing cabinet
> An office clerk jots each new note in a notebook kept in alphabetical order, and keeps a carbon copy in a running diary. When the notebook is full, it is filed as a finished, sorted folder and a fresh notebook starts. Every so often the clerk merges several old folders into one, throwing away notes that later notes replaced.
>
> **How it maps:** The diary is the write-ahead log, the notebook is the memtable, each filed folder is an immutable SSTable, and merging folders is compaction. Looking something up means checking the notebook first, then the newest folders.
>
> **Where it stops:** Real compaction competes with live traffic for disk bandwidth, and an engine uses Bloom filters and per-file indexes to avoid opening most folders. A deletion is itself a note (a tombstone): lookups treat the old value as gone at once, but it is only physically removed when folders are merged.

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
