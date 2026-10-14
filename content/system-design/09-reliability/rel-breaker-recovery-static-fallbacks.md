---
id: rel-breaker-recovery-static-fallbacks
title: Breaker recovery and static fallbacks
level: intermediate
minutes: 3
summary: Fail quickly around a troubled dependency and keep degraded responses useful.
sourceLesson: rel-overload-protection
---

Bulkheads reserve resources. A circuit breaker goes further by stopping new calls when recent outcomes show a dependency is unhealthy. Decide what useful response remains, and ensure the fallback does not introduce another untested live dependency.

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

This illustrative YAML policy expresses the original thresholds; it is not any named library’s configuration format. Translate slow-call handling into the chosen library’s separate threshold, predicate or timeout controls.

```yaml
breaker:
  window: "10s rolling"
  # One failed call is too little evidence.
  min_requests: 20
  failure_rate: "50%"
  # Classify latency by library policy.
  slow_call: "over 500ms counts as failure"
  open_duration: "30s"
  # Limit probes before full traffic
  # resumes.
  half_open_trials: 5
```

Counting **slow calls** as failures matters: it lets the breaker react to gray failure, not just errors. Resilience4j provides separate slow-call rate thresholds. Polly uses a configured failure predicate; combine it with an appropriate timeout strategy to classify slow operations. Envoy and Istio also provide host outlier detection, with different signals and configuration.

> [!warning] Breakers can hide partial failure
> A single breaker per dependency may trip when only one of its hosts is bad, cutting off healthy hosts too. Per-host breakers or proxy-level outlier ejection give finer control.

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
> The AWS Builders' Library argues against complex fallbacks: a code path that only runs during outages may be poorly exercised, and it may put sudden new load on another system. Prefer **static fallbacks** (cached or precomputed data), or make the "fallback" the path you use all the time.

## Key takeaways

- Closed breakers admit calls; open breakers reject; half-open breakers allow limited recovery trials.
- Count enough requests and include slow calls using the library’s actual failure signals.
- Prefer simple, exercised, static fallbacks; a rare live fallback can fail under sudden incident load.

## Further reading

- [Circuit breaker (Martin Fowler)](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Avoiding fallback in distributed systems (AWS Builders' Library)](https://aws.amazon.com/builders-library/avoiding-fallback-in-distributed-systems/)
- [Circuit Breaker pattern (Azure Architecture Center)](https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker)
