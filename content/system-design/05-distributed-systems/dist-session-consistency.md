---
id: dist-session-consistency
title: Session guarantees users can notice
level: intermediate
minutes: 3
summary: Prevent vanished edits and backwards reads with version-aware session routing.
sourceLesson: dist-consistency-models
---

Eventual convergence can still make an edit appear to vanish on the next page refresh. Session guarantees add promises that follow a particular client without globally ordering every operation.

## Session guarantees

Pure eventual consistency produces anomalies users notice immediately. Terry et al. (Bayou, 1994) defined four **session guarantees** that fix the worst of them cheaply, per client session:

| Guarantee | Promise |
|---|---|
| Read-your-writes | You see your own writes |
| Monotonic reads | You never see time go backwards |
| Monotonic writes | Your writes apply in order |
| Writes-follow-reads | Writes after a read are ordered after it |

### Read-your-writes

A user edits their profile, the page reloads from a lagging replica, and the edit has "vanished". They edit again. Read-your-writes prevents this.

Implementations:

- Read from the authoritative leader for relevant data, or track a confirmed replication position. Routing to the leader for 60 s is only a heuristic unless replica lag is bounded below that interval.
- The client remembers the log position (LSN / timestamp) of its last write; a replica serves the read only if it has caught up past that point.

### Monotonic reads

```
User refreshes comments twice:
  read 1 -> replica R1 (up to date)
            shows 10 comments
  read 2 -> replica R2 (lagging)
            shows 8 comments  <- went back
```

Fix: pin each user to a replica whose history never rolls back; when moving replicas, carry the last-seen version and wait for that version. Tracking versions is necessary across failover or rollback.

> [!tip] Session guarantees are cheap
> They need only per-client metadata, not global coordination. Cross-device sessions are harder: the phone doesn't know what the laptop wrote unless the token is shared via the server.

## Choosing a model

| Need | Model |
|---|---|
| Locks, leader, unique IDs | Linearizable |
| Comments, chat threads | Causal |
| Own profile edits | Read-your-writes |
| Like counts, view counts | Eventual |

A common pattern is to mix them: strong consistency for a small core (account balances, inventory reservation) and weaker models everywhere else.

> [!warning] Check the claims
> Jepsen has repeatedly found databases that advertise strong consistency but violate it under partitions or clock skew. Treat vendor claims as hypotheses and look for independent testing.

## Key takeaways
- Read-your-writes, monotonic reads, monotonic writes and writes-follow-reads protect a client session.
- Carry confirmed replication positions across replica moves and failover; timed leader pinning alone is a heuristic.
- Cross-device sessions need shared metadata, and applications can choose stronger models only for their critical data.

## Further reading
- [Original session guarantees paper (Terry et al.)](https://www.cs.cornell.edu/courses/cs734/2000FA/cached%20papers/SessionGuaranteesPDIS_1.html)
- [Consistency models map (Jepsen)](https://jepsen.io/consistency)
- [Causal consistency (Jepsen)](https://jepsen.io/consistency/models/causal)
- [Please stop calling databases CP or AP (Kleppmann)](https://martin.kleppmann.com/2015/05/11/please-stop-calling-databases-cp-or-ap.html)
