---
id: dist-transactions
title: Distributed transactions and sagas
level: advanced
minutes: 15
summary: Two-phase commit and why it blocks, three-phase commit's limits, and sagas with orchestration, choreography and compensating actions.
---

A transaction on one database is atomic: all of its writes happen or none do. Once a business operation spans several databases or services (charge a card, reserve stock, book a courier), you need a way to keep them consistent. There are two broad answers: **atomic commit protocols** that make many participants behave like one transaction, and **sagas** that give up atomicity in favour of compensation.

## The atomic commit problem

Every participant must reach the same decision, **commit** or **abort**, and commit is only allowed if *every* participant voted yes. That differs from consensus, where a majority suffices: here a single "no" (constraint violation, out of stock) must abort everything.

## Two-phase commit (2PC)

2PC uses a **coordinator** (often the application's transaction manager) and **participants** (databases, queues).

```
Coordinator       P1         P2
 |--prepare------->|          |
 |--prepare------------------>|
 |<--yes-----------|          |
 |<--yes----------------------|
 | log COMMIT                 |
 |--commit-------->|          |
 |--commit------------------->|
 |<--ack-----------|          |
 |<--ack----------------------|
```

### Phase 1: prepare

The coordinator asks each participant "can you commit?". A participant that says **yes** must first write all the transaction's changes and a prepare record durably to disk, and hold its locks. From then on it has **given up the right to abort**: it must commit if told to, even after a crash and restart.

### Phase 2: commit or abort

If every participant voted yes, the coordinator writes **COMMIT** to its own log (this is the **commit point**) and tells everyone. If any voted no or timed out, it writes **ABORT**. The coordinator retries the phase 2 message until every participant acknowledges, forever if necessary.

There are two points of no return: the participant's yes vote and the coordinator's decision log record.

### Recovery: presumed abort

What if the coordinator crashes and, on restart, finds **no** decision record for a transaction? Then it never reached the commit point, so no participant can have been told to commit. It is safe to abort, and the coordinator does so. This convention, **presumed abort**, means the coordinator only needs to force-write COMMIT records; aborts can be logged lazily or not at all.

Participants that crash recover the same way from their own log: no prepare record means they never voted yes and can abort; a prepare record with no outcome means they are in doubt and must ask the coordinator.

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

## Sagas

Microservices usually can't (or shouldn't) hold locks across services for the duration of a business process. A **saga** (Garcia-Molina and Salem, 1987) breaks a long transaction into a sequence of **local transactions**, each committed immediately in its own service. If a later step fails, previously completed steps are undone by **compensating transactions**.

```
T1 order    T2 payment   T3 stock
created --> charged ----> reserve FAILS
                              |
C2 refund <-------------------+
C1 cancel order
```

### Compensating actions

A compensation is a *semantic* undo, not a rollback. A refund is not the same as never having charged: the customer may see two lines on their statement. Some actions can't be compensated at all (an email sent, a parcel shipped), so order steps carefully:

1. **Compensatable** steps first (create order in PENDING, reserve stock).
2. The **pivot** step: the point of no return (charge the card).
3. **Retriable** steps after the pivot, which must eventually succeed (send confirmation email, notify warehouse).

Compensations must themselves be **idempotent** and retried until they succeed; if a refund call times out, you retry it.

### Timeouts make it harder

A step that times out has an **unknown** outcome, exactly as in lesson 1. If the orchestrator gives up on "charge card" and starts compensating, the charge might still happen later: the request could be sitting in a queue. So:

- A compensation must be safe to run even if the forward step **never happened** (refunding an unknown charge is a no-op).
- The service should record the compensation, so a forward request that arrives **after** it is rejected rather than applied. Use a shared saga or step identifier for correlation, with distinct idempotency keys for the forward action and compensation; a durable step state machine must reject late forward work after cancellation.
- Where possible, ask the service for the step's status (by idempotency key) before deciding to compensate.

### Orchestration versus choreography

| | Orchestration | Choreography |
|---|---|---|
| Control | Central orchestrator | Services react to events |
| Visibility | Saga state in one place | Spread across services |
| Coupling | Orchestrator knows all | Services know events |
| Best for | Complex, many steps | Short, simple flows |

**Orchestration**: an orchestrator (a state machine, often built on Temporal, AWS Step Functions or Camunda) tells each service what to do and handles failures. The orchestrator's own state must be durable, so a crash mid-saga resumes where it left off; durable-execution engines like Temporal exist largely to provide that.

```
Orchestrator
 |--reserve stock--> Inventory
 |<--ok-------------
 |--charge---------> Payments
 |<--declined-------
 |--release stock--> Inventory
```

**Choreography**: each service publishes events and others subscribe. `OrderCreated` triggers Payments; `PaymentFailed` triggers Inventory to release stock and Orders to cancel. There's no central coordinator, but the flow is implicit and harder to trace or change, and cyclic dependencies creep in.

### Isolation: the saga's weakness

Sagas preserve local transaction guarantees but do not provide global ACID atomicity or isolation; compensation is a later business action, not an invisible rollback. Other transactions see intermediate states: a product shows "reserved" stock for an order that's about to be cancelled, or a balance briefly includes a charge that will be refunded. Anomalies include **lost updates** and **dirty reads** across steps. Countermeasures:

- **Semantic locks**: mark records as PENDING so others treat them carefully.
- **Commutative updates**: design steps so order doesn't matter (increment/decrement).
- **Re-reading values** before acting, or versioning records.

### Reliable messaging

Every step needs "update my database *and* publish an event" atomically, otherwise a crash between them stalls the saga. The standard fix is the **transactional outbox**: write the event to an `outbox` table in the same local transaction, and have a relay (or CDC tool like Debezium) publish it. Consumers must deduplicate, because delivery is at least once.

## Choosing

| Situation | Use |
|---|---|
| Shards of one database | 2PC over consensus groups |
| Few systems, short, need atomicity | 2PC/XA (carefully) |
| Microservices, long-running flow | Saga |
| Can redesign boundaries | Avoid it: one service owns the data |

## Key takeaways
- Atomic commit needs every participant to agree; one "no" aborts all, unlike majority consensus.
- 2PC: prepare (vote yes durably, keep locks) then commit; the coordinator's logged decision is the commit point.
- 2PC blocks if the coordinator fails after participants vote yes; they're in doubt, holding locks. A coordinator that restarts without a decision record presumes abort.
- 3PC avoids blocking only under synchronous assumptions; partitions break it. Real systems run 2PC with consensus-replicated coordinators.
- Sagas replace atomicity with local commits plus compensating transactions; order steps as compensatable, pivot, retriable.
- A timed-out step has an unknown outcome: compensations must handle steps that never ran, and late forward requests must be rejected.
- Orchestration centralises saga logic; choreography uses events. Sagas lack isolation, so use semantic locks and an outbox for reliable events.

## Further reading
- [Two-phase commit protocol (Wikipedia)](https://en.wikipedia.org/wiki/Two-phase_commit_protocol)
- [Three-phase commit protocol (Wikipedia)](https://en.wikipedia.org/wiki/Three-phase_commit_protocol)
- [Sagas (Garcia-Molina and Salem, 1987)](https://www.cs.cornell.edu/andru/cs711/2002fa/reading/sagas.pdf)
- [Saga pattern (microservices.io)](https://microservices.io/patterns/data/saga.html)
- [Saga distributed transactions (Azure Architecture Center)](https://learn.microsoft.com/en-us/azure/architecture/patterns/saga)
- [Compensating Transaction pattern (Azure)](https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction)
- [PREPARE TRANSACTION (PostgreSQL docs)](https://www.postgresql.org/docs/current/sql-prepare-transaction.html)
- [Parallel commits in CockroachDB (Cockroach Labs)](https://www.cockroachlabs.com/blog/parallel-commits/)
