---
id: rel-overload-protection
title: Circuit breakers, bulkheads and load shedding
level: intermediate
minutes: 13
summary: Stop failures spreading with circuit breakers and bulkheads, and survive overload with load shedding, backpressure and graceful degradation.
---

Timeouts and retries deal with individual calls. This lesson is about protecting a whole service when a dependency is failing or when demand exceeds capacity. The goal is the same in every case: **fail small and fast rather than big and slow**.

## Why overload is a cliff, not a slope

With variable arrivals and service times, queueing delay can rise sharply near capacity. The simplest model that shows this is the **M/M/1 queue**: requests arrive at random (a Poisson process), each takes a random, exponentially distributed time to serve, there is one server, requests are served first in, first out (FIFO), and the waiting line has no size limit. For a stable M/M/1 queue, the average time a request spends in the system (waiting plus being served) is:

```formula
W = S / (1 − ρ)
W = 10 ms / (1 − 0.9)
W = 10 ms / 0.1 = 100 ms
where
W: the mean time in system (queueing plus service), in milliseconds (ms)
S: the mean service time, the time to process one request with no queue, here 10 ms
ρ: rho, the utilisation: the fraction of time the server is busy, from 0 to just under 1; here 0.9 (90%)
ms: milliseconds
In words: at 90% busy, a request that takes 10 ms of work spends 100 ms in the system on average, ten times its service time, because most of that time is spent queueing.
```

Dividing W by S gives the latency multiplier 1 / (1 − ρ). The model only holds while ρ is below 1; at or above 1 the queue never settles.

| Utilisation | Latency multiplier |
|---|---|
| 50% | 2× |
| 80% | 5× |
| 90% | 10× |
| 99% | 100× |

The tail is worse than the mean. In an M/M/1 queue the time in system is exponentially distributed, and for an exponential distribution any percentile is a fixed multiple of the mean:

```formula
W_99 = W × ln(100)
W_99 ≈ 100 ms × 4.6 ≈ 460 ms
where
W_99: the 99th-percentile (p99) time in system: 99% of requests finish faster than this, in milliseconds (ms)
W: the mean time in system, here 100 ms (90% utilisation, 10 ms service time)
ln: the natural logarithm (log to base e ≈ 2.718); ln(100) ≈ 4.6
≈: approximately equal to (rounded)
ms: milliseconds
In words: in this model the slowest 1% of requests take more than about 4.6 times the average, so a 100 ms mean means a p99 of about 460 ms.
```

Where does ln(100) come from? For an exponential distribution, the fraction of requests slower than some multiple of the mean shrinks exponentially:

```formula
F = e^(−x)
F = e^(−ln(100)) = 1/100 = 1%
where
F: the fraction of requests slower than x times the mean
x: how many times the mean, here ln(100) ≈ 4.6
e: Euler's number, about 2.718, the base of natural logarithms
ln: the natural logarithm, the inverse of e^; e^(ln(100)) = 100
^: "to the power of"
≈: approximately equal to
In words: only 1% of requests are slower than about 4.6 times the mean, which is why p99 is about 4.6 times the mean in this model.
```

Multi-worker systems and other arrival/service distributions have different delay curves; measure actual service behavior rather than treating M/M/1 as a universal bound.

Two more facts worth carrying around:

**Little's law** links traffic, latency and concurrency for any stable system, whatever the arrival pattern:

```formula
L = λ × W
L = 1,000 req/s × 0.05 s = 50
L = 1,000 req/s × 2 s = 2,000
where
L: the average number of requests in flight (in the system at once)
λ: lambda, the arrival rate, in requests per second (req/s), here 1,000
W: the average time each request spends in the system, in seconds (s): 50 ms = 0.05 s, or 2 s
req/s: requests per second
s: seconds
In words: in-flight requests equal arrival rate times latency. At 1,000 req/s, a 50 ms latency keeps 50 requests in flight; a 2 s latency keeps 2,000 in flight.
```

So slowness alone exhausts threads and connections: the traffic didn't change, but the concurrent slots needed went up forty-fold.

**Without rejection or abandonment, sustained arrivals above service capacity have no finite steady-state queue.** The queue grows at the gap between what arrives and what is served:

```formula
Q(t) = (λ − μ) × t
Q(60 s) = (1,100 − 1,000) req/s × 60 s
Q(60 s) = 6,000
where
Q(t): the extra requests queued after t seconds of overload
λ: lambda, the arrival rate, here 1,100 requests per second (req/s)
μ: mu, the service rate, the most requests per second the server can complete, here 1,000 req/s
t: the time the overload has lasted, in seconds (s), here 60 s
req/s: requests per second
s: seconds
In words: 100 more requests arrive each second than can be served, so after a minute 6,000 are waiting, and the queue keeps growing for as long as the overload lasts.
```

Every request waits longer than the one before until something gives.

Past saturation, latency rises until requests time out. Callers retry, adding load. Work completes after the client has given up, so the server does 100% work for 0% useful output. This is **congestive collapse**, and the patterns below exist to prevent it.

```
Goodput
  ▲      with shedding
  │   ┌───────────────
  │  ╱╲
  │ ╱  ╲ without
  │╱    ╲___________
  └──────────────────▶
       offered load
```

## Circuit breakers

A **circuit breaker** wraps calls to a dependency and tracks failures. When failures cross a threshold, it "trips" and fails calls immediately without contacting the dependency. Martin Fowler popularised the pattern, building on Michael Nygard's *Release It!*.

```
        failures > threshold
 ┌────────┐ ─────────▶ ┌──────┐
 │ CLOSED │            │ OPEN │
 └────────┘ ◀──┐       └──────┘
     ▲         │  timer   │
     │ ok      │ expires  ▼
     │      ┌───────────┐
     └──────│ HALF-OPEN │
      fail→ └───────────┘
      back to OPEN
```

- **Closed**: calls pass through; failures are counted over a rolling window.
- **Open**: calls fail immediately (or go to a fallback). No new calls through that breaker reach the dependency; existing calls and other clients can remain.
- **Half-open**: after a cool-down, a few trial calls go through. Success closes the breaker; failure reopens it.

### Why it helps

1. The failing dependency gets breathing room to recover instead of being hammered.
2. Callers stop wasting threads and time waiting on doomed calls; they fail without waiting for the remote timeout.
3. It provides a natural place to return a fallback or degraded response.

### Tuning

```
breaker:
  window: 10s rolling
  min_requests: 20   # not on 1/1
  failure_rate: 50%
  slow_call: >500ms counts as failure
  open_duration: 30s
  half_open_trials: 5
```

Counting **slow calls** as failures matters: it lets the breaker react to gray failure, not just errors. Resilience4j provides separate slow-call rate thresholds. Polly uses a configured failure predicate; combine it with an appropriate timeout strategy to classify slow operations. Envoy and Istio also provide host outlier detection, with different signals and configuration.

> [!warning] Breakers can hide partial failure
> A single breaker per dependency may trip when only one of its hosts is bad, cutting off healthy hosts too. Per-host breakers or proxy-level outlier ejection give finer control.

## Bulkheads

Ships are divided into watertight compartments (bulkheads) so one breach doesn't sink the vessel. In software, a **bulkhead** isolates resources so one failing workload can't consume everything.

Without bulkheads, a service with a 200-thread pool calling three dependencies can lose all 200 threads to the one dependency that's hanging:

```
Shared pool (200)      Bulkheads
┌───────────────┐   ┌─────┬─────┬─────┐
│ ████████████  │   │ A:80│ B:80│ C:40│
│ all stuck on C│   │ ok  │ ok  │stuck│
└───────────────┘   └─────┴─────┴─────┘
 everything down     only C's feature down
```

Bulkheads appear at many scales:

- **Thread or connection pools** per dependency.
- **Separate instances** for critical and non-critical traffic (e.g. checkout vs recommendations).
- **Per-tenant quotas**, so a noisy customer can't starve others.
- **Cells and shards**, the largest form of bulkhead (see the designing-for-failure lesson).

## Load shedding

When a server is beyond capacity, it should **reject excess work quickly** rather than accept everything and serve it all late. An early `503` can cost far less than normal processing; a request that times out after doing 2 s of work costs 2 s of capacity for nothing.

The AWS Builders' Library describes the principle: protect **goodput** (useful completed work) by shedding just enough to keep latency within the clients' timeouts.

### How to decide what to shed

- **Concurrency limits**: cap in-flight requests (e.g. 100). Above that, reject. Size the cap with Little's law (see the formula below), plus a margin. Adaptive versions (like Netflix's concurrency-limits library) adjust the cap from observed latency, TCP-congestion style.
- **Queue time**: if a request waited in the queue longer than the client's timeout, drop it if its useful work is tied to that deadline. Durable accepted jobs may still need completion even after a client disconnects. Some systems go further: Facebook's "adaptive LIFO" serves the queue newest-first when it builds up, because the newest requests are the ones whose clients are still waiting.
- **Priority / criticality**: shed lower-priority traffic first. Google tags requests as `CRITICAL_PLUS`, `CRITICAL`, `SHEDDABLE_PLUS` and `SHEDDABLE`, and sheds from the bottom.

Sizing a concurrency limit with Little's law:

```formula
C = X × W × (1 + m)
C = 2,000 req/s × 0.04 s × 1.25 = 100
where
C: the concurrency limit, the most requests allowed in flight at once
X: the throughput the server can sustain at healthy latency, in requests per second (req/s), here 2,000
W: the healthy latency at that throughput, in seconds (s), here 40 ms = 0.04 s
m: the safety margin as a fraction, here 25% = 0.25
req/s: requests per second
s: seconds
In words: a server doing 2,000 req/s at 40 ms has about 80 requests in flight when healthy; allowing 25% headroom gives a cap of 100. More in flight than that means requests are queueing, not being served faster.
```

The numbers here are illustrative. The admission check might look like this in code:

```python
def admit(req):
  if req.deadline <= now():
    return reject(503)
  # Priority is assigned by trusted policy.
  # Lower classes have smaller limits.
  cap = limits[req.trusted_priority]
  if not slots.try_acquire_below(cap):
    return reject(503, retry_after=1)
  try:
    return process(req)
  finally:
    slots.release()
```

> [!tip] Make rejection cheap
> Shedding only works if rejecting is much cheaper than serving. Use cheap early admission checks before expensive body parsing or database access. Authenticate or validate any priority/tenant identity used for admission; never trust a caller-supplied criticality flag to bypass limits.

### Client-side throttling

The Google SRE book describes **adaptive throttling**: each client counts the requests it has tried to make and the requests the backend accepted, over the last two minutes, and rejects new requests locally with this probability:

```formula
P_rej = max(0, (R − K × A) / (R + 1))
P_rej = max(0, (100 − 2 × 30) / 101)
P_rej = 40 / 101 ≈ 0.40
where
P_rej: the probability that the client rejects a new request itself, without sending it, from 0 to 1
max: the larger of the two values, so P_rej is never below 0
R: requests, the number of requests the application attempted, including ones the client rejected locally, here 100
A: accepts, the number of requests the backend accepted, here 30
K: a tuning multiplier, usually 2
≈: approximately equal to (rounded)
In words: while the backend accepts at least half the requests (with K = 2), nothing is dropped locally; when it accepts only 30 of 100, the client drops about 40% of new requests itself.
```

So with K = 2, once the backend is rejecting more than half the requests, the client starts dropping some itself, and those rejected requests don't even cost the backend a network round trip. In steady state the client sends roughly K × A requests: twice what the backend is accepting, enough to notice quickly when it recovers. Lower K is more aggressive; higher K wastes more backend effort on rejections. The +1 in the denominator only stops division by zero when the client has sent nothing yet.

## Backpressure at the service level

**Backpressure** means a slow consumer signals upstream to slow down instead of silently buffering. Unbounded queues are the enemy: they turn an overload into ever-increasing latency and eventually an out-of-memory crash.

- **Bounded queues**: when full, reject or block the producer.
- **Protocol signals**: HTTP `429` with `Retry-After`, gRPC `RESOURCE_EXHAUSTED`, TCP flow control windows, Reactive Streams' `request(n)`.
- **Pull-based consumption**: Kafka consumers pull at their own pace, so the broker never pushes faster than they can handle; lag grows instead (which you alert on).

Backpressure must propagate all the way to something that can actually slow down: a user, a batch job, or a queue with spare capacity. Otherwise it just moves the overflow somewhere else.

## Graceful degradation

When a dependency fails, serve a **reduced but useful** response rather than an error.

| Failed dependency | Degraded behaviour |
|---|---|
| Recommendations | Show bestsellers (static list) |
| Reviews | Hide the reviews panel |
| Personalised prices | Show list price |
| Search ranking ML | Fall back to text relevance |

Netflix is the classic example: if the personalisation service is down, the home page still renders with generic rows, and users can still press play.

> [!warning] Fallbacks are dangerous if rarely exercised
> The AWS Builders' Library argues against complex fallbacks: a code path that only runs during outages may be poorly exercised, and it may put sudden new load on another system. Prefer **static** fallbacks (cached or precomputed data), or make the "fallback" the path you use all the time.

## How the patterns fit together

```
Request
  ▼
[Load shedder] reject if over capacity
  ▼
[Bulkhead]  per-dependency pool
  ▼
[Breaker]   fail fast if open
  ▼
[Timeout + budgeted retry]
  ▼
Dependency
  ✗ → fallback (degrade)
```

## Key takeaways

- Overload is a cliff: past saturation, latency explodes and goodput collapses, so protection must be designed in.
- Circuit breakers stop calls to failing dependencies, give them time to recover, and should count slow calls as failures.
- Bulkheads partition pools, instances and quotas so one bad dependency or tenant can't consume everything.
- Load shedding rejects excess work cheaply and early, preferring low-priority traffic and requests whose clients have already timed out.
- Backpressure needs bounded queues and explicit signals that reach something able to slow down.
- Graceful degradation keeps the core experience working; keep fallbacks simple, static and regularly exercised.

## Further reading

- [Circuit breaker (Martin Fowler)](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Using load shedding to avoid overload (AWS Builders' Library)](https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/)
- [Avoiding fallback in distributed systems (AWS Builders' Library)](https://aws.amazon.com/builders-library/avoiding-fallback-in-distributed-systems/)
- [Handling overload (Google SRE book)](https://sre.google/sre-book/handling-overload/)
- [Bulkhead pattern (Azure Architecture Center)](https://learn.microsoft.com/en-us/azure/architecture/patterns/bulkhead)
- [Circuit Breaker pattern (Azure Architecture Center)](https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker)
