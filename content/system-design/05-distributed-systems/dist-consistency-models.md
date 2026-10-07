---
id: dist-consistency-models
title: Consistency models
level: intermediate
minutes: 13
summary: What linearizable, sequential, causal and eventual consistency actually promise, plus the session guarantees users notice.
---

When data is replicated, different clients can see different values at the same moment. A **consistency model** is a contract that says which histories of reads and writes are allowed. Stronger models allow fewer surprising histories, at a cost in latency and availability.

CAP's "C" means one specific model, linearizability. In practice there's a whole spectrum, and choosing the right point on it is one of the most important design decisions you make.

## The hierarchy

From strongest to weakest (these are models for individual reads and writes, not multi-step transactions):

```
   Linearizable
        |
   Sequential
        |
     Causal
```

Each level shown allows every history the level above allows, plus more. Session guarantees form additional, partly independent properties. Eventual convergence is a separate liveness promise and should not be inferred merely from a safety ordering model. Jepsen's map also places transactional models such as serializability alongside these.

## Linearizability

**Linearizability** (also called atomic or strong consistency) means the system behaves as if there were **one copy** of the data, and every operation takes effect **atomically at some instant between its start and its end**.

The key consequence is **recency**: once a write completes, every later read (in real time) must see it or something newer. And once any client has read a new value, no later read anywhere may return the old one.

```
time ------------------------------->
A: |--write x=1--|
B:                 |--read x--| -> 1
C:   |------read x------|        -> 0 or 1
```

C's read overlaps A's write, so either answer is fine. B's read starts after the write finished, so it **must** return 1.

### A violation

```
A: |--------write x=1--------|
B:    |-read-| -> 1
C:              |-read-| -> 0   ILLEGAL
```

B saw the new value; C started *after* B finished, yet saw the old one. That's what happens with naive async replication: B hit an up-to-date replica, C hit a lagging one.

### Composability

Linearizability is **local** (Herlihy and Wing call it *composable*): if every individual object is linearizable, the system as a whole is linearizable. You can shard keys across independent linearizable groups and still reason about each one alone. Sequential consistency does **not** compose: two objects that are each sequentially consistent can together produce a history that no single order explains.

### Where you need it

- **Leader election and locks**: everyone must agree who holds the lock.
- **Uniqueness constraints**: two users can't both claim username `alice`.
- **Cross-channel timing**: a user uploads a file, then a message on a queue tells a worker to process it. If the worker reads a stale replica, the file "doesn't exist".

### What it costs

Linearizability needs coordination (a single leader with synchronous confirmation, or consensus). Every read and write must reach a majority or the leader, so latency includes at least one round trip to them. During a partition, the minority side must stop serving. That's CAP, and PACELC's "else latency" is the cost even without partitions.

> [!note] Linearizable vs serializable
> **Serializability** is about *transactions* over many objects: the result equals *some* serial order, which needn't match real time. **Linearizability** is about *single operations* respecting real time. Having both is called **strict serializability**. Spanner (which calls it external consistency) and FoundationDB provide it; CockroachDB provides serializability with somewhat weaker real-time guarantees.

## Sequential consistency

**Sequential consistency** (Lamport, 1979) requires that all operations appear in *some* single total order that is consistent with **each client's program order**, but not necessarily with real time.

So in the violation diagram above, if B and C are different clients with no communication, sequential consistency could allow it (order: C reads 0, A writes 1, B reads 1). What it forbids is a single client seeing time go backwards, or two clients disagreeing about the order of two writes.

It's mostly of interest for CPU memory models and as a stepping stone. ZooKeeper is a real-world example of something close to it: writes are linearizable, but a read served by a follower may be stale, while each client still sees updates in one agreed order.

### Telling the three apart

The names are easy to mix up, so compare them on two questions: what do they cover, and do they respect real time?

| Model | Covers | Real time? |
|---|---|---|
| Linearizable | Single operations | Yes |
| Sequential | Single operations | No, only per-client order |
| Serializable | Multi-object transactions | No |
| Strict serializable | Transactions | Yes |

A quick test: if a history only looks wrong when you compare *wall-clock* times across different clients, it can still be sequentially consistent or serializable, but it isn't linearizable or strictly serializable.

## Causal consistency

**Causal consistency** only orders operations that are **causally related**. If operation A could have influenced operation B (B happened after reading A's result, or they're in the same session), everyone must see A before B. **Concurrent** operations can be seen in different orders by different nodes.

```
Alice: post "I lost my job"
Alice: post "Never mind, got a new one!"
Bob reads 2nd post, replies "Congrats!"

Causal: nobody sees "Congrats!" before
        the post it replies to.
```

Without causal consistency, Carol might see Bob's "Congrats!" before Alice's posts arrive, or see the posts in reverse, which reads as Bob celebrating a sacking.

Causal consistency is, in effect, the **strongest model that remains available during partitions**: each side keeps working and merges causal histories later. (Strictly, Mahajan et al. proved this for a slight strengthening called real-time causal, and it needs *sticky* availability, where each client keeps talking to the same replica.) Systems track causality with version vectors or dependency metadata; MongoDB offers causally consistent sessions.

## Eventual consistency

**Eventual consistency** promises only that if writes stop, all replicas *eventually* converge to the same value. It says nothing about what you read in the meantime: stale values, values going backwards, writes out of order.

It's what you get from Dynamo-style stores with low quorum settings, DNS, and asynchronous read replicas. It is cheap and highly available, and fine for things like like-counts and product views. But "eventually" has no bound, and convergence needs a conflict-resolution rule (lesson 8).

Some systems offer **bounded staleness** in between: reads may lag, but by no more than a stated time or number of versions (Azure Cosmos DB offers this as a named level). That is stronger than eventual, because it gives a bound, but weaker than linearizable.

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
- A consistency model defines which read/write histories are allowed; stronger means fewer anomalies but more coordination.
- Linearizability = one copy, real-time order. Needed for locks, leader election and uniqueness; it costs latency and partition availability.
- Sequential consistency keeps per-client order but not real time; causal consistency orders only causally related operations.
- Linearizability composes across objects (you can shard it); sequential consistency doesn't.
- Causal consistency can preserve availability for clients that remain on a suitable replica (sticky availability); arbitrary client migration during a partition can require waiting for dependencies.
- Eventual consistency only promises convergence; add session guarantees (read-your-writes, monotonic reads) to avoid user-visible anomalies.
- Serializability (transactions) and linearizability (real-time single operations) are different; both together is strict serializability.

## Further reading
- [Consistency models map (Jepsen)](https://jepsen.io/consistency)
- [Linearizability (Jepsen)](https://jepsen.io/consistency/models/linearizable)
- [Causal consistency (Jepsen)](https://jepsen.io/consistency/models/causal)
- [Sequential consistency (Jepsen)](https://jepsen.io/consistency/models/sequential)
- [Strict serializability (Jepsen)](https://jepsen.io/consistency/models/strict-serializable)
- [Linearizability versus serializability (Peter Bailis)](https://www.bailis.org/blog/linearizability-versus-serializability/)
- [Please stop calling databases CP or AP (Kleppmann)](https://martin.kleppmann.com/2015/05/11/please-stop-calling-databases-cp-or-ap.html)
