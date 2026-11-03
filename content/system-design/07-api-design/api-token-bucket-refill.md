---
id: api-token-bucket-refill
title: Token buckets, bursts and refill waits
level: advanced
minutes: 4
summary: Separate burst capacity from sustained rate, refill lazily and tell rejected clients when another token can be ready.
sourceLesson: api-rate-limiting
---

## Token bucket

A common algorithm. Each client has a bucket that holds up to **capacity** tokens. Tokens are added at a fixed **refill rate**. Each request takes one token; if the bucket is empty, the request is rejected.

```
  refill r tokens/s
        |
        v
   +---------+
   | o o o o |  capacity C
   | o o o   |
   +----+----+
        |
   1 token per request
   empty -> 429
```

Two parameters, two meanings:

- **Refill rate** = long-run average throughput.
- **Capacity** = largest burst allowed.

You don't need a timer to add tokens. Store the token count and the time of the last top-up, and when a request arrives, add the tokens that would have dripped in since then:

```formula reference
b_new = min(C, b_old + r × Δt)
where
b_new: the number of tokens in the bucket after the top-up
b_old: the tokens stored at the last top-up
C: the capacity, the most tokens the bucket can hold
r: the refill rate, in tokens per second
Δt: delta t, the time since the last top-up, in seconds
min: the smaller of the two values, so the bucket never overflows its capacity
In words: add tokens for the time that has passed, but never more than the bucket holds.
```

If the bucket then holds less than one whole token, the request is rejected, and the client can be told how long until one token is ready:

```formula reference
W = (1 − b_new) / r
where
W: the wait until the bucket holds one whole token, in seconds; this is the natural Retry-After value
b_new: the tokens in the bucket now, less than 1
r: the refill rate, in tokens per second
In words: the missing fraction of a token divided by how fast tokens arrive. Use this only when fewer than one token remains and the rate is positive. For Retry-After expressed as a delay, round upwards to whole seconds.
```

This executable Python function receives the current token count, its stored timestamp, a trusted current timestamp in seconds, the capacity and the refill rate. Assume finite inputs: capacity at least one, positive refill rate, and a token count between zero and capacity. Use one consistent monotonic clock; never accept arbitrary client timestamps. The small clamp prevents a regressing timestamp from minting tokens, while large forward clock jumps still need an explicit policy.

```python
def take_token(tokens, last_refill, now,
               capacity, rate):
    # Never move stored time backwards.
    now = max(now, last_refill)
    elapsed = now - last_refill
    # Refill only when a request arrives.
    tokens = min(capacity,
                 tokens + elapsed * rate)
    if tokens >= 1:
        # Allowed: spend a complete token.
        return True, tokens - 1, now, 0.0
    # Rejected: keep fractional allowance.
    wait = (1 - tokens) / rate
    return False, tokens, now, wait
```

The returned tuple contains the decision, remaining tokens, new stored timestamp and wait in seconds. The wait is zero for an allowed request; otherwise round it upwards for a whole-second `Retry-After`. This local function does not coordinate concurrent servers; the later atomic-limiter unit handles shared state.

> [!example] Token bucket maths
> Capacity 10, refill 2 tokens/s, bucket full. A client sends 15 requests instantly: the first 10 succeed, 5 get 429. One second later the bucket has 2 tokens, so 2 more can go through. Sustained, the client gets 2 requests/s, or 120 per minute.

The burst and the sustained rate are different limits:

Stored tokens allow a burst above the refill rate. The rate controls sustained average traffic, not a strict cap in every rolling second or minute.

Amazon API Gateway and AWS service APIs use token buckets (they call the parameters "rate" and "burst"). Stripe uses token buckets in Redis.

> [!analogy] Real-world analogy: Refilling admission passes
> **How it maps:** A box holds a limited number of passes and gains new passes steadily. Each visitor uses one. A full box admits a group immediately; later visitors depend on refill.
>
> **Where it stops:** This limiter rejects when no pass remains; it does not queue rejected requests. Real implementations must handle shared state and clock behaviour.

## Key takeaways
- Capacity bounds the stored burst; refill rate sets the sustained average.
- Refill lazily from elapsed time, capped at capacity, then spend a token.
- Round the missing-token wait upwards for a whole-second Retry-After.

## Further reading
- [Stripe blog: Scaling your API with rate limiters](https://stripe.com/blog/rate-limiters)
- [Wikipedia: Token bucket](https://en.wikipedia.org/wiki/Token_bucket)
