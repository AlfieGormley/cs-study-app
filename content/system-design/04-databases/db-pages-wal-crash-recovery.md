---
id: db-pages-wal-crash-recovery
title: Pages, WAL and crash recovery
level: advanced
minutes: 4
summary: Trace durable commit before dirty-page flush and weigh checkpoints, full-page images and async commit.
sourceLesson: db-storage-internals
---

Underneath every database is a **storage engine**: the code that lays bytes out on disk, survives crashes and answers lookups. Knowing how it works lets you predict performance, tune it and choose between engines. This unit goes one level below the earlier indexing units.

## Disks, pages and the buffer pool

Disks read and write in blocks, and random I/O is far slower than sequential: a good NVMe SSD manages hundreds of thousands of random 4 KB reads per second (high-end drives exceed a million) and several GB/s sequentially; a spinning disk manages only ~100–200 random I/Os per second.

These indicative hardware figures vary by device, queue depth, cache and workload; they are not measurements from this review. Measure the selected storage under the actual workload.

These indicative hardware figures vary by device, queue depth, cache and workload; they are not measurements from this review. Measure the selected storage under the actual workload.

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
5. After a crash, **crash recovery** replays WAL from the checkpoint redo position. Physical redo can include changes made by transactions that never committed. Postgres uses transaction status and MVCC to keep those versions invisible; engines such as InnoDB also undo uncommitted changes.

Why it's fast: the WAL is a sequential append, while page writes are random. Commit costs one sequential `fsync` instead of many random page writes. **Group commit** batches several transactions' commits into one `fsync`.

> [!warning] Torn pages
> A crash midway through writing an 8 KB page to a disk with 4 KB storage-atomic writes leaves half old, half new. Postgres guards against this by logging a *full page image* the first time a page changes after each checkpoint (`full_page_writes`); InnoDB uses a doublewrite buffer.

The WAL also feeds **replication** (followers replay it) and **change data capture**.

> [!tip] Durability knobs
> `synchronous_commit = off` (Postgres) or `innodb_flush_log_at_trx_commit = 2` (MySQL) skip the per-commit flush. Throughput rises, but a power loss or OS crash can lose recently acknowledged commits: up to about 3 × `wal_writer_delay` (around 600 ms by default) in Postgres, and about a second in MySQL at its default background flush interval. MySQL scheduling and configuration can widen that approximate loss window; it is not a hard one-second bound. Neither corrupts the database; turning off `fsync` entirely is what does that.

The Postgres figure comes from how often the background WAL writer flushes. The PostgreSQL documentation gives the worst case as three of its cycles:

```formula
t_loss ≤ 3 × d_w
t_loss ≤ 3 × 200 ms = 600 ms
where
t_loss: the longest window of acknowledged commits that a crash can lose, in milliseconds (ms)
d_w: the WAL writer delay, the `wal_writer_delay` setting: how long the WAL writer sleeps between flushes, 200 ms by default
≤: less than or equal to
ms: millisecond, one thousandth of a second
In words: with asynchronous commit, a crash can lose up to about three WAL-writer cycles of commits, roughly the last 0.6 seconds at the default setting.
```

Raising `wal_writer_delay` widens the window in proportion. Lost commits are lost cleanly: recovery still ends at a consistent point.

## Key takeaways
- Pages are cached and modified in memory; WAL must reach durable storage before dependent data pages.
- Durable commit can finish before dirty pages reach their final locations.
- Checkpoint spacing, torn-page protection and async commit change recovery work and loss windows.

## Further reading
- [PostgreSQL: Write-Ahead Logging](https://www.postgresql.org/docs/current/wal-intro.html)
- [PostgreSQL: Database page layout](https://www.postgresql.org/docs/current/storage-page-layout.html)
- [PostgreSQL: Asynchronous commit](https://www.postgresql.org/docs/current/wal-async-commit.html)
- [PostgreSQL: WAL configuration](https://www.postgresql.org/docs/current/wal-configuration.html)
