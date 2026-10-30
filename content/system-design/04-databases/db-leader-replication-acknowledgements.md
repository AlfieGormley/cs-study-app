---
id: db-leader-replication-acknowledgements
title: Leader replication and acknowledgements
level: intermediate
minutes: 4
summary: Compare physical and logical replication and distinguish durable standby acknowledgement from applied visibility.
sourceLesson: db-replication
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

- **Physical log shipping**: the raw WAL bytes (Postgres streaming replication). Replays physical page changes, so leader and follower need compatible formats and the same major version, and you can't replicate just one table.
- **Logical (row-based) replication**: "row X in table Y changed to Z" (MySQL row-based binlog, Postgres logical replication). Works across major versions (so it's a common way to upgrade with little downtime), can replicate a subset of tables, and is usable for change data capture into Kafka.
- **Statement-based**: replay the SQL. Some non-deterministic expressions and unordered operations are unsafe; MySQL explicitly handles `NOW()` using logged timestamp context, so it is not inherently unsafe. Row-based logging avoids many of these replay hazards.

## Synchronous vs asynchronous

**Synchronous**: the leader waits for a follower to confirm it has the write before telling the client "committed". **Asynchronous**: the leader acknowledges after its local commit conditions without waiting for a replica acknowledgement. Streaming can already be sending changes while the transaction runs.

| | Synchronous | Asynchronous |
|---|---|---|
| Data loss on leader failure | None if a durable acknowledged copy survives and is promoted | Recent writes may be lost |
| Write latency | Waits for required remote acknowledgement | No required replica acknowledgement |
| Follower down | Stalls if too few required acknowledgements remain | Can continue subject to resources and policy |

> [!analogy] Real-world analogy: filing a signed contract
> A solicitor receives a signed contract. In one office, the clerk files it, tells the client "done", and posts a copy to the branch office later that day. In another, the clerk waits for the branch office to phone and confirm it has filed its copy before telling the client.
>
> **How it maps:** The main office is the leader, the branch office is a follower, and "done" is the commit acknowledgement. The first office is asynchronous replication: if it burns down before the post goes, the client was told "done" but the only copy is lost. The second is synchronous: slower, but a confirmed copy exists elsewhere.
>
> **Where it stops:** Real replication streams changes continuously rather than in a daily post, and "confirmed" has degrees (received, flushed to disk, or applied and visible). After a fire, safety also depends on promoting the branch that actually holds the copy.

Fully synchronous to *every* follower is fragile: any slow replica stalls all writes. PostgreSQL supports quorum synchronous replication, for example `ANY 1 (s1, s2)`. MySQL semi-sync is a separate protocol with its own acknowledgement and timeout/fallback behavior. Aurora’s six-copy storage design uses a four-copy write quorum and three-copy recovery quorum; this does not mean every ordinary SQL read waits for three storage nodes.

"Synchronous" also has degrees. Postgres's `synchronous_commit` decides what the leader waits for:

| Setting | Standby has... |
|---|---|
| `remote_write` | Written to its filesystem, possibly only in OS cache |
| `on` | Flushed it to disk |
| `remote_apply` | Applied it; visible to reads |

With `on` (the default once a sync standby is configured), a committed write is safe on the standby's disk but may not be *visible* there yet. Only `remote_apply` gives read-your-writes from that standby, at extra latency.

> [!warning] Async means "committed" can be lost
> With async replication, if the leader dies 200 ms after confirming a write that hasn't shipped yet, and a follower is promoted, that write is gone. Whatever your users were told.

## Plan a logical-replication cutover

For a major-version upgrade, check schema and type compatibility, initialise the target and stream changes before the switch. Logical replication does not automatically copy every object: schema definitions and sequence state need separate handling. Rehearse the write pause, catch-up check and client switch; logical replication alone does not guarantee a particular downtime.

## Key takeaways
- One leader orders writes; physical and logical replication carry different information.
- Synchronous durability requires the right surviving acknowledged history at failover.
- PostgreSQL on waits for standby flush; remote_apply also waits for replay visibility.

## Further reading
- [www.postgresql.org: warm standby](https://www.postgresql.org/docs/current/warm-standby.html)
- [www.postgresql.org: runtime config wal](https://www.postgresql.org/docs/current/runtime-config-wal.html)
- [www.postgresql.org: logical replication restrictions](https://www.postgresql.org/docs/current/logical-replication-restrictions.html)
- [MySQL: Replication](https://dev.mysql.com/doc/refman/8.4/en/replication.html)
