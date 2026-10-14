---
id: db-isolation-anomaly-traces
title: Trace transaction anomalies
level: advanced
minutes: 3
summary: Distinguish dirty reads, lost updates, phantoms and write skew from concrete interleavings.
sourceLesson: db-transactions-isolation
---

The "I" in ACID is the slipperiest letter. Perfect isolation, **serializability**, means concurrent transactions produce the same result as *some* serial order. It's expensive, so databases offer weaker **isolation levels** that allow certain anomalies. Knowing exactly which anomalies your level allows is the difference between correct code and a race condition that only appears under load.

## The anomalies

### Dirty read

Reading data another transaction has written but not committed. If it rolls back, you acted on data that never existed.

### Dirty write

Overwriting another transaction's uncommitted write. Mainstream transactional engines prevent dirty writes, commonly through write locks; the exact mechanism is implementation-specific.

### Non-repeatable read (read skew)

Reading the same row twice in one transaction and getting different values, because someone committed in between.

```
T1: SELECT bal FROM acct WHERE id=1  → 100
T2: UPDATE acct SET bal=50 WHERE id=1
T2: COMMIT
T1: SELECT bal FROM acct WHERE id=1  →  50
```

A backup or report reading many rows across a long transaction sees a mixture of before and after states: totals that never existed at any instant.

### Lost update

Two read-modify-write cycles interleave, and one overwrites the other.

```
T1: read counter = 10
T2: read counter = 10
T1: write counter = 11, COMMIT
T2: write counter = 11, COMMIT  ← one lost
```

### Phantom read

A query's *set* of matching rows changes because another transaction inserted or deleted rows that match the condition. Row locks can't prevent this: the new rows didn't exist to be locked.

### Write skew

Two transactions read the same data, make a decision based on it, then write to *different* rows. Each is fine alone; together they break an invariant.

> [!example] The on-call doctors
> Rule: at least one doctor must be on call. Alice and Bob are both on call, and both feel ill.
> 1. Alice's transaction: `count(on_call) = 2`, so she sets herself off.
> 2. Bob's transaction, concurrently: also sees `2`, sets himself off.
> 3. Both commit. Nobody is on call.
>
> They updated different rows, so no write conflict was detected. This is write skew, and snapshot isolation allows it.

Other examples: double-booking a meeting room, two users claiming the same username via a "check then insert" pattern, overspending a balance split across rows.

## Key takeaways
- Dirty reads use uncommitted data; dirty writes overwrite uncommitted work.
- Repeated reads and separate report statements can observe different committed states.
- Lost updates overwrite a concurrent change; write skew writes different rows and breaks a shared invariant.

## Further reading
- [PostgreSQL: Transaction isolation](https://www.postgresql.org/docs/current/transaction-iso.html)
- [Ports and Grittner: Serializable Snapshot Isolation in PostgreSQL](https://arxiv.org/abs/1208.4179)
