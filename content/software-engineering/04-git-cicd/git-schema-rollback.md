---
id: git-schema-rollback
title: Rollback and expand-and-contract migrations
level: advanced
minutes: 3
sourceLesson: git-cd-release
summary: Choose a recovery version that remains compatible with current data and schema.
---

A rollout can put old and new application versions alongside each other. Recovery works only while both versions remain compatible with the data and schema they share.

## Rolling back versus rolling forward

**Rolling back** (deploying the previous artefact) is usually the fastest way to stop an incident and should be routine and rehearsed. **Rolling forward** (shipping a fix) is tempting but slower under pressure, and a hurried fix may have insufficient validation. Choose the tested way to recover that is compatible with the current state.

A rollback is only safe if the previous version can still run against the current state. The usual thing that breaks this is the database.

## Database changes: expand and contract

Code rollback can be faster than reversing state changes, but neither its duration nor safe data recovery is guaranteed. And during a rolling deploy, old and new code run at the same time. So schema migrations must be **backward compatible** at every step. The standard technique is **expand and contract** (also called **parallel change**).

Renaming `customers.name` to `full_name`:

1. **Expand**: add nullable `full_name`. Old code ignores it.
2. **Dual write**: deploy code that writes both columns and still reads `name`.
3. **Backfill**: after all old-only writers have been replaced, copy `name` into `full_name` in batches using concurrency-safe updates. Verify consistency before switching reads.
4. **Switch reads**: deploy code that reads `full_name` (still writing both).
5. **Stop writing** `name`.
6. **Contract**: after all readers and writers have migrated and the rollback window for old code has closed, drop `name`.

Expansion can preserve rollback compatibility, but stopping old-column writes and dropping the column restrict which versions are safe to restore. Check that contract explicitly at each stage. The cost is several deploys spread over days, which is cheap if deploys are routine.

> [!warning] The one-step rename
> `ALTER TABLE customers RENAME COLUMN name TO full_name` deployed with new code breaks every old instance still running mid-rollout, and makes the old code incompatible unless the schema is restored or another compatible recovery path is used.

## Key takeaways

- Choose a recovery version that remains compatible with current data and schema.
- Expand, dual-write, backfill, switch reads, then contract after the compatibility window closes.
- A traffic switch cannot restore a table dropped from a shared database.

## Further reading

- [Parallel change (expand and contract) — martinfowler.com](https://martinfowler.com/bliki/ParallelChange.html)
