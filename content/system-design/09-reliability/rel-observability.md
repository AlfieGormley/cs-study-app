---
id: rel-observability
title: Observability with logs, metrics and traces
level: intermediate
minutes: 13
summary: Use structured logs, metrics and distributed traces together, apply the RED and USE methods, and instrument with OpenTelemetry.
---

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

```
http_requests_total{
  service="checkout",
  route="/pay",
  status="500"
} 1432
```

The common types (as in Prometheus and OpenTelemetry):

- **Counter**: accumulates nonnegative increments, with resets such as on restart (requests, errors, bytes). You graph its *rate*.
- **Gauge**: goes up and down (queue depth, memory in use).
- **Histogram**: counts observations into buckets, so you can compute percentiles across many hosts.

With fixed-cardinality, periodically exported aggregates, metric storage primarily scales with series count, sample frequency and retention rather than individual requests. Instrumentation work still scales with observations. A million requests per second still produces one time series per combination.

> [!warning] Cardinality explosions
> Never put unbounded values like user IDs, request IDs or full URLs in metric labels. 10 routes × 5 status codes × 100 hosts = 5,000 series, fine. Adding `user_id` with 1 million users permits up to 5 billion label combinations if all combinations occur, likely exceeding ordinary metrics capacity.

### Percentiles, not averages

Averages hide the tail. If 99 requests take 10 ms and one takes 5 s, the mean is ~60 ms: it looks fine, but 1% of users wait 5 seconds. Use p50, p95, p99 and p99.9.

You **cannot average percentiles** across hosts (the mean of each host's p99 is not the fleet p99). Aggregate histograms first, then compute percentiles.

Histograms have their own catch: a percentile computed from buckets is an estimate, interpolated within the bucket it falls in. Put bucket boundaries at the thresholds you care about. For a classic histogram and an SLO of "at most 300 ms", put an upper-inclusive bucket edge at exactly 300 ms. This counts that threshold without within-bucket interpolation; strict "under" has different boundary semantics, and scraped rates still have measurement-window limitations.

## Logs

Logs record discrete events with context. The single most valuable practice is **structured logging**: emit machine-parseable key-value records (usually JSON) rather than free-form text.

```
Unstructured:
"Payment failed for user 42 after 3012ms"

Structured:
{"ts":"2026-10-01T09:14:03Z",
 "level":"error",
 "msg":"payment failed",
 "user_id":42,
 "duration_ms":3012,
 "provider":"stripe",
 "trace_id":
   "4bf92f3577b34da6a3ce929d0e0e4736"}
```

With structured logs you can query `provider=stripe AND duration_ms>2000` and group by any field, instead of writing fragile regexes.

Good logging practice:

- Include a **trace ID** and request ID on every line, so logs can be joined to traces.
- Log at boundaries (request in, response out, external call) and on errors, not in tight loops.
- Never log secrets, tokens, passwords or full card numbers; redact PII.
- Sample high-volume debug logs; prioritize errors, but rate-limit or deduplicate error storms while preserving counters and useful examples.

Log cost depends on event size, indexing, volume and retention. At 50,000 req/s with 1 KB of logs per request, you produce ~4.3 TB per day, or around 130 TB over a 30-day retention period.

## Distributed traces

In a microservice system, one user request may touch 20 services. A **trace** records that request's whole journey as a tree of **spans**. Each span has a name, start time, duration and attributes; root spans have no parent. Span links can represent additional causal relationships, including across traces.

```
trace 4bf92f…  total 840ms
├ gateway        ████████████ 840
│ ├ auth         █ 30
│ └ checkout     ██████████ 790
│   ├ cart       ██ 60
│   ├ inventory  ███████ 610  ← slow
│   └ payment    █ 90
```

Here the waterfall shows instantly that inventory, not payment, is the problem. Metrics alone would only tell you checkout is slow.

### Context propagation

For the spans to join into one tree, each service must pass the trace context to the next. The W3C **Trace Context** standard defines a `traceparent` header:

```
traceparent:
 00-4bf92f3577b34da6a3ce929d0e0e4736
 -00f067aa0ba902b7-01
 ver-trace id-parent span id-flags
```

For linked instrumentation, propagate context using the supported carrier (such as HTTP/gRPC metadata or message properties). The displayed header is wrapped for readability; its wire value is one uninterrupted line. One service that drops the header breaks the trace into disconnected pieces; async boundaries like queues need explicit attention.

### Sampling

Tracing every request at high volume is expensive. Strategies:

- **Head-based sampling**: decide at the start (e.g. keep 1%). The decision travels with the trace (the last field of `traceparent` contains flags, including the sampled bit). Parent-based sampling can keep decisions consistent, but this flag is a recommendation and downstream policy can differ. Cheap and simple, but you'll miss most rare errors.
- **Tail-based sampling**: buffer spans for a decision window and apply outcome-based policies, such as retaining errors and slow traces plus a sample of normal ones. Late spans, missing instrumentation, upstream sampling or buffer overflow can prevent retention of every interesting trace. Better signal, but needs a collector tier with memory to hold in-flight traces, and every span of a trace must reach the same collector instance (OpenTelemetry uses a load-balancing exporter keyed on trace ID for this).

Google's Dapper paper, which inspired Zipkin and Jaeger, sampled as few as 1 in 1,024 traces and still found it useful for aggregate latency analysis.

## OpenTelemetry

**OpenTelemetry (OTel)** is the CNCF standard for generating and exporting telemetry. It provides vendor-neutral APIs and SDKs for traces, metrics and logs, plus automatic instrumentation for common frameworks, and the **OTel Collector**, which receives, processes (batching, sampling, redacting) and exports data to supported backends through configured exporters.

```
[service + OTel SDK]──OTLP──┐
[service + OTel SDK]──OTLP──┤
                            ▼
                    [OTel Collector]
                     │ sample, batch
          ┌──────────┼─────────┐
          ▼          ▼         ▼
       traces     metrics     logs
      backend     backend   backend
```

Because instrumentation targets the OTel API rather than a vendor SDK, you can often switch compatible backends by reconfiguring collector exporters; backend-specific features, schemas and unsupported signals may require additional migration work.

## What to measure: RED and USE

Two complementary checklists stop you drowning in metrics.

### RED: for every service (request-driven)

Tom Wilkie's **RED method**, for each service or endpoint:

- **Rate**: requests per second.
- **Errors**: failed requests per second (or ratio).
- **Duration**: latency distribution (histogram).

RED describes what users experience, which makes it a good basis for dashboards and SLIs.

### USE: for every resource

Brendan Gregg's **USE method**, for each resource (CPU, memory, disk, network, connection pools, queues):

- **Utilisation**: how busy a resource is, such as busy-time percentage for a device or used capacity for memory and pools.
- **Saturation**: extra work it can't service yet (run-queue length, swap, queue depth).
- **Errors**: error events (disk errors, dropped packets).

USE helps diagnose *why* a service's RED metrics went bad.

| Method | Applies to | Answers |
|---|---|---|
| RED | services | Are users OK? |
| USE | resources | What's the bottleneck? |

Google's SRE book recommends the **four golden signals**: latency, traffic, errors and saturation. That's essentially RED plus the most important USE question: how full is the service?

> [!tip] Alert on symptoms, investigate with causes
> Page a human on symptoms users feel (RED metrics, SLO burn). Use cause metrics (USE: CPU, disk, GC) on dashboards for diagnosis. Paging on "CPU > 80%" wakes people for things that may not matter to users.

## Key takeaways

- Metrics are cheap and great for alerting; logs give detail; traces show where time goes across services. Link them with trace IDs.
- Keep metric label cardinality bounded and use histograms for percentiles; never average percentiles.
- Structured (JSON) logs with trace IDs make logs queryable and joinable; never log secrets.
- Traces depend on context propagation (W3C `traceparent`) across every hop, including queues; use tail-based sampling to keep the interesting traces.
- OpenTelemetry gives vendor-neutral instrumentation and a collector to process and route telemetry.
- RED (rate, errors, duration) for services; USE (utilisation, saturation, errors) for resources.

## Further reading

- [Observability primer (OpenTelemetry)](https://opentelemetry.io/docs/concepts/observability-primer/)
- [Traces (OpenTelemetry)](https://opentelemetry.io/docs/concepts/signals/traces/)
- [Context propagation (OpenTelemetry)](https://opentelemetry.io/docs/concepts/context-propagation/)
- [Trace Context (W3C Recommendation)](https://www.w3.org/TR/trace-context/)
- [The USE method (Brendan Gregg)](https://www.brendangregg.com/usemethod.html)
- [The RED method (Grafana Labs)](https://grafana.com/blog/2018/08/02/the-red-method-how-to-instrument-your-services/)
- [Monitoring distributed systems (Google SRE book)](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Dapper, a large-scale distributed systems tracing infrastructure (Google Research)](https://research.google/pubs/pub36356/)
