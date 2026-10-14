---
id: db-row-locks-race-fixes
title: Row locks, constraints and two-phase locking
level: advanced
minutes: 3
summary: Fix lost updates and missing-row races, then trace the deadlock cost of lock-based serializability.
sourceLesson: db-transactions-isolation
---

Choose the smallest mechanism that protects the decision you make. A SQL increment using the stored value, a lock on existing rows or an enforced uniqueness rule solves different kinds of race.

## Fixing races without full serializability

```sql
-- Atomic update: no read-modify-write gap
UPDATE counters SET n = n + 1 WHERE id = 7;

-- Explicit lock on the rows you depend on
BEGIN;
SELECT * FROM doctors
 WHERE shift_id = 3 AND on_call
 FOR UPDATE;
-- Count locked rows; refuse the last
-- doctor.
-- Continue only when the decision permits
-- it.
UPDATE doctors SET on_call = false
 WHERE id = 'alice';
COMMIT;

-- Enforce one booking per exact room-slot.
CREATE UNIQUE INDEX
  ON bookings(room_id, slot);
```

The fragment assumes existing `counters`, `doctors` and `bookings` tables. It demonstrates three separate techniques; the doctors branch still needs the application decision described below.

`FOR UPDATE` turns the read into a locking read: Bob's transaction blocks until Alice commits. Under Read Committed it then re-checks the rows and sees that Alice is now off call; under Repeatable Read it fails with a serialization error and retries. Either way, the invariant holds. It fixes write skew only when the rows you depend on already exist. For "check that nothing exists, then insert" phantoms, you need a unique constraint, a materialised lock row, or serializable isolation.

## Serializable, method 1: two-phase locking

**2PL** was the standard way for decades (still used by SQL Server's Serializable and MySQL's Serializable mode).

1. **Growing phase**: acquire locks as you go. Reads take *shared* locks; writes take *exclusive* locks. Readers block writers and writers block readers.
2. **Shrinking phase**: after releasing a lock, acquire no new locks. Strict 2PL retains exclusive write locks until commit/abort; retaining all shared and exclusive locks until then is often called rigorous 2PL.

To stop phantoms, it locks *ranges* too: **predicate locks** or, more practically, **index-range (next-key) locks**.

Costs: much lower concurrency, long waits behind slow transactions, and **deadlocks** (T1 holds A and wants B; T2 holds B and wants A). The database detects the cycle and aborts one transaction, which the application must retry.

## The application decision is still required

The doctors example locks the rows, then the application must count the returned on-call doctors and refuse to remove the last one. The SQL fragment assumes that decision permits Alice to leave; it is not a complete invariant-checking stored procedure. The booking index enforces equality of a room and slot, not arbitrary overlapping time ranges.

## Key takeaways
- A single SQL increment removes the application read-modify-write gap.
- Row locks protect existing rows; a uniqueness rule or other mechanism is needed for absent-row races.
- Strict two-phase locking holds write locks until completion and can deadlock.

## Further reading
- [www.postgresql.org: explicit locking](https://www.postgresql.org/docs/current/explicit-locking.html)
- [PostgreSQL: Transaction isolation](https://www.postgresql.org/docs/current/transaction-iso.html)
- [PostgreSQL: Constraints](https://www.postgresql.org/docs/current/ddl-constraints.html)
