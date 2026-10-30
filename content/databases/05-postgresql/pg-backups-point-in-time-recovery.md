---
id: pg-backups-point-in-time-recovery
title: Backups and point-in-time recovery
level: intermediate
minutes: 3
sourceLesson: postgresql-in-practice
summary: Replicas copy mistakes too; a base backup plus archived WAL lets you rewind to just before one.
---

A standby replays the primary's changes, including mistakes. Crash recovery restores logged work; it does not know that a valid DELETE was accidental. This unit separates availability from recoverability.

## Recover an earlier database state

Replication is not a backup. A mistaken DELETE can propagate to the standby. Protect recovery separately:

- A logical dump with `pg_dump` captures one database in a form that can be restored with PostgreSQL tools. Database roles and other cluster-wide objects need separate handling.
- A physical base backup plus an unbroken series of archived WAL files supports **point-in-time recovery**, for example to just before an accidental deletion. The target must be after that base backup finished; you cannot use a backup still in progress at the desired target.
- Point-in-time recovery restores the whole database cluster, not one table. Everything after the target is missing from the restored copy, so a common way to undo one bad DELETE is to restore into a separate server and copy the lost rows back.
- Test restores into a separate environment and measure recovery time. A successful backup command alone does not prove you can recover.

> [!analogy] Real-world analogy: a shared document's version history
> A shared document is mirrored live onto a second screen in another office. If someone deletes a paragraph, the mirror shows the deletion a moment later. To get the paragraph back, you open the version history and view the document as it was at 10:41, just before the deletion.
>
> **How it maps:** the mirror is a streaming standby; it copies mistakes faithfully. The version history is a base backup plus continuous archived WAL, and choosing 10:41 is the recovery target.
>
> **Where it stops:** a document's history can restore one paragraph in place. PostgreSQL rebuilds a whole cluster, usually on a separate server, by replaying WAL forward from the backup rather than undoing changes backwards.

Choose a recovery point objective (acceptable lost work) and recovery time objective (acceptable downtime). Those requirements determine backup frequency, WAL retention, replica configuration and the restore procedure. A managed provider automates some of this, but you still need to understand its retention and recovery guarantees.

## Key takeaways

- Replication can copy an accidental deletion.
- PITR needs a suitable base backup and the required continuous WAL, and restores the whole cluster.
- Test restores against both data-loss and downtime objectives.

## Further reading

- [PostgreSQL 18: backup and restore](https://www.postgresql.org/docs/18/backup.html)
- [PostgreSQL 18: pg_dump](https://www.postgresql.org/docs/18/app-pgdump.html)
- [PostgreSQL 18: continuous archiving and PITR](https://www.postgresql.org/docs/18/continuous-archiving.html)
- [PostgreSQL 18: WAL settings](https://www.postgresql.org/docs/18/runtime-config-wal.html)
