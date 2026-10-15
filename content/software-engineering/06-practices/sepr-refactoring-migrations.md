---
id: sepr-refactoring-migrations
title: Migrate interfaces and legacy systems
level: basic
minutes: 4
summary: Use expand and contract, branch by abstraction and strangler routing to replace systems incrementally.
sourceLesson: sepr-refactoring
---

Tests protect local changes, but public contracts also include callers, schemas, stored formats and operational consumers. Incremental migration keeps compatible versions working together.

## Refactoring code you do not fully control
Renaming a function is easy when you can update every caller in one commit. It is hard when callers live in other services, other teams or other companies.

### Parallel change (expand and contract)

Change an interface in three phases, each safe to deploy on its own:

```
1. Expand    add new_name(); old_name()
             calls it. Both work.
2. Migrate   move callers to new_name()
             one at a time.
3. Contract  delete old_name() once
             nothing calls it.
```

For columns, expand the schema and deploy atomic dual writes while still reading the old column. Drain every old-only writer, including jobs, before a race-safe backfill from the current row values; alternatively use database synchronization that also covers old writers. Validate equality before switching reads. Keep dual writes through the rollback window, then retire all old readers/writers before dropping the old column. Locks, transactions and conditional updates must prevent stale backfill data from overwriting newer values.

### Branch by abstraction

To replace a large internal component (say, an ORM or a payment library) without a long-lived branch:

1. Put an **abstraction layer** (an interface) in front of the old component.
2. Move all callers to use the abstraction.
3. Build the new implementation behind the same abstraction, switched by a flag.
4. Flip callers over gradually, then delete the old implementation and, if it no longer helps, the abstraction.

The aim is to keep changes integrated on the main branch, with each step building and remaining deployable; the pattern does not guarantee this without tests of component compatibility and behaviour.

### Strangler fig

For a whole legacy system, Fowler's **strangler fig** pattern (named after a vine that grows round a tree until it replaces it) routes traffic through a facade. New functionality goes into the new system; old routes are moved across one at a time until the legacy system handles nothing and can be switched off.

```
client -> facade --+--> new service
                   |    (/orders, /users)
                   +--> legacy system
                        (everything else)
```

The big-bang rewrite is the alternative, and it has a poor record: the old system keeps changing while you rebuild it, the rewrite delivers nothing until it is finished, and hidden behaviour in the old code is rediscovered as production bugs.

## Pitfalls
- **Refactoring without tests** is just editing and hoping.
- **Mixing refactoring with behaviour change** in one commit makes review and bisecting much harder. Separate commits, ideally separate PRs.
- **Refactoring for its own sake.** Spend effort where code changes often. A stable module may have little change-related cost, but still assess operational, security and knowledge risks.
- **Big-bang refactors on a long-lived branch** drift from main and end in painful merges. Prefer small steps merged daily.
- **Breaking public contracts.** Anything other code depends on (APIs, serialised formats, database schemas, even log formats parsed by alerts) is behaviour. Use parallel change.
- **Speculative generality.** Refactoring towards a flexibility nobody needs yet adds indirection. Refactor for the change in front of you.

## Key takeaways
- Expand an interface before migrating callers, then contract after all old dependencies are gone.
- Database backfills must account for concurrent and old-version writers, validation and rollback.
- Branch by abstraction replaces a component; strangler routing replaces system capabilities incrementally.

## Further reading
- [Parallel Change — Martin Fowler](https://martinfowler.com/bliki/ParallelChange.html)
- [Branch By Abstraction — Martin Fowler](https://martinfowler.com/bliki/BranchByAbstraction.html)
- [Strangler Fig Application — Martin Fowler](https://martinfowler.com/bliki/StranglerFigApplication.html)
