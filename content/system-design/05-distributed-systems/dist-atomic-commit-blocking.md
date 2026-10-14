---
id: dist-atomic-commit-blocking
title: Blocking commit and replicated coordinators
level: advanced
minutes: 3
summary: Diagnose in-doubt transactions and understand which failures consensus replication and 3PC can address.
sourceLesson: dist-transactions
---

The preceding unit established what a prepared participant has promised. If the coordinator disappears before that participant learns the decision, preserving the promise can prevent all progress.

### The blocking problem

Suppose a participant has voted yes and the coordinator then crashes before sending the decision.

```
Coordinator     P1           P2
 |<--yes--------|            |
 |<--yes---------------------|
 X crashes
                P1: in doubt
                P2: in doubt
         holding locks...
```

P1 can't commit (maybe P2 voted no). It can't abort (maybe the coordinator logged COMMIT and P2 already committed). Asking P2 doesn't help if P2 is also in doubt. Both must **wait for the coordinator to recover**, holding row locks the whole time. Other transactions touching those rows block too.

This is why 2PC is called a **blocking protocol**: a single coordinator failure can stall participants indefinitely. In practice, operators sometimes resolve in-doubt transactions by hand (Postgres `COMMIT PREPARED` / `ROLLBACK PREPARED`), which risks inconsistency if they guess differently from the coordinator. Postgres disables prepared transactions by default (`max_prepared_transactions = 0`) partly because forgotten ones hold locks and block vacuum.

### Other costs

- At least two round trips and several forced disk writes (`fsync`) per transaction.
- Locks held across a network round trip, which hurts throughput under contention.
- The slowest participant sets the latency.
- **XA** (the cross-vendor 2PC standard) acts as a lowest common denominator; failure handling across heterogeneous systems is notoriously fragile.

> [!note] 2PC on top of consensus
> Spanner and CockroachDB still use 2PC across shards, but each participant and the coordinator are **Raft or Paxos groups**, not single machines. A coordinator "crash" just means its group elects a new leader, which reads the decision from the replicated log. This permits recovery from an individual coordinator failure while its group retains a quorum; losing that quorum or an essential participant can still block progress. CockroachDB's **parallel commits** go further, overlapping the two phases so that a typical distributed transaction commits after a single round of consensus writes.

## Three-phase commit (3PC)

3PC (Skeen, 1981) inserts a **pre-commit** phase so that no participant is ever uncertain while another might have committed:

```
1. canCommit?   -> yes/no
2. preCommit    -> ack
3. doCommit     -> ack
```

After coordinator failure, survivors run a termination protocol that exchanges their states and coordinates a common outcome. A participant that voted yes must not simply abort on its own because its local preCommit message has not arrived; another survivor may already be prepared.

The catch: this reasoning assumes a **synchronous network with bounded delay and perfect failure detection**. Under a partition, a recovery coordinator may be unable to exchange states with all required participants. Treating local timeout alone as authority to commit or abort can produce conflicting decisions; the termination protocol's synchrony and failure assumptions are essential. Because real networks are partially synchronous, 3PC is rarely used. The practical answer is 2PC with a replicated, consensus-backed coordinator.

## Key takeaways
- Prepared participants retain locks while an unknown decision prevents safe commit or abort.
- Replicating coordinators and participants reduces blocking after individual node failures while reachable quorums remain.
- Three-phase commit needs its termination protocol and strong timing assumptions; local timeout decisions are unsafe under partitions.

## Further reading
- [Two-phase commit protocol (Wikipedia)](https://en.wikipedia.org/wiki/Two-phase_commit_protocol)
- [Three-phase commit protocol (Wikipedia)](https://en.wikipedia.org/wiki/Three-phase_commit_protocol)
- [PREPARE TRANSACTION (PostgreSQL docs)](https://www.postgresql.org/docs/current/sql-prepare-transaction.html)
- [Parallel commits in CockroachDB (Cockroach Labs)](https://www.cockroachlabs.com/blog/parallel-commits/)
