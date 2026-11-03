---
id: rel-latency-timeouts-deadlines
title: Latency-based timeouts and shared deadlines
level: intermediate
minutes: 4
summary: Choose per-call timeouts from latency measurements and propagate one operation budget.
sourceLesson: rel-timeouts-retries
---

Gray failures hold caller resources while appearing alive. This unit bounds that resource use. A per-try timeout limits one attempt; an operation deadline limits the entire chain, including time already spent at earlier hops.

Every remote call can hang, fail or succeed slowly. Timeouts bound how long you wait; retries can recover from transient failures. Used carelessly, though, retries can contribute to large outages: they multiply load at the exact moment a system is weakest.

The following units separate timeout selection, retry safety, backoff, amplification and budgets.

## Timeouts: every call needs one

A call with no timeout can hold a thread, a connection and memory forever. Many client libraries default to *no timeout* or to absurdly long ones (some HTTP clients default to minutes). Under a gray failure (a dependency that's slow but alive), these calls pile up until the caller runs out of threads and fails too.

There are usually several timeouts on one call:

| Timeout | Bounds | Typical value |
|---|---|---|
| Connect | Connection establishment; TLS/DNS coverage depends on client | Measure for the client and network |
| Request / read | Response wait or inactivity interval, depending on client | Choose from measured latency |
| Overall deadline | Whole operation | user's budget |

### Choosing the value

The AWS Builders' Library recommends picking a timeout from the dependency's **latency distribution**: choose an acceptable false-timeout rate (say 0.1%) and set the timeout at the matching percentile (p99.9), plus some padding.

A percentile is read from measured latencies: **p99.9** is the latency that 99.9% of calls beat, so only 0.1% of healthy calls take longer. If a dependency's p99.9 is 140 ms, a timeout at 140 ms reaches the roughly 0.1% healthy-call tail; padding it to about 150 ms should reduce false timeouts, but the precise fraction depends on the measured distribution. Very rare outliers (a 2-second GC pause at p99.99) are deliberately left to time out.

- Too short: you time out healthy-but-slightly-slow requests, retry them and *add* load.
- Too long: callers wait on doomed requests and exhaust their resources.

### Deadline propagation

A user-facing request with a 2-second budget calls A, which calls B, which calls C. If each hop independently uses a 2 s timeout, C may keep working for seconds after the user has given up.

The fix is to propagate an **RPC deadline**, rather than restarting a timeout at each hop. gRPC supports this when the language/runtime propagates the incoming context to outgoing calls. The remaining budget travels with the request; handlers must observe cancellation and stop their own work, because the deadline does not forcibly roll back or terminate every side effect.

Each downstream call receives only the time still available in the original operation budget. Time spent in earlier calls or backoff is already gone.

```
User budget: 2000 milliseconds
Arrival: A starts, 2000 ms left
After 300 ms: A calls B, 1700 ms left
After 900 ms: B calls C, 1100 ms left
C: fail if budget cannot fit useful work
```

A service can reject work unlikely to finish within the remaining budget; choose that request-admission rule from its latency distribution and the value of a late result. Absolute deadlines assume the hosts' clocks roughly agree; gRPC avoids most clock skew by sending the remaining *duration* and converting it to a local deadline at each hop.

> [!analogy] Real-world analogy: one lunch break for several errands
> If the first errand uses most of your lunch break, the next shop does not give you a fresh hour.
>
> **How it maps:** The lunch break is the whole-operation budget; each call and wait spends part of the same remaining time.
>
> **Where it stops:** A deadline cannot reverse work already done. Services must observe cancellation, and timing behaviour depends on the runtime.

## Key takeaways

- Timeout scope depends on the client: connect, read and whole-operation deadlines are different.
- Choose an acceptable false-timeout rate and measure the matching latency percentile.
- Propagate the remaining duration and observe cancellation; a deadline cannot undo an already committed effect.

## Further reading

- [Timeouts, retries and backoff with jitter (AWS Builders' Library)](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
- [gRPC deadlines](https://grpc.io/docs/guides/deadlines/)
