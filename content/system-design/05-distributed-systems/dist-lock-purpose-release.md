---
id: dist-lock-purpose-release
title: Lock purpose and atomic release
level: advanced
minutes: 2
summary: Choose an efficiency or correctness lock and avoid deleting a successor’s lease.
sourceLesson: dist-leases-locks
---

The required lock strength depends on the consequence of two actors working at once. Even when duplication only wastes CPU, a stale actor must not erase its successor’s lock.

## Efficiency locks versus correctness locks

Kleppmann distinguishes two purposes:

- **Efficiency**: avoid doing the same work twice (e.g. two workers both regenerating a report). An occasional double run wastes money but is harmless.
- **Correctness**: two holders would corrupt data, double-charge or lose updates.

For efficiency, a simple single-node Redis lock (`SET key token NX PX 10000`) is perfectly fine. For correctness, you need a consensus-backed lock service *and* fencing at the resource.

Even an efficiency lock needs a careful **release**. A plain `DEL key` is wrong: if your lease expired during a pause and someone else acquired the lock, you'd delete *their* lock. Release only if the value is still your random token, atomically, with a small Lua script:

The lock key is `KEYS[1]`; this worker’s random ownership token is `ARGV[1]`. Execute the fragment as one Redis Lua script, so no other command can replace the key between the check and deletion. A return of 1 means this script deleted the key; 0 means it did not.

```lua
-- Delete only the lock we still own.
if redis.call("get", KEYS[1])
   == ARGV[1] then
  return redis.call("del", KEYS[1])
end
-- Expired or replaced: leave it alone.
return 0
```

Partitioning work by key, as Kafka consumer groups do, can reduce the need for per-key distributed locks. Keep each account’s ledger operations ordered, and enforce sequencing or fencing at external storage so a stale consumer cannot reorder writes during a rebalance. Idempotency suppresses repeated operations but does not order different operations.

## Key takeaways
- An efficiency lock avoids duplicated work; a correctness lock protects an invariant that concurrent holders would break.
- Release only when the stored random ownership token still matches, checking and deleting atomically.
- Partitioning work by key can reduce distributed locking, but external writes still need ordering or fencing through rebalances.

## Further reading
- [How to do distributed locking (Martin Kleppmann)](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html)
- [Distributed locks with Redis (Redis docs)](https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/)
