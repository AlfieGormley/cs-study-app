---
id: rel-structured-log-cost-context
title: Structured log context and cost
level: intermediate
minutes: 3
summary: Make logs queryable, safe and affordable without losing useful error evidence.
sourceLesson: rel-observability
---

Metrics summarise a service over time. Logs preserve individual events and the fields needed to reconstruct them. A request ID groups one request’s messages; a trace ID can correlate its journey across services, introduced fully in the next unit.

## Logs

Logs record discrete events with context. The single most valuable practice is **structured logging**: emit machine-parseable key-value records (usually JSON) rather than free-form text.

An unstructured event:

```text-output
"Payment failed for user 42 after 3012ms"
```

The same event as a JSON record, with duration in milliseconds and a correlation ID:

```json
{"ts":"2026-10-01T09:14:03Z",
 "level":"error",
 "msg":"payment failed",
 "user_id":42,
 "duration_ms":3012,
 "provider":"stripe",
 "trace_id":
   "4bf92f3577b34da6a3ce929d0e0e4736"}
```

With structured logs you can filter and group fields instead of writing fragile regexes. For example, in a SQL-accessible log table, this native query selects slow Stripe events:

```sql
-- Filter fields, not the free-form message.
SELECT provider, duration_ms, trace_id
FROM payment_logs
WHERE provider = 'stripe'
  AND duration_ms > 2000;
```

The table and field types depend on the logging backend. The shown record matches this filter because its 3,012-millisecond duration is above two seconds.

Good logging practice:

- Include a **trace ID** and request ID on every line, so logs can be joined to traces.
- Log at boundaries (request in, response out, external call) and on errors, not in tight loops.
- Never log secrets, tokens, passwords or full card numbers; redact PII.
- Sample high-volume debug logs; prioritize errors, but rate-limit or deduplicate error storms while preserving counters and useful examples.

Log cost depends on event size, indexing, volume and retention. Estimate raw volume from request rate, log bytes per request and elapsed time:

```formula
V = rbt
V = 50,000 /s × 1 KB × 86,400 s
V = 4,320,000,000 KB ≈ 4.3 TB
V_30 = 4.32 TB × 30 ≈ 130 TB
where
V: the log volume produced in one day
V_30: the volume kept over a 30-day retention period
r: the request rate, here 50,000 requests per second (/s)
b: the log bytes written per request, here 1 kilobyte (KB)
t: the time period, here one day = 86,400 seconds (s)
KB: kilobytes; 1 TB = 1,000,000,000 KB (decimal units)
TB: terabytes
s: seconds
≈: approximately equal to (rounded)
In words: 50,000 requests a second at 1 KB each is about 4.3 terabytes of logs a day, roughly 130 TB if you keep 30 days.
```

Indexing, replication and compression can make the stored size larger or smaller than this raw figure.

## Key takeaways

- Structured fields and trace IDs make events filterable and joinable.
- Record useful boundaries and errors, redact secrets and personal data, and control error storms.
- Estimate raw log volume before choosing retention; indexing, compression and replicas change stored size.

## Further reading

- [Observability primer (OpenTelemetry)](https://opentelemetry.io/docs/concepts/observability-primer/)
- [Monitoring distributed systems (Google SRE book)](https://sre.google/sre-book/monitoring-distributed-systems/)
