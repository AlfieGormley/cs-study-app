---
id: rel-metric-cardinality-histograms
title: Metric cardinality and latency histograms
level: intermediate
minutes: 5
summary: Choose metric types and aggregation that preserve meaningful latency measurements.
sourceLesson: rel-observability
---

Recovery and overload controls require evidence. Metrics, logs and traces answer different questions. This unit focuses on metric types, costs and aggregation, building on the percentile definitions in Fundamentals.

**Monitoring** tells you *that* something is wrong. **Observability** is the property that lets you work out *why*, including for failures you never predicted, by asking new questions of the telemetry your system already emits.

A system is observable when an on-call engineer can go from "checkout p99 doubled" to "it's the new connection-pool setting on one shard of the inventory service" without deploying new code.

## The three signals

| Signal | Shape | Best for |
|---|---|---|
| Metrics | numbers over time | alerting, trends |
| Logs | discrete events | detail, forensics |
| Traces | causal request tree | latency, dependencies |

Each has a different cost and a different job. Mature systems link them: a metric spike leads to exemplar traces, and a trace span links to the logs it emitted.

## Metrics

A metric is a numeric measurement aggregated over time, identified by a name and labels:

This wrapped Prometheus exposition sample shows one counter value and its labels. Actual exposition writes the complete sample on one line; the wrapping here is only for the phone display.

```text-output
# 1432 is cumulative requests, not req/s.
http_requests_total{
  service="checkout",
  route="/pay",
  status="500"
} 1432
```

The common types (as in Prometheus and OpenTelemetry):

- **Counter metric**: accumulates nonnegative increments, with resets such as on restart (requests, errors, bytes). You graph its *rate*.
- **Gauge metric**: goes up and down (queue depth, memory in use).
- **Histogram**: counts observations into buckets, so you can compute percentiles across many hosts.

With fixed-cardinality, periodically exported aggregates, metric storage primarily scales with series count, sample frequency and retention rather than individual requests. Instrumentation work still scales with observations. A million requests per second still produces one time series per combination.

> [!warning] Cardinality explosions
> Never put unbounded values like user IDs, request IDs or full URLs in metric labels. Every distinct combination of label values is a separate time series, so increasing label diversity increases storage and indexing work.

Label choices determine how many series can exist:

Every distinct combination of labels creates a series. Adding user identity can multiply even a small set of routes, statuses and hosts into an enormous collection; classic histogram buckets add further series.

Only combinations that occur create series. An unbounded label has no configured cardinality ceiling.

### Percentiles, not averages

Averages hide the tail. A mean alone does not describe the slowest users:

If 99 requests take 10 milliseconds and one takes five seconds, the mean is about 60 milliseconds. That single mean does not reveal the five-second experience. Inspect the distribution and explicit latency-threshold counts.

Use percentiles instead. The **p99** (99th percentile) is the latency that 99% of requests beat; p50 is the median. Track p50, p95, p99 and p99.9.

You **cannot average percentiles** across hosts (the mean of each host's p99 is not the fleet p99). Aggregate histograms first, then compute percentiles.

Histograms have their own catch: a percentile computed from buckets is an estimate, interpolated within the bucket it falls in. Put bucket boundaries at the thresholds you care about. For a classic histogram and an SLO of "at most 300 ms", put an upper-inclusive bucket edge at exactly 300 ms. This counts that threshold without within-bucket interpolation; strict "under" has different boundary semantics, and scraped rates still have measurement-window limitations.

## Key takeaways

- Counters measure accumulated events, gauges current state and histograms distributions.
- Bound labels: series combinations multiply, with histogram buckets adding series of their own.
- Aggregate histograms before percentiles and include bucket edges at the SLI thresholds you must count.

## Further reading

- [Observability primer (OpenTelemetry)](https://opentelemetry.io/docs/concepts/observability-primer/)
- [Monitoring distributed systems (Google SRE book)](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Prometheus histograms and summaries](https://prometheus.io/docs/practices/histograms/)
