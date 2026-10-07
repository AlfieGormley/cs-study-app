---
id: db-storage-internals
title: Storage engine internals
level: advanced
minutes: 17
summary: Write-ahead logs, pages, compaction, read/write/space amplification, bloom filters, and why analytics uses column stores.
---

Underneath every database is a **storage engine**: the code that lays bytes out on disk, survives crashes and answers lookups. Knowing how it works lets you predict performance, tune it and choose between engines. This lesson goes one level below the indexing lesson.

## Disks, pages and the buffer pool

Disks read and write in blocks, and random I/O is far slower than sequential: a good NVMe SSD manages hundreds of thousands of random 4 KB reads per second (high-end drives exceed a million) and several GB/s sequentially; a spinning disk manages only ~100–200 random I/Os per second.

So databases organise data into fixed-size **pages**: 8 KB in Postgres, 16 KB in InnoDB, 4 KB in SQLite by default. A page is the unit of I/O and of caching.

```
 Postgres heap page (8 KB)
┌────────────────────────────┐
│ header (LSN, free space)   │
│ item pointers ► 1 2 3 4 …  │
│                            │
│       free space           │
│                            │
│ … tuple 4 │ tuple 3 │ t2 t1│
└────────────────────────────┘
 pointers grow down, tuples up
```

The **buffer pool** (`shared_buffers` in Postgres, `innodb_buffer_pool_size` in MySQL) caches hot pages in RAM. A modified ("dirty") page is written back later, not at commit. That raises the question: what if the server crashes before it's written?

## The write-ahead log

The answer is the **write-ahead log (WAL)**, called the redo log in InnoDB. The rule: *before any change to a data page reaches disk, the log record describing it must be on disk*.

1. A transaction modifies pages in the buffer pool and appends records to the WAL buffer.
2. With durable commit settings, WAL is flushed using the configured synchronization method up to the commit record. That's the durability point.
3. Dirty pages are written to their real locations later, in the background.
4. A **checkpoint** periodically ensures all pages dirtied before a given log position are on disk, so older WAL can be recycled. Checkpoint spacing is a trade-off: further apart means fewer page writes (repeated changes to a hot page coalesce) and fewer full-page images, but more WAL to keep and a longer replay after a crash.
5. After a crash, **recovery** replays WAL from the checkpoint redo position. Physical redo can include changes made by transactions that never committed. Postgres uses transaction status and MVCC to keep those versions invisible; engines such as InnoDB also undo uncommitted changes.

Why it's fast: the WAL is a sequential append, while page writes are random. Commit costs one sequential `fsync` instead of many random page writes. **Group commit** batches several transactions' commits into one `fsync`.

> [!warning] Torn pages
> A crash midway through writing an 8 KB page to a disk with 4 KB atomic writes leaves half old, half new. Postgres guards against this by logging a *full page image* the first time a page changes after each checkpoint (`full_page_writes`); InnoDB uses a doublewrite buffer.

The WAL also feeds **replication** (followers replay it) and **change data capture**.

> [!tip] Durability knobs
> `synchronous_commit = off` (Postgres) or `innodb_flush_log_at_trx_commit = 2` (MySQL) skip the per-commit flush. Throughput rises, but a power loss or OS crash can lose recently acknowledged commits: up to about 3 × `wal_writer_delay` (around 600 ms by default) in Postgres, and about a second in MySQL. Neither corrupts the database; turning off `fsync` entirely is what does that.

## LSM trees in more detail

Recap: writes go to the WAL and an in-memory **memtable**; full memtables flush to immutable sorted **SSTables**; reads merge across memtable and SSTables.

An SSTable contains sorted key/value blocks (say 4–64 KB), a sparse **index** of the first key in each block, and a **bloom filter**. Deletes write a **tombstone**; the old value disappears only when compaction merges it away.

### Compaction strategies

**Size-tiered** (Cassandra's long-standing default, `STCS`): when there are several SSTables of similar size, merge them into one bigger one.

- Low write amplification.
- But a key may exist in many overlapping files (reads check more), and a merge temporarily needs as much free space as its inputs (up to 2× space).

**Leveled** (RocksDB, LevelDB, Cassandra `LCS`): level L1 is, say, 256 MB, and each level is 10× larger. Within a level (other than L0), SSTables don't overlap, so a key is in at most one file per level.

```
L0  [ ][ ][ ]           overlapping
L1  [a-f][g-p][q-z]      256 MB
L2  [a-c][d-f] … [x-z]  2.5 GB
L3  … 10× again …        25 GB
```

- Fewer overlapping candidate files for a point read and often lower space overhead; L0, snapshots and temporary compaction output prevent a universal 10% bound.
- But much higher write amplification: pushing data into the next level also rewrites the overlapping data already there, with amplification depending on overlap, file selection, retained versions and workload; a level-size ratio is not a universal upper bound.

There's also time-window compaction, which suits time-series data with TTLs: whole expired windows are dropped as files. Cassandra 5.0 adds a *unified* compaction strategy that can be tuned anywhere between tiered and leveled behaviour.

## The three amplifications

**Write amplification**: bytes written to disk ÷ bytes the application wrote. **Read amplification**: disk reads per logical read. **Space amplification**: bytes on disk ÷ size of live data.

| | B-tree | LSM leveled | LSM tiered |
|---|---|---|---|
| Write amp | Medium–high | High | Low |
| Read amp | Low | Low–med | Higher |
| Space amp | Depends on page fill and retained versions | Depends on levels, versions and temporary output | Depends on retained files and temporary output |

A B-tree's write amplification comes from writing a whole 8–16 KB page (plus WAL, plus full-page images) for a small change. The key variable is how many changes a page collects before it's written back:

- Sequential inserts or a hot working set that fits in RAM: many changes per page write, so the amplification is modest.
- Random updates to a table far bigger than RAM: perhaps one 100-byte change per 16 KB page write, which is over 150×, and InnoDB's doublewrite buffer doubles it.

Leveled LSM amplification comes from compaction overlap and repeated rewriting. No universal 10–30× range or winner is supplied because a matched workload benchmark is absent. Compare measured read/write latency and amplification: an LSM read may check several levels, and background compaction competes for I/O.

The **RUM conjecture** formalises the trade: you can optimise for two of Read, Update and Memory (space) overheads, at the expense of the third. Every engine picks a point; tuning moves it.

On SSDs, write amplification also matters because flash cells wear out after a limited number of program/erase cycles.

## Bloom filters

A **bloom filter** answers "is this key *possibly* in this set?" using very little memory. It never gives a false negative, and gives false positives at a tunable rate.

How it works: a bit array of *m* bits, and *k* hash functions. To add a key, set the *k* bits it hashes to. To check, test those *k* bits: any zero means "definitely not present".

```
add "cat": h1=2 h2=5 h3=9
bits: 0 0 1 0 0 1 0 0 0 1
check "dog": h1=2 h2=4 h3=9
bit 4 is 0 → definitely absent
```

With about **10 bits per key** and the best *k* (≈7), the false-positive rate is about **1%**. A billion keys need ~1.2 GB of filter, a fraction of the data size.

In an LSM tree, each SSTable has a filter. A read for a missing key consults filters for every level and skips almost all of them, so a lookup may need far fewer candidate-file checks. False positives still require checking metadata or cached/disk blocks; there is no guarantee of at most one file read. RocksDB, Cassandra (`bloom_filter_fp_chance`), HBase and Bigtable all do this.

Bloom filters can't help range scans, which have to visit every level. RocksDB's prefix bloom filters help when ranges share a prefix.

## OLTP vs OLAP

| | OLTP | OLAP |
|---|---|---|
| Query | Few rows by key | Scan millions |
| Users | Customers, apps | Analysts, BI |
| Writes | Small, random | Bulk loads |
| Data size | GB–TB | TB–PB |

Large analytical scans can harm latency-sensitive OLTP workloads: a big aggregate evicts hot pages from the buffer pool and competes for I/O. That's why analytics moves to a separate **data warehouse**, fed by ETL or CDC.

## Column stores

Row stores keep each row's columns together, which is ideal for "fetch order 42". But an analytical query like

```sql
SELECT region, sum(revenue_p)
FROM sales
WHERE sale_date >= '2026-01-01'
GROUP BY region;
```

reads only 3 columns of a 100-column table. A full row-store heap scan reads pages containing the other columns too, but covering indexes, cache residency and projections can change the I/O comparison.

A **column store** keeps each column in its own file (or segment):

```
 row store:   [id,date,region,rev,...]
              [id,date,region,rev,...]

 column store:
   date:   [d1 d2 d3 d4 ...]
   region: [UK UK UK FR ...]
   rev:    [12 40  7 33 ...]
```

Benefits:

- **Read only the needed columns**: 3 of 100 equally sized columns would mean roughly 97% less uncompressed column data. Actual I/O savings depend on column sizes, compression, indexes and row-group pruning.
- **Compression**: a column holds similar values. Run-length encoding (`UK×3`), dictionary encoding and bit-packing can compress repeated or correlated values; the ratio depends on the dataset and encoding.
- **Vectorised execution**: processing a batch of values from one column in a tight loop uses CPU caches and SIMD instructions efficiently.
- **Zone maps**: min/max per block let the engine skip blocks that can't match `sale_date >= '2026-01-01'`.

Costs: a pure column layout may update many column chunks, so many column stores batch writes (often via an in-memory row buffer, LSM-style) and are poor at single-row updates.

Examples: Snowflake, BigQuery (Capacitor format, Dremel engine), Amazon Redshift, ClickHouse, Apache Druid, DuckDB, and file formats like **Parquet** and ORC. Some databases are hybrids (HTAP): SQL Server columnstore indexes, TiDB with TiFlash, SingleStore.

## Key takeaways
- Pages are the unit of I/O and caching; the buffer pool holds hot ones in RAM.
- The WAL makes commits durable with one sequential flush, enables crash recovery, and feeds replication and CDC.
- LSM compaction strategies trade write, read and space amplification: tiered for writes, leveled for reads and space.
- Bloom filters let LSM reads skip files that can't contain a key, at about 10 bits per key for a 1% false-positive rate.
- OLAP belongs in column stores: read only the needed columns, compress heavily, and process them in vectorised batches.

## Further reading
- [PostgreSQL: Write-Ahead Logging](https://www.postgresql.org/docs/current/wal-intro.html)
- [PostgreSQL: Database page layout](https://www.postgresql.org/docs/current/storage-page-layout.html)
- [RocksDB: Leveled compaction](https://github.com/facebook/rocksdb/wiki/Leveled-Compaction)
- [Wikipedia: Bloom filter](https://en.wikipedia.org/wiki/Bloom_filter)
- [Wikipedia: Column-oriented DBMS](https://en.wikipedia.org/wiki/Column-oriented_DBMS)
- [PostgreSQL: Asynchronous commit](https://www.postgresql.org/docs/current/wal-async-commit.html)
- [Mark Callaghan: Read, write and space amplification](https://smalldatum.blogspot.com/2015/11/read-write-space-amplification-pick-2_23.html)
