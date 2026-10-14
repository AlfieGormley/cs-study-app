---
id: api-shared-limiter-atomicity
title: Atomic distributed limiters
level: advanced
minutes: 4
summary: Share limiter state and apply refill and consumption atomically without expiry or clock regressions.
sourceLesson: api-rate-limiting
---

## Distributed rate limiting

With 20 API servers behind a load balancer, a per-server in-memory limiter doesn't work: a client limited to 100/min could get 100 *per server*, or 2,000 in total:

```formula
L_eff = N × L
L_eff = 20 × 100 = 2,000
where
L_eff: the most requests per minute the client can actually get through the fleet
N: the number of servers, each with its own independent counter
L: the limit each server enforces, here 100 per minute
In words: independent limiters don't know about each other, so the real limit is multiplied by the number of servers the client can reach.
```

```
 +----+ +----+ +----+
 |API1| |API2| |API3|
 +--+-+ +--+-+ +--+-+
    \     |     /
     +---------+
     |  Redis  |  shared
     +---------+  counters
```

A common design uses a **shared store** such as Redis for atomic operations and TTLs. Individual command atomicity does not make a multi-command read/modify/write sequence atomic, and failover durability is a separate concern.

## Race conditions

A naïve read-then-write has a race. Two servers both read `tokens = 1`, both allow, both write `tokens = 0`: two requests went through on one token.

Fixes:

- **Atomic commands.** `INCR` is atomic, but the conditional `EXPIRE` must also be protected from a crash between commands, for example by a Lua script. With a separate minute in the key, a missing expiry leaks old keys; with a reused key it can also lock out the client.
- **Lua scripts.** For token bucket, run the whole read-refill-decrement in a Lua script. Redis executes a script atomically, so no other command interleaves.

```lua
-- KEYS[1]=bucket
local C   = tonumber(ARGV[1])
local r   = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
-- Missing state starts as a full bucket.
local b = redis.call('HMGET',
  KEYS[1], 'tokens', 'ts')
local tokens = tonumber(b[1]) or C
local ts = tonumber(b[2]) or now
-- Never move stored time backwards.
now = math.max(now, ts)
-- Refill and cap before spending one token.
tokens = math.min(C,
  tokens + (now - ts) * r)
local ok = tokens >= 1
if ok then tokens = tokens - 1 end
redis.call('HSET', KEYS[1],
  'tokens', tokens, 'ts', now)
-- Expiry must allow a complete refill.
local ttl = math.max(1, math.ceil(C / r))
redis.call('EXPIRE', KEYS[1], ttl)
-- 1 means allowed; 0 means rejected.
return ok and 1 or 0
```

This teaching script assumes a validated finite capacity of at least one token, a positive finite refill rate and a trusted timestamp in seconds. Arbitrary client timestamps must not reach it. Expiry must be no shorter than the time an empty bucket takes to refill completely; otherwise a slow-refilling bucket could expire and incorrectly reset to full:

```formula
T_full = C / r
TTL = max(1, ⌈T_full⌉)
TTL = max(1, ⌈10 / 0.1⌉) = 100 s
where
T_full: the time for an empty bucket to refill to capacity, in seconds (s)
C: the bucket capacity, in tokens
r: the refill rate, in tokens per second
TTL: time to live, how long Redis keeps the key before deleting it, in whole seconds
max: the larger of the two values, so the TTL is never below 1 s
⌈ ⌉: ceiling: round up to the next whole number
s: seconds
In words: keep the key at least as long as a full refill takes; a bucket of 10 refilling at 0.1 tokens per second needs 100 s.
```

Once that time has passed with no requests the bucket would be full anyway, so deleting the key and starting again full gives the same answer.

## Key takeaways
- Independent full-limit counters multiply the reachable fleet quota.
- Atomic commands alone do not protect a multi-command read-modify-write sequence.
- A Redis Lua script can apply refill and consumption without interleaving.
- Retain state for a full refill period and validate capacity, rate and timestamp inputs.

## Further reading
- [Redis: Rate limiting](https://redis.io/glossary/rate-limiting/)
- [Redis: Scripting atomicity](https://redis.io/docs/latest/develop/programmability/eval-intro/)
