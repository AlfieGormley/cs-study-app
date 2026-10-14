---
id: cs1-url-http-cache-click-analytics
title: Choose redirect caching and asynchronous analytics
level: intermediate
minutes: 3
summary: Choose Cache-Control explicitly for freshness and repeat click visibility.
sourceLesson: cs1-url-shortener
---

A redirect that is reused by a browser or edge cache may never reach the origin. This unit connects HTTP caching semantics to click visibility and the analytics pipeline.

## Deep dive 2: 301 vs 302

Both send the browser to the long URL. The difference is caching.

| | 301 Permanent | 302 Found |
|---|---|---|
| Heuristic cacheability | Yes | Not normally; explicit freshness can permit storage |
| Later clicks hit us? | Depends on freshness policy | Depends on freshness policy |
| Analytics | Cached visits may be missed | Cached visits may be missed |
| Updated target seen? | Depends on cache policy | Depends on cache policy |

A fresh cached redirect can bypass your service, hiding visits and delaying target or expiry changes. A **301** is heuristically cacheable; **302/307** can also be cached with explicit freshness. Use an explicit policy such as `Cache-Control: no-store` when repeat navigation should resolve through your service, and account for analytics delivery failures separately.

Without explicit cache headers, browsers treat a 301 as cacheable and may keep it indefinitely; a 302 is cached only if headers say so. A permanent redirect can still use a short freshness lifetime or `no-store`; the status and cache policy serve different purposes.

> [!note] Content gap: live provider headers
> Exact Bitly, t.co and TinyURL cache-header claims have been removed. No reproducible set of representative URLs and dated response captures was supplied, so this audit cannot reliably present those variable deployment settings as provider-wide facts.

So the real lever is `Cache-Control`, not only the status code. Say the trade-off explicitly; that's what the interviewer is checking.

## Deep dive 3: Analytics

Never update a counter row synchronously on every redirect. At 30,000 redirects/s, a popular link would become a hot row and add latency to every redirect.

Instead:

1. The redirect service emits a click event (`code, timestamp, country from IP, user agent, referrer`) to Kafka, fire-and-forget, and returns immediately.
2. A stream processor (Flink, Kafka Streams) aggregates events into per-link, per-hour buckets.
3. Aggregates go into an OLAP store such as ClickHouse or Druid, which answers "clicks by country last 7 days" quickly.

Raw events can also be written to object storage (S3) for reprocessing. If Kafka is briefly unavailable, the redirect must still work: buffer locally and drop analytics before you ever fail a redirect. Redirects are the product; analytics are a feature.

## Make the analytics guarantee explicit

Returning quickly and recording every click are competing requirements during a log outage. A fire-and-forget event can be lost between process failure and publication, even if Kafka itself is durable after acknowledgement. A bounded local queue needs a size limit, retention policy and metric for dropped events.

If the product requires durable click accounting, persist a recoverable event before acknowledging the operation or use an equivalent durable capture design, then measure its latency cost. For this availability-first shortener, redirect success takes priority and occasional missing analytics are accepted. Neither a 302 nor a no-store policy proves complete analytics: clients, bots and event delivery failures still need a measurement definition.

## Key takeaways

- Choose Cache-Control explicitly for freshness and repeat click visibility.
- Status codes and freshness policy are separate decisions.
- Keep analytics bounded and asynchronous; quantify tolerated event loss.

## Further reading

- [RFC 9111: HTTP caching](https://www.rfc-editor.org/rfc/rfc9111.html)
- [RFC 9110: redirect status codes](https://www.rfc-editor.org/rfc/rfc9110.html)
