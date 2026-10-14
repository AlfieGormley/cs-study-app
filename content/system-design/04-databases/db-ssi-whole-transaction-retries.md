---
id: db-ssi-whole-transaction-retries
title: SSI and whole-transaction retries
level: advanced
minutes: 3
summary: Use optimistic dependency tracking and bounded retries without repeating external side effects.
sourceLesson: db-transactions-isolation
---

PostgreSQL Serializable adds dependency tracking to snapshots. It can reject a transaction whose decisions conflict with another, so the application must make retries part of its normal control flow.

## Serializable, method 2: SSI

**Serializable Snapshot Isolation** (Cahill et al., 2008; in Postgres since 9.1) is *optimistic*. Plain snapshot reads avoid row-level reader/writer blocking, and the database tracks read/write dependencies. Ordinary write locks, explicit locking reads and table locks can still cause waits or deadlocks:

- It records what each transaction read (using SIREAD markers on rows and index ranges, not blocking locks).
- If T1 read something T2 later wrote (an rw-antidependency), and a *dangerous structure* of two such consecutive edges appears, one transaction is aborted, often at commit but sometimes at an earlier statement.

In the doctors example, each transaction read the set the other wrote, so one of them fails with a serialization error and must retry. On retry it sees only one doctor on call and refuses.

SSI can produce *false positives*: it tracks reads coarsely (a whole page or relation if many rows are read), so it sometimes aborts transactions that would have been fine. Proper indexes help, because they let it track narrower index ranges instead of whole tables.

| | 2PL | SSI |
|---|---|---|
| Approach | Pessimistic | Optimistic |
| Plain read row locks? | Yes | No |
| Failure mode | Waits, deadlocks | Aborts, retries |
| Best when | High contention | Low contention |

> [!tip] Retries are part of the contract
> Under Serializable (and even SI), any transaction can fail with a serialization error (SQLSTATE `40001`). Wrap transactions in a retry loop with backoff, and keep them short and free of side effects such as sending emails.

Serializability on a single node is a different property from linearizability across replicas; that distinction, and distributed transactions, are covered in the consistency module.

## A retry is a new transaction

Roll back after SQLSTATE 40001, then rerun the complete read-and-write logic with a fresh snapshot. Bound the attempts and surface exhaustion instead of silently dropping the operation. Atomic database work can be retried; an external email cannot be rolled back, so use an outbox and a downstream idempotency protocol when such an effect is needed.

## Key takeaways
- SSI tracks read/write dependencies using non-blocking SIREAD markers.
- A serialization failure requires rerunning the entire transaction in a fresh snapshot.
- Keep external effects out of retry bodies and use durable handoff with downstream idempotency.

## Further reading
- [Ports and Grittner: Serializable Snapshot Isolation in PostgreSQL](https://arxiv.org/abs/1208.4179)
- [www.postgresql.org: mvcc serialization failure handling](https://www.postgresql.org/docs/current/mvcc-serialization-failure-handling.html)
