---
id: dist-two-phase-prepare-recovery
title: Two-phase commit preparation and recovery
level: advanced
minutes: 3
summary: Identify the participant and coordinator promises that make a distributed commit atomic.
sourceLesson: dist-transactions
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

The coordinator asks each participant "can you commit?". A participant that says **yes** must first persist enough transaction state or redo information and a prepare record to complete after recovery, and hold its locks. From then on it has **given up the right to abort**: it must commit if told to, even after a crash and restart.

### Phase 2: commit or abort

If every participant voted yes, the coordinator writes **COMMIT** to its own log (this is the **commit point**) and tells everyone. If any voted no or timed out, it writes **ABORT**. The coordinator retries the phase 2 message until every participant acknowledges, forever if necessary.

There are two points of no return: the participant's yes vote and the coordinator's decision log record.

### Recovery: presumed abort

What if the coordinator crashes and, on restart, finds **no** decision record for a transaction? Then it never reached the commit point, so no participant can have been told to commit. It is safe to abort, and the coordinator does so. This convention, **presumed abort**, means the coordinator only needs to force-write COMMIT records; aborts can be logged lazily or not at all.

Participants that crash recover the same way from their own log: no prepare record means they never voted yes and can abort; a prepare record with no outcome means they are in doubt and must ask the coordinator.

## Key takeaways
- Atomic commit requires every participant’s yes vote; a majority vote cannot override a business-level no.
- A participant prepares durably before voting yes and then loses the right to abort independently.
- The coordinator’s durable decision is the commit point; recovery without a decision uses the presumed-abort convention.

## Further reading
- [Two-phase commit protocol (Wikipedia)](https://en.wikipedia.org/wiki/Two-phase_commit_protocol)
- [PREPARE TRANSACTION (PostgreSQL docs)](https://www.postgresql.org/docs/current/sql-prepare-transaction.html)
