---
id: rel-trace-context-tail-collection
title: Trace context and tail collection
level: intermediate
minutes: 3
summary: Keep causal traces connected across services and route them for outcome-based sampling.
sourceLesson: rel-observability
---

A slow checkout metric tells you that users wait. A trace shows where that time went. This unit assumes counters and distributions from the metric unit; resource diagnosis with USE follows next.

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

**OpenTelemetry (OTel)** is a CNCF project providing vendor-neutral APIs and protocols for generating and exporting telemetry. It provides vendor-neutral APIs and SDKs for traces, metrics and logs, plus automatic instrumentation for common frameworks, and the **OTel Collector**, which receives, processes (batching, sampling, redacting) and exports data to supported backends through configured exporters.

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

Because instrumentation targets the OTel API rather than a vendor SDK, you can often switch compatible backends by reconfiguring collector exporters; backend-specific features, telemetry data formats and unsupported signals may require additional migration work.

## Key takeaways

- Trace spans record a request’s journey; propagate supported context across network and queue boundaries.
- Head sampling is cheap; tail sampling needs buffered spans and trace-consistent collector routing.
- OpenTelemetry supplies APIs, SDKs and a collector; backend migrations can still require work.

## Further reading

- [Traces (OpenTelemetry)](https://opentelemetry.io/docs/concepts/signals/traces/)
- [Context propagation (OpenTelemetry)](https://opentelemetry.io/docs/concepts/context-propagation/)
- [Trace Context (W3C Recommendation)](https://www.w3.org/TR/trace-context/)
- [Dapper, a large-scale distributed systems tracing infrastructure (Google Research)](https://research.google/pubs/pub36356/)
- [OpenTelemetry tail sampling](https://opentelemetry.io/docs/concepts/sampling/)
- [OpenTelemetry Python propagation API](https://opentelemetry-python.readthedocs.io/en/latest/api/propagate.html)
