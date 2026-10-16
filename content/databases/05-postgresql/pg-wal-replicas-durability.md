---
id: pg-wal-replicas-durability
title: WAL, replicas and commit durability
level: intermediate
minutes: 3
sourceLesson: postgresql-in-practice
summary: Durable commit need not flush every changed table page.
---

**Write-ahead logging**, or WAL, records changes before corresponding data pages are written to durable storage. With normal durability settings, commit waits for the required WAL to be flushed; all changed table pages need not already be on disk. Recovery can replay logged changes after a crash. A checkpoint bounds recovery work; it is not a fresh backup.

This simplified local durability path assumes synchronous commit and normal storage settings:

```flow
Transaction changes buffered pages
WAL records describe the changes
Commit WAL is flushed durably
Server acknowledges the commit
```

Streaming replication sends WAL to a standby. Asynchronous replication can lag: a user may write on the primary server and immediately read an older value on a standby. A failover can lose acknowledged transactions that never reached the promoted server. Synchronous replication can wait for a configured standby acknowledgement, trading latency and availability for stronger durability; whether replay is awaited depends on configuration.

## Key takeaways

- Durable commit need not flush every changed table page.
- Asynchronous replicas can lag and lose commits on failover.
- Synchronous replication guarantees depend on its acknowledgement settings.

## Further reading

- [PostgreSQL 18: wal intro](https://www.postgresql.org/docs/18/wal-intro.html)
- [PostgreSQL 18: wal reliability](https://www.postgresql.org/docs/18/wal-reliability.html)
- [PostgreSQL 18: warm standby](https://www.postgresql.org/docs/18/warm-standby.html)
- [PostgreSQL 18: runtime config wal](https://www.postgresql.org/docs/18/runtime-config-wal.html)
