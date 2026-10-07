---
id: db-transactions-isolation
title: Transactions and isolation levels
level: advanced
minutes: 18
summary: Dirty reads, non-repeatable reads, phantoms and write skew, and how MVCC, snapshot isolation, 2PL and SSI prevent them.
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

## The SQL standard levels

| Level | Forbids |
|---|---|
| Read Uncommitted | Nothing beyond dirty writes |
| Read Committed | + dirty reads |
| Repeatable Read | + non-repeatable reads |
| Serializable | + phantoms; must be serializable |

The standard defined these in terms of a few anomalies and is famously ambiguous: it doesn't mention lost updates or write skew at all. Real databases use the same names for quite different things.

### What each database actually gives you

**PostgreSQL** (default Read Committed):

- Read Uncommitted behaves exactly like Read Committed; Postgres never shows dirty data.
- Read Committed takes a new snapshot per statement.
- Repeatable Read is **snapshot isolation**. Unlike the standard's minimum, it also prevents phantoms, and it aborts a transaction that tries to update a row someone else changed after its snapshot. Write skew is still allowed.
- Serializable is **SSI**, truly serializable (since 9.1).

**MySQL InnoDB** (default Repeatable Read):

- Read Uncommitted really does allow dirty reads.
- Repeatable Read is a hybrid. Plain `SELECT`s read from a snapshot taken at the first read. But `UPDATE`, `DELETE` and locking reads (`FOR UPDATE`, `FOR SHARE`) read the *latest committed* row and take next-key (row plus gap) locks.
- There's no first-committer-wins check, so a read-then-write race silently loses an update, and write skew is possible.
- Serializable is Repeatable Read with plain `SELECT`s turned into `SELECT ... FOR SHARE` (when autocommit is off): lock-based, effectively 2PL.

**Oracle** (default Read Committed):

- Offers only Read Committed and Serializable (plus a Read Only mode). There is no Read Uncommitted or Repeatable Read.
- Its Serializable is **snapshot isolation**: it raises `ORA-08177` on a write-write conflict but allows write skew, so it isn't truly serializable.

**SQL Server** (default Read Committed, implemented with short read locks unless `READ_COMMITTED_SNAPSHOT` is on, which it is by default in Azure SQL Database) offers a separate `SNAPSHOT` level that is snapshot isolation, and a Serializable level that uses key-range locks (2PL).

> [!warning] Names lie
> "Repeatable Read" means snapshot isolation in Postgres and a snapshot-plus-locking hybrid in MySQL; "Serializable" means SSI in Postgres and snapshot isolation in Oracle. Always check what your database's level actually prevents. Jepsen's analyses have repeatedly found databases that didn't deliver the isolation they advertised.

## MVCC: how reads avoid blocking

**Multi-version concurrency control** keeps several versions of each row. A writer creates a new version rather than overwriting, so readers can carry on reading the old one. *Plain snapshot reads avoid row-level reader/writer blocking.* Table locks, explicit locking reads and DDL can still block.

In Postgres each row version has `xmin` (the transaction that created it) and `xmax` (the one that deleted or replaced it). A transaction's **snapshot** records which transactions had committed when it started; a version is visible if its `xmin` committed before the snapshot and its `xmax` didn't.

```
row id=1 versions:
 [xmin=100 xmax=205 bal=100]
 [xmin=205 xmax=  - bal= 50]
snapshot taken before tx 205
committed → sees bal=100
```

Old versions are garbage-collected later: by `VACUUM` in Postgres, and purge of undo logs in InnoDB. An old retained snapshot or transaction-id horizon can delay cleanup and cause **bloat**; merely issuing BEGIN without acquiring such a horizon is not sufficient.

- **Read Committed** takes a new snapshot per *statement*.
- **Snapshot isolation / Repeatable Read** takes one snapshot per *transaction* (in Postgres, at its first non-transaction-control statement, not at BEGIN).

## Snapshot isolation

Under SI, a transaction sees a consistent snapshot as of its start, and its own writes. On write-write conflicts, **first committer wins**: if T2 tries to update a row that T1 updated and committed after T2's snapshot was taken, T2 aborts. In Postgres, T2 first waits on T1's row lock; if T1 commits, T2 fails with `could not serialize access due to concurrent update`, and if T1 rolls back, T2 carries on.

SI prevents dirty reads, non-repeatable reads, read skew, most phantoms, and lost updates on the same row. It **does not prevent write skew**, because the conflict check only looks at rows both transactions *wrote*.

## Fixing races without full serializability

```sql
-- Atomic update: no read-modify-write gap
UPDATE counters SET n = n + 1 WHERE id = 7;

-- Explicit lock on the rows you depend on
BEGIN;
SELECT * FROM doctors
 WHERE shift_id = 3 AND on_call
 FOR UPDATE;
-- count, decide, then:
UPDATE doctors SET on_call = false
 WHERE id = 'alice';
COMMIT;

-- Constraints the database enforces
CREATE UNIQUE INDEX
  ON bookings(room_id, slot);
```

`FOR UPDATE` turns the read into a locking read: Bob's transaction blocks until Alice commits. Under Read Committed it then re-checks the rows and sees that Alice is now off call; under Repeatable Read it fails with a serialization error and retries. Either way, the invariant holds. It fixes write skew only when the rows you depend on already exist. For "check that nothing exists, then insert" phantoms, you need a unique constraint, a materialised lock row, or serializable isolation.

## Serializable, method 1: two-phase locking

**2PL** was the standard way for decades (still used by SQL Server's Serializable and MySQL's Serializable mode).

1. **Growing phase**: acquire locks as you go. Reads take *shared* locks; writes take *exclusive* locks. Readers block writers and writers block readers.
2. **Shrinking phase**: after releasing a lock, acquire no new locks. Strict 2PL retains exclusive write locks until commit/abort; retaining all shared and exclusive locks until then is often called rigorous 2PL.

To stop phantoms, it locks *ranges* too: **predicate locks** or, more practically, **index-range (next-key) locks**.

Costs: much lower concurrency, long waits behind slow transactions, and **deadlocks** (T1 holds A and wants B; T2 holds B and wants A). The database detects the cycle and aborts one transaction, which the application must retry.

## Serializable, method 2: SSI

**Serializable Snapshot Isolation** (Cahill et al., 2008; in Postgres since 9.1) is *optimistic*. Transactions run on snapshots without blocking, and the database tracks read/write dependencies:

- It records what each transaction read (using SIREAD markers on rows and index ranges, not blocking locks).
- If T1 read something T2 later wrote (an rw-antidependency), and a *dangerous structure* of two such consecutive edges appears, one transaction is aborted, often at commit but sometimes at an earlier statement.

In the doctors example, each transaction read the set the other wrote, so one of them fails with a serialization error and must retry. On retry it sees only one doctor on call and refuses.

SSI can produce *false positives*: it tracks reads coarsely (a whole page or relation if many rows are read), so it sometimes aborts transactions that would have been fine. Proper indexes help, because they let it track narrower index ranges instead of whole tables.

| | 2PL | SSI |
|---|---|---|
| Approach | Pessimistic | Optimistic |
| Readers block? | Yes | No |
| Failure mode | Waits, deadlocks | Aborts, retries |
| Best when | High contention | Low contention |

> [!tip] Retries are part of the contract
> Under Serializable (and even SI), any transaction can fail with a serialization error (SQLSTATE `40001`). Wrap transactions in a retry loop with backoff, and keep them short and free of side effects such as sending emails.

Serializability on a single node is a different property from linearizability across replicas; that distinction, and distributed transactions, are covered in the consistency module.

## Key takeaways
- Know the anomalies: dirty reads, non-repeatable reads, lost updates, phantoms and write skew.
- MVCC lets readers see a snapshot without blocking writers; Read Committed snapshots per statement, SI per transaction.
- Snapshot isolation prevents most anomalies but not write skew; fix it with `FOR UPDATE`, constraints, or Serializable.
- 2PL achieves serializability pessimistically with locks (and deadlocks); SSI does it optimistically by aborting dangerous transactions.
- Level names vary between databases: Postgres Repeatable Read and Oracle Serializable are both snapshot isolation, and MySQL Repeatable Read mixes snapshot reads with locking writes. Check what yours actually guarantees, and always be ready to retry.

## Further reading
- [PostgreSQL: Transaction isolation](https://www.postgresql.org/docs/current/transaction-iso.html)
- [Wikipedia: Snapshot isolation](https://en.wikipedia.org/wiki/Snapshot_isolation)
- [Wikipedia: Two-phase locking](https://en.wikipedia.org/wiki/Two-phase_locking)
- [Ports and Grittner: Serializable Snapshot Isolation in PostgreSQL](https://arxiv.org/abs/1208.4179)
- [Jepsen: Consistency models](https://jepsen.io/consistency)
- [MySQL: Transaction isolation levels](https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-isolation-levels.html)
