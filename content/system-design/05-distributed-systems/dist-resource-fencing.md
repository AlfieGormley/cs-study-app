---
id: dist-resource-fencing
title: Fencing stale holders at the resource
level: advanced
minutes: 3
summary: Reject old lock epochs with monotonically increasing tokens and a consistent resource-side check.
sourceLesson: dist-leases-locks
---

A lease holder cannot reliably prove it is still current after a pause. Fencing moves that decision to the resource, which can compare the holder’s epoch with epochs already accepted.

## Fencing tokens

The fix, described in the Chubby paper and popularised by Martin Kleppmann: every time the lock service grants the lock, it also returns a **fencing token**, a number that strictly increases with each grant.

- The client sends the token with every request to the protected resource.
- The resource remembers the highest token it has seen and **rejects** any request with a lower one.

The resource's rule fits on one line:

```formula
T ≥ T_max
where
T: the fencing token attached to the incoming request (a whole number)
T_max: the highest token the resource has accepted so far
≥: greater than or equal to
In words: accept a request only if its token is at least as high as any token already used; then raise the remembered highest token to match.
```

```
A gets lock, token 33
A pauses
lease expires
B gets lock, token 34
B writes (34)  -> storage: max=34 OK
A wakes, writes (33)
               -> storage: 33<34 REJECT
```

Once the resource has accepted a higher token, it rejects lower-token writes. Acquisition alone does not notify the resource: register the new epoch before reading or acting on state when the protocol requires that boundary.

### Where tokens come from

| System | Natural fencing token |
|---|---|
| etcd | Lock key's `create_revision` or `mod_revision` |
| ZooKeeper | Lock-node creation `zxid` |
| Raft/Paxos | Term/ballot for leader epochs |
| Database | A version column updated with each grant |

ZooKeeper sequence numbers and parent `cversion` counters are only ordered within the same surviving parent and before integer wraparound. Recreating the parent or wrapping the counter can reuse or decrease a token; use the lock node's creation `zxid`, or a durable namespace epoch, when those risks apply. Durable token history must also survive service restore: recreating or restoring a token namespace must not restart it below epochs the resource already accepted. A Raft term orders leader epochs, but several application-lock grants in one term need a separate committed grant counter or log index.

Raft's **term** is itself a fencing token for leaders: followers reject `AppendEntries` from a leader with a lower term. That's why stale Raft leaders can't corrupt the log.

### The catch

The resource has to cooperate. A database can do it with a conditional update:

This SQL fragment assumes a `jobs` table with `id`, `owner` and `token` columns, a non-null stored token and no trigger that suppresses matching updates. It changes no row when that row has already accepted a higher token.

```sql
-- Check the token in the same update.
UPDATE jobs
SET owner = 'B', token = 34
WHERE id = 7 AND token <= 34;
-- Zero affected rows means no match.
```

The `<=` lets the current holder write repeatedly with the same token, while any lower (stale) token matches no rows. Check the affected row count: zero means no row matched. If the job exists and its token is non-null, a higher stored token means you've been fenced off.

The check must also happen in **one consistent place**. If the "resource" is three asynchronously replicated copies that each track their own highest token, a stale write can still succeed on a copy that hasn't yet seen the newer token. A single leader or a linearizable conditional write does the job; independent replicas don't.

An arbitrary payment or email API may not accept your fencing token. Some storage APIs offer conditional writes, which must be integrated into the resource protocol. For those, you need idempotency (so a duplicate is harmless) or you must accept the risk.

## Key takeaways
- Each lock grant gets a strictly increasing fencing token, attached to every protected operation.
- The resource rejects tokens below the highest one it has accepted; acquisition alone does not notify it of a new epoch.
- Token checks need one consistent authority, and external APIs without fencing support need another protection such as idempotency.

## Further reading
- [UPDATE and affected-row results (PostgreSQL)](https://www.postgresql.org/docs/current/sql-update.html)
- [How to do distributed locking (Martin Kleppmann)](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html)
- [Leader election in distributed systems (AWS Builders' Library)](https://aws.amazon.com/builders-library/leader-election-in-distributed-systems/)
- [ZooKeeper recipes: locks and leader election](https://zookeeper.apache.org/doc/current/recipes.html)
