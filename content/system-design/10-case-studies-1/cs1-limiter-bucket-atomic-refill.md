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

```formula
T_new = min(B, T + (now − last) × r)
where
T_new: tokens in the bucket after the refill, before this request takes one
T: tokens stored at the last update
B: the bucket capacity, the most tokens it can hold, which is the largest burst allowed
r: the refill rate, in tokens per second
now: the current time, in seconds
last: the time of the last update (last_refill), in seconds
now − last: seconds since the last update
min: "the smaller of", which stops the bucket filling beyond B
In words: add the tokens earned since the last request at r per second, but never more than the capacity B.
```

For a capacity of ten tokens and a refill rate of one token a second, substitute a bucket left with two tokens:

```formula
T_new = min(10, 2 + 5 s × 1/s) = 7
T_new = min(10, 2 + 60 s × 1/s) = 10
where
T_new: available tokens after refill and before spending one
min: choose the smaller value, capping at ten tokens
s: seconds; 1/s means one token per second here
In words: five idle seconds restore the bucket to seven tokens; a minute restores it only to its ten-token capacity.
```

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

- **Pro**: allows controlled bursts (up to *B*) while enforcing a long-run average of *r*. Two numbers per key. Stripe’s published implementation describes this algorithm, and AWS API Gateway’s documentation specifies token-bucket throttling.
- **Con**: two parameters to tune; bursts are allowed by design, which might not suit a fragile downstream.

### Leaky bucket

Requests enter a FIFO queue drained at a fixed rate. Output is perfectly smooth, which suits traffic shaping in front of something fragile, but queued requests wait, and bursts are delayed rather than served. As a pure "allow or reject" meter, it behaves like a token bucket. GCRA (generic cell rate algorithm) is an elegant single-timestamp variant.

> [!tip] Default answer
> Token bucket for explicit burst-plus-average limits; sliding counters approximate rolling windows but do not provide exact rolling-window enforcement.

## Deep dive 2: Correctness under concurrency

Hundreds of gateway nodes check the same key at the same moment. A naive "read count, compare, write count + 1" is a race: two servers both read 99, both allow, both write 100, and the client got 101.

Fixes:

- **Atomic primitives.** For fixed windows, `INCR` is atomic and returns the new value: `INCR key`, then `EXPIRE key 60` on first creation, and compare the returned value with the limit. If the process dies between the two commands the key never expires, so do both in a Lua script or an appropriate transaction. Repeatedly extending a relative TTL changes expiration semantics unless the key includes the fixed window or the expiry is an absolute window boundary.
- **Lua scripts.** For token buckets, run the read-refill-decrement-write as a single Redis Lua script. Redis executes scripts atomically, so there are no races, and it's still one round trip.
- **Use the server's clock.** If every gateway passes its own `now`, clock skew between gateways distorts refills. Read time inside the script (`redis.call('TIME')`) so one clock is authoritative per key.

Redis Cluster maps keys to hash slots. The client-tag design co-locates that client's rules for one script; a global fleet counter or IP/account combination can require other slots, so arbitrary combined rules are not automatically atomic.

## Key takeaways

- Bucket capacity sets burst size; refill rate sets the long-run allowance.
- Perform read, refill, decrement and persistence in one atomic operation.
- Keep fixed-window expiry and clock semantics explicit.

## Further reading

- [Redis: atomic increment and rate-limit patterns](https://redis.io/docs/latest/commands/incr/)
- [Stripe: rate and concurrency limiting](https://stripe.com/blog/rate-limiters)
- [Redis: scripting atomicity](https://redis.io/docs/latest/develop/programmability/eval-intro/)
