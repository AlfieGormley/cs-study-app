---
id: pg-wal-replicas-durability
title: WAL, replicas and commit durability
level: intermediate
minutes: 4
sourceLesson: postgresql-in-practice
summary: Commit is durable once its log record is safely on disk, and replicas follow that log at their own pace.
---

**Write-ahead logging**, or WAL, records changes before the corresponding data pages are written to durable storage. With normal durability settings, commit waits for the required WAL to be flushed; the changed table pages themselves can stay in memory and be written later. Recovery replays logged changes after a crash. A checkpoint writes out changed pages so that recovery need only replay WAL from that point; it bounds recovery work but is not a backup.

This simplified local durability path assumes synchronous commit and normal storage settings:

```flow
Transaction changes buffered pages
WAL records describe the changes
Commit WAL is flushed durably
Server acknowledges the commit
```

Writing one sequential log on commit is much cheaper than forcing every changed page, scattered across table and index files, to disk.

> [!analogy] Real-world analogy: a shop's till roll
> A busy shop writes every sale on the till roll the moment it happens, but updates the stock cards in the back office only when there is time. After a power cut, the manager rebuilds the stock cards by working through the till roll since the last time the cards were brought up to date.
>
> **How it maps:** the till roll is WAL; the stock cards are table and index pages; a sale counts as done once it is on the roll, just as a commit is durable once its WAL is flushed. The last time the cards were brought up to date is a checkpoint. A branch shop receiving copies of the roll and updating its own cards is a streaming standby.
>
> **Where it stops:** a till roll records sales in words, whereas WAL records low-level changes to specific pages. A roll survives a power cut on its own; WAL is only safe once the storage has actually flushed it.

## Settings that trade durability for speed

Two settings are easy to confuse, and their risks are very different:

- `synchronous_commit = off` lets commit return before its WAL is flushed. After a crash, the last few "committed" transactions can be lost, up to about three times `wal_writer_delay` (200 ms by default). The database remains consistent, as if those transactions had aborted. It can be set for one transaction, so only low-value writes take the risk.
- `fsync = off` stops Postgres forcing data to storage at all. An operating-system crash or power failure can leave the database corrupted beyond repair. It is only for data you can recreate, such as a throwaway bulk-load cluster.

## Replicas follow the log

Streaming replication sends WAL to a standby, which replays it. Asynchronous replication, the default, can lag: a user may write on the primary server and immediately read an older value on a standby. A failover can lose acknowledged transactions that never reached the promoted server.

With synchronous replication, the primary acknowledges a commit only after a configured standby confirms it, trading latency and availability for stronger durability. With the default `synchronous_commit = on`, the standby has flushed the WAL but may not have replayed it yet, so a read there can still be stale; `remote_apply` waits until the change is visible on the standby too.

## Key takeaways

- Durable commit needs only the WAL flushed, not every changed table page.
- `synchronous_commit = off` risks losing recent commits; `fsync = off` risks corruption.
- Asynchronous replicas can lag and lose commits on failover.
- Synchronous replication guarantees depend on what the standby must acknowledge.

## Further reading

- [PostgreSQL 18: write-ahead logging](https://www.postgresql.org/docs/18/wal-intro.html)
- [PostgreSQL 18: reliability](https://www.postgresql.org/docs/18/wal-reliability.html)
- [PostgreSQL 18: asynchronous commit](https://www.postgresql.org/docs/18/wal-async-commit.html)
- [PostgreSQL 18: standby servers and replication](https://www.postgresql.org/docs/18/warm-standby.html)
- [PostgreSQL 18: WAL settings](https://www.postgresql.org/docs/18/runtime-config-wal.html)
