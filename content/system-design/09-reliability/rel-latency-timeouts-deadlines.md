---
id: rel-latency-timeouts-deadlines
title: Latency-based timeouts and shared deadlines
level: intermediate
minutes: 4
summary: Choose per-call timeouts from latency measurements and propagate one operation budget.
sourceLesson: rel-timeouts-retries
---

Gray failures hold caller resources while appearing alive. This unit bounds that resource use. A per-try timeout limits one attempt; an operation deadline limits the entire chain, including time already spent at earlier hops.

Every remote call can hang, fail or succeed slowly. Timeouts bound how long you wait; retries turn transient failures into successes. Used carelessly, though, retries can contribute to large outages: they multiply load at the exact moment a system is weakest.

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

Each hop works out how much time is left from the one absolute deadline it received:

```formula
t_left = D − t_now
t_left = 2000 ms − 300 ms = 1700 ms
t_left = 2000 ms − 900 ms = 1100 ms
where
t_left: the time remaining before the user gives up, in milliseconds (ms)
D: the absolute deadline on a clock with request arrival as zero, in milliseconds (ms); here 2000 ms
t_now: the current time on the same request-start clock, in milliseconds (ms); here 300 ms when A calls B
ms: milliseconds; 1000 ms = 1 second
In words: the remaining budget is the deadline minus the time already spent, so every hop down the chain gets less, never a fresh 2 seconds.
```

```
User budget: 2000 milliseconds
Arrival: A starts, 2000 ms left
After 300 ms: A calls B, 1700 ms left
After 900 ms: B calls C, 1100 ms left
C: fail if budget cannot fit useful work
```

Here p50 is the median latency of C's work: if less time remains than C usually needs, it is better to fail at once than start work nobody will wait for. Absolute deadlines assume the hosts' clocks roughly agree; gRPC avoids most clock skew by sending the remaining *duration* and converting it to a local deadline at each hop.

## Key takeaways

- Timeout scope depends on the client: connect, read and whole-operation deadlines are different.
- Choose an acceptable false-timeout rate and measure the matching latency percentile.
- Propagate the remaining duration and observe cancellation; a deadline cannot undo an already committed effect.

## Further reading

- [Timeouts, retries and backoff with jitter (AWS Builders' Library)](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
- [gRPC deadlines](https://grpc.io/docs/guides/deadlines/)
