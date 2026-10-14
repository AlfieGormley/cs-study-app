---
id: db-lsm-compaction-strategies
title: LSM compaction strategies
level: advanced
minutes: 3
summary: Compare tiered, leveled and time-window compaction without assuming universal amplification or free-space bounds.
sourceLesson: db-storage-internals
---

The LSM write path leaves immutable files that need merging. The compaction strategy decides how much overlap, rewriting and temporary space a workload must tolerate.

## LSM trees in more detail

Recap: writes go to the WAL and an in-memory **memtable**; full memtables flush to immutable sorted **SSTables**; reads merge across memtable and SSTables.

An SSTable contains sorted key/value blocks (say 4–64 KB), a sparse **index** of the first key in each block, and a **bloom filter**. Deletes write a **tombstone**; the old value disappears only when compaction merges it away.

### Compaction strategies

**Size-tiered** (Cassandra's long-standing default, `STCS`): when there are several SSTables of similar size, merge them into one bigger one.

- Low write amplification.
- But a key may exist in many overlapping files (reads check more), and a merge temporarily needs as much free space as its inputs (up to 2× space).

**Leveled** (RocksDB, LevelDB, Cassandra `LCS`): level L1 is, say, 256 MB, and each level is 10× larger. Within a level (other than L0), SSTables don't overlap, so a key is in at most one file per level.

The target size of each level grows geometrically:

```formula
S_L = S_1 × T^(L − 1)
S_3 = 256 MB × 10^2 = 25,600 MB = 25.6 GB
where
S_L: the target size of level L, in megabytes (MB)
L: the level number, counting L1 as 1
S_1: the target size of level L1, here 256 MB
S_3: the target size of level L3, worked out in the second line
T: the size ratio between neighbouring levels, here 10
MB: megabyte, 1,000,000 bytes (RocksDB actually uses 1,048,576-byte mebibytes)
GB: gigabyte, 1,000 MB
In words: each level is ten times bigger than the one above, so a few levels hold a huge amount and most data sits in the last level.
```

Because each level is ten times the previous one, the last level holds roughly 90% of the data, which is why leveled compaction keeps space overhead fairly low.

```
L0  [ ][ ][ ]           overlapping
L1  [a-f][g-p][q-z]      256 MB
L2  [a-c][d-f] … [x-z]  2.5 GB
L3  … 10× again …        25 GB
```

- Fewer overlapping candidate files for a point read and often lower space overhead; L0, snapshots and temporary compaction output prevent a universal 10% bound.
- But much higher write amplification: pushing data into the next level also rewrites the overlapping data already there, with amplification depending on overlap, file selection, retained versions and workload; a level-size ratio is not a universal upper bound.

There's also time-window compaction, which suits time-series data with TTLs: whole expired windows are dropped as files. Cassandra 5.0 adds a *unified* compaction strategy that can be tuned anywhere between tiered and leveled behaviour.

## Treat the last-level share as conditional

The roughly 90% last-level statement describes a well-filled geometric layout and RocksDB's dynamic level-size targeting. Static target settings, an underfilled last level, L0 and retained versions can change the observed share. It is a model for reasoning, not a universal space guarantee.

## Key takeaways
- Tiered compaction merges similarly sized files and can retain overlapping runs.
- Leveled compaction limits per-level point-key overlap while rewriting overlapping data.
- Peak free-space needs and amplification depend on versions, snapshots, overlap and workload.

## Further reading
- [RocksDB: Leveled compaction](https://github.com/facebook/rocksdb/wiki/Leveled-Compaction)
- [cassandra.apache.org: lcs](https://cassandra.apache.org/doc/latest/cassandra/managing/operating/compaction/lcs.html)
- [cassandra.apache.org: Apache Cassandra 5.0 Features Unified Compaction Strategy](https://cassandra.apache.org/_/blog/Apache-Cassandra-5.0-Features-Unified-Compaction-Strategy.html)
