---
id: db-replica-lag-read-guarantees
title: Replica lag and read guarantees
level: intermediate
minutes: 3
summary: Diagnose stale and backwards reads and weigh report cancellation against retained-version bloat.
sourceLesson: db-replication
---

A replica can have less recent data than the leader, and two replicas can have different histories applied. Read routing needs to preserve the guarantees the user experience requires.

## Replication lag and its anomalies

Async followers are behind the leader by some **replication lag**, usually milliseconds but seconds or minutes under load, during a long-running query on the replica, or after a network blip. This is *eventual consistency*: stop writing and the replicas converge, but at any moment they may be stale.

Long queries on a Postgres replica create a specific tension. If the leader's vacuum removes row versions the replica's query still needs, the replica must either pause replay (lag grows) or cancel the query. The default 30 s `max_standby_streaming_delay` budgets total replay delay for received WAL, rather than granting every query thirty seconds. A conflicting query may therefore have less grace time before cancellation with *conflict with recovery*. `hot_standby_feedback = on` can prevent cleanup-related cancellations (not all recovery conflicts) by telling the leader to keep those versions, at the cost of bloat on the leader.

Three classic anomalies:

### Reading your own writes

A user updates their profile (leader) and reloads the page (served by a lagging follower). The change seems to have vanished.

Fixes for **read-your-writes** consistency:

- Read data the user can edit from the leader (e.g. their own profile).
- For a short time after a write (say 10 s), route that user's reads to the leader. This is a heuristic unless replication lag is bounded; use log-position tracking for a guarantee.
- Track the log position of the user's last write (Postgres LSN, MySQL GTID) and only read from a replica that has caught up to it.

### Monotonic reads

A user refreshes twice; the first request hits a replica 1 s behind, the second hits one 10 s behind. A comment appears, then disappears. Pinning each user to one advancing replica helps. Across failover or reassignment, carry a minimum observed log position/version and wait for it or use the leader; pinning alone cannot guarantee monotonic reads.

### Consistent prefix reads

In partitioned systems, a reader sees an answer before the question that prompted it, because they were stored on partitions replicating at different speeds. Fix: write causally related data to the same partition, or track causal dependencies.

These guarantees are part of a wider family of consistency models, covered in the consistency module.

## Key takeaways
- Async lag can violate read-your-writes, monotonic reads and consistent prefixes.
- Log-position tracking gives a stronger guarantee than an arbitrary post-write routing window.
- Standby feedback helps cleanup conflicts but can retain dead versions on the primary.

## Further reading
- [PostgreSQL: Hot standby](https://www.postgresql.org/docs/current/hot-standby.html)
- [PostgreSQL: Replication settings](https://www.postgresql.org/docs/current/runtime-config-replication.html)
