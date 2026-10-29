---
id: sql-postgresql-migration-locks
title: Keep PostgreSQL migration locks short
level: advanced
minutes: 3
sourceLesson: sql-schema-ddl
summary: Metadata changes can still wait for and hold blocking locks.
---

The examples continue the shop database introduced in the first unit. The original products are Kettle £30, Toaster £25, Lamp £40, Rug £90 and Mug £8. 

### PostgreSQL: watch the locks

Most `ALTER TABLE` forms take an `ACCESS EXCLUSIVE` lock, which blocks reads and writes on that table. Whether that matters depends on how long the lock is held:

- **Fast, metadata only:** adding a nullable column, or (since PostgreSQL 11) adding a column with a non-volatile default such as `'std'` or `now()`. This avoids work that grows with the number of rows, but lock waits and catalogue work still determine the elapsed time.
- **Slow, rewrites or scans:** changing a column's type, adding a column with a volatile default such as `clock_timestamp()`, or `SET NOT NULL`, which scans every row to check.

Even a fast `ALTER` can cause an outage. If a long-running query holds a lock on the table, the `ALTER` waits for it, and every new query queues behind the `ALTER`. Set `lock_timeout` (for example `SET lock_timeout = '2s'`) so the migration fails fast and can be retried.

> [!analogy] Real-world analogy: a queue at a shop door
> A shop lets browsers share the floor, but a fitter who needs the shop empty waits at the door. Customers arriving after the fitter queue behind them, even though they could have browsed alongside the one customer still inside.
>
> **How it maps:** The long-running report is the customer inside, holding an `ACCESS SHARE` lock that lets other readers in. The `ALTER TABLE` is the fitter, waiting for an `ACCESS EXCLUSIVE` lock. New queries queue behind the waiting `ALTER`, so the table appears frozen. `lock_timeout` tells the fitter to give up and come back later rather than block the door.
>
> **Where it stops:** Once the fitter gets in, a metadata-only change may take milliseconds, far quicker than a real refit. The outage comes from the waiting, not the work, which is why the timeout matters even for "instant" changes.

For slow changes, split the work so that the long validation phase permits ordinary reads and writes. The short catalogue changes still take locks:

This migration assumes an existing nullable `customers.email` column whose older rows have already been populated. It upgrades that older schema to require email; the completed redesign in the earlier unit already makes email required.

```sql
-- PostgreSQL: validate existing email
-- values.
-- 1. add, not yet checked
ALTER TABLE customers
  ADD CONSTRAINT email_nn
  CHECK (email IS NOT NULL)
  NOT VALID;
-- 2. validate while ordinary writes run
ALTER TABLE customers
  VALIDATE CONSTRAINT email_nn;
-- 3. PG 12+ uses the valid CHECK
--    to skip the scan
ALTER TABLE customers
  ALTER COLUMN email SET NOT NULL;
```

Indexes follow the same idea. Plain `CREATE INDEX` blocks ordinary writes for the whole build. `CREATE INDEX CONCURRENTLY` permits ordinary writes, but requires extra scans and waits, cannot run inside a transaction block, and can leave an `INVALID` index after a failure. Inspect a failed build and normally drop or rebuild the invalid index before retrying.

Renaming or dropping a column that running code still uses breaks that code instantly. The safe pattern is **expand and contract**: add the new column, deploy code that writes both while still reading the old one, and wait until every writer uses that code or a synchronisation trigger covers older writers. Backfill in batches, verify agreement, switch reads, and keep dual writes until every reader has migrated. Only then stop writing and drop the old column in a later release. Switching reads while older writers still update only the original column exposes stale data.

## Key takeaways
- Metadata changes can still wait for and hold blocking locks.
- Use lock_timeout to fail a waiting migration promptly.
- Validate constraints separately and expand-and-contract incompatible column changes.

## Further reading
- [ALTER TABLE — PostgreSQL documentation](https://www.postgresql.org/docs/current/sql-altertable.html)
