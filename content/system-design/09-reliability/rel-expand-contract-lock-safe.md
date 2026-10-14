---
id: rel-expand-contract-lock-safe
title: Expand-contract migrations and lock queues
level: advanced
minutes: 3
summary: Preserve compatibility through staged schema change and bound database-lock disruption.
sourceLesson: rel-safe-deployments
---

Reader-first rollout keeps data formats compatible. Database columns need the same care across old and new application versions. “Zero downtime” is an engineering goal with explicit lock, writer-synchronisation and rollback prerequisites, rather than a guarantee from a command name.

## Zero-downtime schema changes: expand and contract

You can't upgrade the database and every application server in the same instant. For some period, old and new code run against the same schema. So schema changes must be split into compatible steps. Martin Fowler calls this **parallel change**, or **expand and contract**.

Example: rename column `fullname` to `display_name` on a large `users` table.

```
1 EXPAND   add display_name (nullable)
2 DUAL     app writes both columns
3 BACKFILL copy fullname → display_name
4 MIGRATE  app reads display_name
5 CONTRACT stop writing fullname,
           later drop the column
```

Before switching reads, all active writers must synchronize both columns atomically (for example in one UPDATE), or use a carefully designed compatibility trigger. Complete and verify the backfill only after old single-column writers have retired; otherwise they can leave the new column stale after it was copied. During rollback, preserve that synchronization.

The expansion and migration stages should support both old and new code. Contraction deliberately removes compatibility: drop the old column only after old binaries and the rollback window have retired. A destructive drop is not automatically reversible.

### Practical details

- **Avoid locking DDL** on large tables. In PostgreSQL, adding a nullable column is a metadata-only change, and since version 11 so is adding one with a constant (non-volatile) default. Many type changes rewrite the table under an exclusive lock; binary-compatible changes can avoid a rewrite. Where applicable, `CREATE INDEX CONCURRENTLY` avoids blocking ordinary writes, but can wait on transactions and leave an invalid index after failure; it cannot run inside a transaction block. For MySQL, tools like gh-ost and pt-online-schema-change copy the table in the background.
- **Beware lock queues.** Even an instant `ALTER TABLE` needs a brief exclusive lock. If a long-running query holds a conflicting lock, the `ALTER` waits, and every new query on the table queues behind it. Set a short `lock_timeout` (e.g. a few seconds) and retry, rather than stalling the whole table.
- **Backfill in batches** (say 10,000 rows at a time, throttled on replica lag), not one giant `UPDATE` that holds locks and floods replication.
- **Never drop in the same release** that stops using a column; wait until no running version references it, and keep a backup.
- Run migrations as a separate, observable step, not on application start-up from every instance at once.

This SQL fragment uses named parameters supplied by a migration runner. It demonstrates a bounded, repeatable update; the runner selects ranges, commits batches and throttles from measured replica lag. It assumes the writer-synchronisation prerequisites above.

```sql
-- Keep each transaction to one chosen
-- range.
UPDATE users
SET display_name = fullname
WHERE id BETWEEN :lo AND :hi
  -- Preserve already populated new values.
  AND display_name IS NULL;
-- Runner sleeps if replica lag exceeds 1s.
```

## Key takeaways

- Add compatible schema, retire old writers, verify synchronised backfill, switch readers and contract only after rollback retirement.
- Metadata-only DDL still takes locks; bound lock waits and inspect concurrent-index failure states.
- Batch and observe migrations in one coordinated pipeline step rather than racing every instance at start-up.

## Further reading

- [Ensuring rollback safety during deployments (AWS Builders' Library)](https://aws.amazon.com/builders-library/ensuring-rollback-safety-during-deployments/)
- [Parallel change (Martin Fowler)](https://martinfowler.com/bliki/ParallelChange.html)
- [Release engineering (Google SRE book)](https://sre.google/sre-book/release-engineering/)
- [PostgreSQL ALTER TABLE](https://www.postgresql.org/docs/current/sql-altertable.html)
- [PostgreSQL CREATE INDEX](https://www.postgresql.org/docs/current/sql-createindex.html)
- [PostgreSQL explicit locking](https://www.postgresql.org/docs/current/explicit-locking.html)
