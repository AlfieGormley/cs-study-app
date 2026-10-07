---
id: db-replication
title: Replication
level: intermediate
minutes: 16
summary: Single-leader, multi-leader and leaderless replication, sync versus async, replication lag anomalies and failover.
---

**Replication** means keeping copies of the same data on several machines. You do it for three reasons:

- **Availability**: if one machine dies, another can serve.
- **Read scaling**: spread reads across replicas.
- **Latency**: put a copy near users in each region.

Replicating data that never changes is trivial. All the difficulty is in handling *changes*. There are three main designs.

## Single-leader replication

One node, the **leader** (primary), accepts all writes. It sends a stream of changes to **followers** (replicas, standbys), which preserve the required replication semantics; physical replay and parallel logical execution differ. Reads can go to the leader or any follower.

```
   writes      ┌────────┐
 ─────────────►│ Leader │
               └───┬────┘
        change log │ (WAL / binlog)
        ┌──────────┼──────────┐
        ▼          ▼          ▼
   ┌────────┐ ┌────────┐ ┌────────┐
   │Follower│ │Follower│ │Follower│
   └────────┘ └────────┘ └────────┘
        ▲ reads    ▲          ▲
```

This is how Postgres streaming replication, MySQL replication, SQL Server Always On, MongoDB replica sets and Amazon RDS read replicas work. This avoids independent multi-leader histories, but concurrent application transactions can still contend or conflict on the leader.

What gets shipped varies:

- **Physical log shipping**: the raw WAL bytes (Postgres streaming replication). Byte-identical replicas, but leader and follower must run the same major version, and you can't replicate just one table.
- **Logical (row-based) replication**: "row X in table Y changed to Z" (MySQL row-based binlog, Postgres logical replication). Works across major versions (so it's a common way to upgrade with little downtime), can replicate a subset of tables, and is usable for change data capture into Kafka.
- **Statement-based**: replay the SQL. Some non-deterministic expressions and unordered operations are unsafe; MySQL explicitly handles `NOW()` using logged timestamp context, so it is not inherently unsafe. Row-based logging avoids many of these replay hazards.

## Synchronous vs asynchronous

**Synchronous**: the leader waits for a follower to confirm it has the write before telling the client "committed". **Asynchronous**: the leader confirms immediately and ships the change afterwards.

| | Synchronous | Asynchronous |
|---|---|---|
| Data loss on leader failure | None if a durable acknowledged copy survives and is promoted | Recent writes may be lost |
| Write latency | Waits for required remote acknowledgement | No required replica acknowledgement |
| Follower down | Stalls if too few required acknowledgements remain | Can continue subject to resources and policy |

Fully synchronous to *every* follower is fragile: any slow replica stalls all writes. PostgreSQL supports quorum synchronous replication, for example `ANY 1 (s1, s2)`. MySQL semi-sync is a separate protocol with its own acknowledgement and timeout/fallback behavior. Aurora’s six-copy storage design uses a four-copy write quorum and three-copy recovery quorum; this does not mean every ordinary SQL read waits for three storage nodes.

"Synchronous" also has degrees. Postgres's `synchronous_commit` decides what the leader waits for:

| Setting | Standby has... |
|---|---|
| `remote_write` | Received it (in OS memory) |
| `on` | Flushed it to disk |
| `remote_apply` | Applied it; visible to reads |

With `on` (the default once a sync standby is configured), a committed write is safe on the standby's disk but may not be *visible* there yet. Only `remote_apply` gives read-your-writes from that standby, at extra latency.

> [!warning] Async means "committed" can be lost
> With async replication, if the leader dies 200 ms after confirming a write that hasn't shipped yet, and a follower is promoted, that write is gone. Whatever your users were told.

## Replication lag and its anomalies

Async followers are behind the leader by some **replication lag**, usually milliseconds but seconds or minutes under load, during a long-running query on the replica, or after a network blip. This is *eventual consistency*: stop writing and the replicas converge, but at any moment they may be stale.

Long queries on a Postgres replica create a specific tension. If the leader's vacuum removes row versions the replica's query still needs, the replica must either pause replay (lag grows) or cancel the query. By default it waits up to 30 s (`max_standby_streaming_delay`) and then cancels with *conflict with recovery*. `hot_standby_feedback = on` can prevent cleanup-related cancellations (not all recovery conflicts) by telling the leader to keep those versions, at the cost of bloat on the leader.

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

## Failover

When the leader dies, a follower must be promoted.

1. **Detect** the failure, usually by missed heartbeats over some timeout (say 30 s).
2. **Choose** a new leader: ideally the most up-to-date follower. Agreeing on it is a consensus problem.
3. **Reconfigure** clients to write to the new leader (DNS, a proxy, or a service discovery update), and make sure the old leader, if it comes back, becomes a follower.

Tools: Patroni (Postgres, using etcd or Consul for leader election), MySQL Group Replication / Orchestrator, and managed services such as RDS Multi-AZ, whose failover duration depends on the service type, workload, recovery and client reconnection; measure it for the deployment.

What goes wrong:

- **Lost writes**: with async replication, unshipped writes from the old leader are discarded. A lagging promoted replica may reuse identifiers whose earlier values remain in caches or external systems, leading to incorrect associations. A specific historical incident attribution is omitted because this review did not establish its primary report.
- **Split brain**: the old leader isn't dead, just partitioned, and keeps accepting writes. Two leaders now diverge. Enforced fencing prevents stale writes. Leases require reliable enforcement/watchdogs, and epoch tokens work only when every protected resource rejects stale epochs.
- **Timeout tuning**: too short and you fail over during a GC pause or traffic spike (making things worse); too long and you're down for longer.

## Multi-leader replication

Several nodes accept writes, typically **one leader per datacentre**, and replicate to each other asynchronously.

```
 DC London         DC Virginia
┌────────┐ async  ┌────────┐
│Leader A│◄──────►│Leader B│
└───┬────┘        └───┬────┘
 followers         followers
```

Benefits: local write latency in every region, and each datacentre keeps working if the link between them fails. Also the model behind offline-first apps (each device is a "leader") and collaborative editing.

The cost: **write conflicts**. Two users edit the same record in different regions at the same moment; both writes succeed locally, then collide.

Conflict resolution strategies:

- **Last write wins (LWW)**: highest timestamp wins. Simple, but silently drops data, and clock skew decides the "winner".
- **Merge**: e.g. union of shopping cart items, or application callbacks.
- **CRDTs**: data types (counters, sets, text) designed so concurrent updates merge deterministically. Used by Riak, Redis Enterprise active-active, and collaborative-editing libraries such as Automerge and Yjs.
- **Avoid conflicts**: route all writes for a given record to one "home" region.

Examples: MySQL/MariaDB multi-source setups, Postgres with BDR/pgEdge, CouchDB, and DynamoDB global tables (LWW in their default multi-region eventually consistent mode).

## Leaderless replication

Any replica accepts writes. The client (or a coordinator node) sends each write to all **n** replicas and considers it successful when **w** acknowledge; reads query **r** replicas and take the newest value. This is the **Dynamo** style, used by Cassandra, ScyllaDB, Riak and Amazon's original Dynamo.

If `w + r > n` (e.g. n=3, w=2, r=2), every read overlaps at least one replica with the latest write. How quorums behave under failure, and why they're weaker than they look, is covered in the consensus module.

Repairing stale replicas:

- **Read repair**: a read that sees a stale replica writes the newer value back.
- **Hinted handoff**: if a replica is down, another node holds its writes ("hints") and passes them on when it recovers.
- **Anti-entropy**: background comparison with Merkle trees to find and fix differences.

| | Single | Multi | Leaderless |
|---|---|---|---|
| Write conflicts | None | Yes | Yes |
| Failover needed | Yes | Per DC | No |
| Write latency | One region | Local | Quorum |

## Key takeaways
- Single-leader replication is the default: no write conflicts, simple reasoning, but failover is a dangerous moment.
- Synchronous replication avoids data loss at the cost of latency and availability; quorum synchronous and product-specific semi-sync protocols have distinct acknowledgement and fallback guarantees.
- Async lag causes read-your-writes, monotonic-read and consistent-prefix anomalies; fix them with routing and log-position tracking.
- Failover risks lost writes and split brain; it needs fencing and careful timeouts.
- Multi-leader and leaderless replication improve write availability and latency but force you to handle conflicts.

## Further reading
- [PostgreSQL: High availability, load balancing and replication](https://www.postgresql.org/docs/current/high-availability.html)
- [MySQL: Replication](https://dev.mysql.com/doc/refman/8.4/en/replication.html)
- [DeCandia et al.: Dynamo, Amazon's highly available key-value store](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)
- [Wikipedia: Replication (computing)](https://en.wikipedia.org/wiki/Replication_%28computing%29)
- [Wikipedia: Eventual consistency](https://en.wikipedia.org/wiki/Eventual_consistency)
- [PostgreSQL: Replication settings](https://www.postgresql.org/docs/current/runtime-config-replication.html)
