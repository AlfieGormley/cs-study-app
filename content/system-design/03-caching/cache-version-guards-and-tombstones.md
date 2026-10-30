---
id: cache-version-guards-and-tombstones
title: Reject older cache writes with version guards
level: intermediate
minutes: 3
summary: Use an atomic version comparison, then explain why deletion needs retained metadata or tombstones.
sourceLesson: cache-invalidation
---

An incoming cached value can carry the database revision it represents. Compare that revision atomically so delayed writers cannot replace a newer cached revision.

## Versioning

Store a version with each cached value (a database-ordered row version or other strictly increasing per-record revision). Only allow a cache write if its version is **strictly greater** than the version already cached; otherwise reject it and keep the stored value. If nothing is cached, there is no stored version to beat, so the write is accepted.

In the earlier concurrent-writer race, suppose B's write carries version 8 and A's late-arriving write carries version 7. When A's arrives, 7 is not greater than 8, so it is rejected. The check has to run atomically inside Redis, which is why it is a Lua script rather than a read followed by a write from the application:

The Python assignment defines a Lua script for an application adapter to execute in Redis; it prints nothing by itself. The Lua return values report whether the cache changed.

```python
# Atomic "set if newer" (Redis Lua)
SET_IF_NEWER = """
-- Compare and write in one atomic call.
local cur = redis.call('HGET', KEYS[1], 'v')
if cur and
   tonumber(cur) >= tonumber(ARGV[1]) then
  -- Zero means old or equal: no change.
  return 0
end
-- One means the newer version was stored.
redis.call('HSET', KEYS[1],
  'v', ARGV[1], 'data', ARGV[2])
redis.call('EXPIRE', KEYS[1], ARGV[3])
return 1
"""
```

The script assumes whole-number versions small enough to compare exactly (Lua's `tonumber` uses floating point, which is exact for whole numbers up to about 9 quadrillion) and version metadata that is still present when the late write arrives. With these assumptions, Race 1 is fixed: A's late write of version 7 is rejected because B already wrote version 8. Versioning alone does not fix Race 2 after a delete, because the key is empty and any version is "newer" than nothing. A tombstone can retain the new version floor, but its comparison metadata must survive until older fills are impossible or rejected by another authority. Expiry/eviction loses that protection. A tombstone-aware script must permit equal-version data to replace that tombstone; the simple strict-greater script shown above does not do so.

A different form of versioning is **versioned keys**: include a version in the key name, such as `user:42:v8`. The writer bumps the version (stored somewhere cheap); readers build the key from the current version, and old keys simply age out via TTL. Fingerprinted asset URLs are the HTTP version of this.

## Key takeaways
- An atomic strictly-newer comparison fixes out-of-order updates when database-ordered revisions and comparison metadata survive.
- An empty key has no revision floor: expiry, eviction or deletion removes the protection.
- A tombstone must retain the revision floor and permit equal-version data to replace it; the simple script shown needs that extension.

## Further reading
- [Scaling Memcache at Facebook — full paper PDF](https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf)
- [Redis Lua scripting](https://redis.io/docs/latest/develop/programmability/eval-intro/)
- [Client-side caching and invalidation — Redis](https://redis.io/docs/latest/develop/use/client-side-caching/)
