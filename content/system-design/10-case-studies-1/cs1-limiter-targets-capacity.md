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

The check rate sets throughput demand. Benchmark the actual script at the required tail latency, then allow for uneven keys, replication and failover rather than running every shard at its maximum.

Count the state retained by the limiter:

Memory depends on concurrently retained keys, rules per key and the actual stored representation. Daily unique clients are not automatically the number of counters resident at once.

These are illustrative workload inputs, not measured Redis capacity or memory bounds. Actual key strings, objects, allocator overhead, scripts, replication and network tails must be measured. A single atomic call reduces both race windows and network hops.

> [!note] Content gap: deployment benchmarks
> No reproducible deployment benchmark is supplied for the stated 1–2 ms target or per-shard throughput/footprint. Universal capacity and latency estimates are omitted; the workload and target above use explicit assumptions.

## Key takeaways

- Separate policy targets from measured Redis capacity.
- Count checks, active keys and rules independently.
- Choose the consequence of counter resets before selecting storage.

## Further reading

- [Stripe: rate and concurrency limiting](https://stripe.com/blog/rate-limiters)
- [Redis: benchmark limitations](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/)
