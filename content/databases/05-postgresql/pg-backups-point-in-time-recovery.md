---
id: pg-backups-point-in-time-recovery
title: Backups and point-in-time recovery
level: intermediate
minutes: 2
sourceLesson: postgresql-in-practice
summary: Replication can copy an accidental deletion.
---

A standby replays the primary's changes, including mistakes. Crash recovery restores logged work; it does not know that a valid DELETE was accidental. This unit separates availability from recoverability.

## Recover an earlier database state

Replication is not a backup. A mistaken DELETE can propagate to the standby. Protect recovery separately:

- A logical dump with `pg_dump` captures one database in a form that can be restored with PostgreSQL tools. Database roles and other cluster-wide objects need separate handling.
- A physical base backup plus an unbroken series of archived WAL files supports **point-in-time recovery**, for example to just before an accidental deletion. The target must be after that base backup finished; you cannot use a backup still in progress at the desired target.
- Test restores into a separate environment and measure recovery time. A successful backup command alone does not prove you can recover.

Choose a recovery point objective (acceptable lost work) and recovery time objective (acceptable downtime). Those requirements determine backup frequency, WAL retention, replica configuration and the restore procedure. A managed provider automates some of this, but you still need to understand its retention and recovery guarantees.

## Key takeaways

- Replication can copy an accidental deletion.
- PITR needs a suitable base backup and the required continuous WAL.
- Test restores against both data-loss and downtime objectives.

## Further reading

- [PostgreSQL 18: backup](https://www.postgresql.org/docs/18/backup.html)
- [PostgreSQL 18: app pgdump](https://www.postgresql.org/docs/18/app-pgdump.html)
- [PostgreSQL 18: continuous archiving](https://www.postgresql.org/docs/18/continuous-archiving.html)
- [PostgreSQL 18: runtime config wal](https://www.postgresql.org/docs/18/runtime-config-wal.html)
