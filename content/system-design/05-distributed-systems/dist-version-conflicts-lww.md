---
id: dist-version-conflicts-lww
title: Version conflicts and last-write-wins
level: advanced
minutes: 3
summary: Detect concurrent versions and understand when timestamp resolution loses useful updates.
sourceLesson: dist-crdts-gossip
---

Systems that accept writes on several replicas at once (multi-leader, leaderless, offline-first apps, multi-region active-active) will see **concurrent writes** to the same data. They must merge them so that every replica ends up with the same value. The following units cover conflict resolution, then how clusters learn about each other through gossip.

## Detecting conflicts: version vectors

Before you resolve a conflict you need to know one exists. A **version vector** (a vector clock keyed by replica rather than by client) records, for each replica, how many updates from it this version has seen.

```
replica A writes:  {A:1}
replica B writes:  {A:1, B:1}  (saw A's)
replica A writes:  {A:2}       (didn't
                                see B's)
```

Compare `{A:1, B:1}` with `{A:2}`: each is ahead in one entry, so they're **concurrent**. A store like Riak keeps both as **siblings** and returns both to the next reader, who merges them and writes back with a vector that dominates both, `{A:2, B:1}` plus an increment of the coordinating replica’s own entry.

If one vector dominates (at least as large in every entry), the dominated version is simply obsolete and can be discarded.

## Last-write-wins (LWW)

The simplest resolution: attach a timestamp to every write and keep the highest (ties broken by something deterministic, such as replica id). Cassandra does this per column; DynamoDB global tables do it per item in their default, eventually consistent mode.

It's simple and converges, but it **silently loses data**:

- Two concurrent writes: one is discarded, even though both clients got "success".
- With clock skew, a write that happened later can lose to an earlier one with a faster clock.

```
t=10.000 A: cart = [book]   clock +50ms
t=10.020 B: cart = [pen]    clock ok
stored ts: A=10.050, B=10.020
LWW keeps [book]; [pen] lost
```

LWW is fine when writes are naturally immutable (each key written once, e.g. keyed by UUID) or when losing a concurrent update is acceptable (a user's "last seen" time). For anything like a shopping cart, you need a merge.

> [!example] Dynamo's shopping cart
> The Dynamo paper's cart merged siblings by taking the **union** of items. That never loses an add, but a removed item could reappear if a concurrent sibling still contained it. That's exactly the problem the OR-Set solves.

## Key takeaways
- A version vector records replica progress; incomparable vectors identify concurrent siblings to merge.
- A merged version must dominate its inputs and include the new coordinator update.
- Last-write-wins converges by a deterministic winner but can discard concurrent adds or later writes with slower clocks.

## Further reading
- [Version vector (Wikipedia)](https://en.wikipedia.org/wiki/Version_vector)
- [Conflict-free replicated data type (Wikipedia)](https://en.wikipedia.org/wiki/Conflict-free_replicated_data_type)
