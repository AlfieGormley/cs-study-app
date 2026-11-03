---
id: cs1-limiter-bucket-atomic-refill
title: Implement burst limits with atomic refill checks
level: intermediate
minutes: 4
summary: Bucket capacity sets burst size; refill rate sets the long-run allowance.
sourceLesson: cs1-rate-limiter
---

### Token bucket

Each key has a bucket that holds up to a fixed number of tokens and is topped up at a steady rate. Each request takes a token; an empty bucket means reject. Instead of a timer adding tokens, store just `tokens` and `last_refill` and work out the refill lazily on each request:

```formula reference
T_new = min(B, T + Δt r)
where
T_new: token balance after refill and before this request spends a token
T: previous token balance
B: maximum token balance, defining the available burst capacity
Δt: nonnegative elapsed time since the last accounted refill, in seconds
r: refill rate in tokens per second
min: choose the smaller value, preventing accumulated tokens from exceeding capacity
In words: idle time earns tokens at the refill rate, but the bucket never holds more than its burst capacity.
```

For example, five idle seconds at one token per second add five tokens if space remains. A long idle period only fills the bucket to capacity; it does not build an unlimited allowance.

The formula assumes the current time has not moved backwards. The Python fixture clamps negative elapsed time to zero; production timestamp persistence must also avoid granting the same elapsed interval twice after a clock regression.

```python
def refill(tokens, elapsed, cap, rate):
    # Clamp time if the clock regresses.
    earned = max(0, elapsed) * rate
    # Cap bursts after long idle time.
    return min(cap, tokens + earned)

print(refill(2, 5, 10, 1))
print(refill(2, 60, 10, 1))
# 7 then 10: refill stops at capacity.
```

This fixture checks refill arithmetic, not distributed admission. Production code must atomically update the token balance and timestamp and define how clock changes and failover are handled.

- **Pro**: separates maximum stored burst allowance from the long-run refill rate. Two numbers per key. Stripe’s published implementation describes this algorithm.
- **Con**: two parameters to tune; bursts are allowed by design, which might not suit a fragile downstream.

### Leaky bucket

Requests enter a FIFO queue drained at a fixed rate. An ideal fixed-rate drain paces output, which suits traffic shaping in front of something fragile, but queued requests wait, and bursts are delayed rather than served. A meter that rejects excess traffic and a queue that delays it have different client-visible behaviour; define which meaning is intended.

> [!tip] Default answer
> Token bucket for explicit burst-plus-average limits; sliding counters approximate rolling windows but do not provide exact rolling-window enforcement.

## Deep dive 2: Correctness under concurrency

Hundreds of gateway nodes check the same key at the same moment. A naive "read count, compare, write count + 1" is a race: two servers both read 99, both allow, both write 100, and the client got 101.

Fixes:

- **Atomic primitives.** For fixed windows, `INCR` is atomic and returns the new value: `INCR key`, then `EXPIRE key 60` on first creation, and compare the returned value with the limit. If the process dies between the two commands the key never expires, so do both in a Lua script or an appropriate transaction. Repeatedly extending a relative TTL changes expiration semantics unless the key includes the fixed window or the expiry is an absolute window boundary.
- **Lua scripts.** For token buckets, run the read-refill-decrement-write as a single Redis Lua script. Redis executes a script atomically on its node, preventing interleaved updates there in one round trip. Atomic execution is not a durability guarantee: Redis Cluster's asynchronous replication can lose acknowledged state on failover, granting extra allowance unless the wider policy accounts for it.
- **Use the server's clock.** If every gateway passes its own `now`, clock skew between gateways distorts refills. Read time inside the script (`redis.call('TIME')`) so one clock is authoritative per key.

Redis Cluster maps keys to hash slots. The client-tag design co-locates that client's rules for one script; a global fleet counter or IP/account combination can require other slots, so arbitrary combined rules are not automatically atomic.

> [!analogy] Real-world analogy: A small jar of admission tickets
> Tickets are replenished steadily, but the jar has a fixed capacity. A visitor can spend several saved tickets together.
>
> **How it maps:** Stored tickets are burst allowance; replenishment is the sustained rate; rejecting an empty jar prevents spending future allowance.
>
> **Where it stops:** Distributed servers must atomically share the balance and account for time and failover; separate jars do not automatically enforce a global limit.

## Key takeaways

- Bucket capacity sets burst size; refill rate sets the long-run allowance.
- Perform read, refill, decrement and persistence in one atomic operation.
- Keep fixed-window expiry and clock semantics explicit.

## Further reading

- [Redis: atomic increment and rate-limit patterns](https://redis.io/docs/latest/commands/incr/)
- [Stripe: rate and concurrency limiting](https://stripe.com/blog/rate-limiters)
- [Redis: scripting atomicity](https://redis.io/docs/latest/develop/programmability/eval-intro/)
