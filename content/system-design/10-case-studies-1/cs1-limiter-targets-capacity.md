---
id: cs1-limiter-targets-capacity
title: Set limiter guarantees and estimate capacity
level: intermediate
minutes: 3
summary: Separate policy targets from measured Redis capacity.
sourceLesson: cs1-rate-limiter
---

A rate limiter caps how many requests a client can make in a period. It protects services from abuse and runaway clients, enforces pricing tiers ("free plan: 100 requests per minute"), and stops one tenant from starving everyone else.

On one server it's an in-memory counter. The interview is about making it work across hundreds of API servers, at a million requests a second, adding no more than a millisecond, and staying correct when clients race each other.

## Step 1: Requirements

**Functional**

- Limit requests per **key** (API key, user ID, IP address, or a combination) according to **rules** such as "100 requests/minute per API key on `POST /charges`".
- Support several rules per request (per-second burst limit *and* per-day quota).
- When a limit is exceeded, reject with **HTTP 429 Too Many Requests** and tell the client when to retry.
- Rules can be changed without redeploying.

**Non-functional**

- **Low overhead**: the check sits on every request, so it must add under ~1–2 ms at p99.
- **Highly available**: if the limiter is down, the API should keep working.
- **Approximately accurate**: a small overshoot (a few percent) is fine; massively over-admitting is not.
- **Distributed**: limits are global across all API servers, not per server.

## Step 2: Estimates

Assume an API fleet handling **1 million requests/s** at peak, with **10 million active keys** a day.

Every request needs one limiter check, which is one Redis call (a single Lua script). The number of Redis shards follows from dividing the check rate by what one shard handles:

```formula
shards = checks / cap
shards = 1,000,000/s / (50,000/s) = 20
where
shards: Redis shards (separate servers each holding part of the keys) needed, before adding replicas
checks: limiter checks per second, one per API request: 1 million at peak
cap: checks per second one shard handles at the target tail latency, here an assumed 50,000 (50k)
/s: per second
In words: a million checks a second at an assumed 50,000 per shard needs about 20 shards, plus replicas for failover.
```

Memory is keys times rules per key times bytes per counter:

```formula
memory = keys × rules × size
memory = 10M × 2 × 100 B ≈ 2 GB
where
memory: RAM needed for all counters
keys: active client keys per day, 10 million (10M)
rules: rules applied to each key, here 2 (a burst limit and a daily quota)
size: bytes per stored counter, an assumed 100 bytes (B)
M: million
B: bytes
GB: gigabyte, 10^9 bytes
≈: approximately equal to
In words: 10 million keys with two 100-byte counters each is about 2 GB of memory.
```

These are illustrative sizing inputs, not measured Redis capacity or memory bounds. Actual key strings, objects, allocator overhead, scripts, replication and network tails must be measured. A single atomic call reduces both race windows and network hops.

> [!note] Content gap: deployment benchmarks
> No reproducible deployment benchmark is supplied for the stated 1–2 ms target or per-shard throughput/footprint. Universal capacity and latency estimates are omitted; the calculation above uses explicit assumptions.

## Key takeaways

- Separate policy targets from measured Redis capacity.
- Count checks, active keys and rules independently.
- Choose the consequence of counter resets before selecting storage.

## Further reading

- [Stripe: rate and concurrency limiting](https://stripe.com/blog/rate-limiters)
- [Redis: benchmark limitations](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/)
