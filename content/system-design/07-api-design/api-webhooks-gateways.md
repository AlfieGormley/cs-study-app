---
id: api-webhooks-gateways
title: Webhooks, API gateways and BFFs
level: advanced
minutes: 15
summary: Delivering webhooks reliably and securely (signing, retries, ordering, replay protection), and what API gateways and backends-for-frontends do in practice.
---

The previous lesson covered pushing data to *browsers*. Webhooks push data to *other servers*: Stripe tells your backend a payment succeeded, GitHub tells your CI that code was pushed, Shopify tells your app an order was placed.

This lesson then zooms out to the infrastructure that sits in front of your APIs: gateways and backends-for-frontends.

## Webhooks: reverse APIs

A webhook is an HTTP `POST` that **the provider** sends to a URL **the consumer** registered. It's an API call in the opposite direction.

```
Provider            Your server
(Stripe)            /webhooks/stripe
   |                     |
   | payment succeeded   |
   |--- POST event ----->|
   |                     | verify sig
   |                     | enqueue
   |<----- 200 OK -------|
   |                     | process async
```

A typical delivery:

```
POST /webhooks/stripe HTTP/1.1
Content-Type: application/json
Stripe-Signature: t=1767225600,
  v1=5257a869e7ecebeda32a...

{"id": "evt_1Nq...",
 "type": "payment_intent.succeeded",
 "created": 1767225600,
 "data": {"object": {...}}}
```

The alternative is the consumer polling `GET /events?since=...`. Webhooks are more efficient and faster, but they shift a lot of reliability problems onto both sides.

## Problem 1: authenticity

Your webhook URL is public. Anyone who discovers it can `POST` a fake "payment succeeded" event and get free goods. You must verify that each request genuinely came from the provider.

A common technique is an **HMAC signature** (a shared-secret message authentication code). Follow the provider-specific signing protocol; asymmetric signatures are another option. Provider and consumer share a secret (`whsec_...`). The provider computes:

```
signed = timestamp + "." + raw_body
sig = HMAC_SHA256(secret, signed)
```

and sends `t=<timestamp>,v1=<sig>` in a header. The consumer recomputes the HMAC and compares.

Details that matter:

- **Use the raw body bytes.** If your framework parses and re-serialises the JSON first, whitespace or key order changes and the signature won't match.
- **Compare in constant time** (`hmac.compare_digest`, `crypto.timingSafeEqual`). Ordinary equality checks are not guaranteed constant-time and can expose timing differences; use a vetted constant-time comparison for appropriately validated equal-length inputs.
- **Support multiple secrets during rotation.** Stripe and the Standard Webhooks spec allow several signatures in one header so old and new secrets both verify during the changeover.

GitHub uses `X-Hub-Signature-256: sha256=<hmac>`, computed over the body alone, with no timestamp. The **Standard Webhooks** specification (backed by Svix, Zapier, Twilio and others) standardises `webhook-id`, `webhook-timestamp` and `webhook-signature` headers, and signs `id.timestamp.body`, so the message id and timestamp are both covered.

## Problem 2: replay attacks

An attacker who captures one genuine, correctly signed webhook (from a log, a misconfigured proxy) can resend it later. The signature is still valid.

Defences:

- **Sign the timestamp** along with the body (as above), and **reject events whose timestamp is too old**. Stripe's libraries default to a 5-minute tolerance.
- **Deduplicate by event id.** Store processed `evt_...` ids and ignore repeats. You need this anyway for retries (below). For GitHub, `X-GitHub-Delivery` is useful for ordinary redelivery deduplication, but it is not included in the body HMAC: someone replaying a captured body can change that header. Use authenticated payload identity or a retained digest of the verified raw body where appropriate, make business effects idempotent, and reconcile current provider state. Without signed freshness or retained identity, the signature alone cannot reject an old valid payload.

> [!warning] Why the timestamp must be inside the signature
> If the timestamp were sent separately and unsigned, an attacker could replay an old body with a fresh timestamp. Including it in the signed string means changing it breaks the signature.

## Problem 3: delivery failures and retries

Your endpoint will sometimes be down, slow or buggy. Many providers retry failed delivery with backoff, so duplicates are possible. Bounded retry windows do not guarantee that every event is eventually delivered. Stripe retries for up to **3 days** in live mode (far less in test mode); GitHub doesn't retry failed deliveries automatically, but lets you redeliver them from the UI or API.

What this means for you as a consumer:

- **Respond 2xx quickly**, within a few seconds. Providers time out (GitHub asks for a 2xx within 10 seconds) and treat slow responses as failures, which causes retries and duplicate work.
- **Do the work asynchronously.** Verify the signature, write the event to a queue or table, return `200`, then process. Your downstream outage then doesn't become a webhook failure.
- **Be idempotent.** You *will* receive the same event more than once. Deduplicate on the authenticated event identity, in the same transaction as a local database side effect. External effects need downstream idempotency or reconciliation; a local transaction cannot atomically commit a remote API call.

```
BEGIN;
INSERT INTO processed_events(id)
  VALUES ('evt_1Nq')
  ON CONFLICT DO NOTHING;
-- if 0 rows inserted: duplicate,
--   COMMIT and return
UPDATE orders SET paid = true ...;
COMMIT;
```

As a **provider**, you need:

- A durable outbox of events, a delivery worker pool, and per-endpoint retry schedules (e.g. 1 min, 5 min, 30 min, 2 h, 8 h...).
- **Auto-disable** endpoints that fail for days, and email the owner.
- **Isolation** between customers, so one customer's slow endpoint doesn't block deliveries to everyone else.
- An **events API** (`GET /events`) so consumers can reconcile anything missed. Webhooks should be a notification channel, not the only source of truth.

## Problem 4: ordering

Webhooks can arrive **out of order**. Retries, parallel workers and network variation mean `subscription.updated` can arrive before `subscription.created`. Stripe explicitly says it doesn't guarantee delivery order.

Strategies:

- **Use trustworthy per-object versions.** Atomically apply only newer versions. Timestamps work only if their ordering and tie-breaking are reliable for that object; event creation time is not automatically an object version.
- **Treat events as hints ("thin events").** On any event for object X, call `GET /objects/X` to fetch its current state. This avoids applying stale event payloads, but concurrent fetches can still complete out of order. Serialize refreshes per object or apply a trustworthy version check when storing the fetched state. Stripe's newer "thin" events take this approach: the payload contains little more than the id.
- **Strict per-key ordering** on the provider side (one in-flight delivery per object with ordered retries) trades throughput and head-of-line blocking for ordering. A consumer that acknowledges before asynchronous processing must preserve order there too.

| Problem | Consumer fix |
|---|---|
| Fake events | Verify HMAC (raw body) |
| Replays | Signed timestamp + tolerance |
| Duplicates | Dedupe on event id |
| Timeouts | Ack fast, process async |
| Out of order | Version check or re-fetch |
| Missed events | Reconcile via events API |

## API gateways

As systems grow into dozens of services, you don't want every service to re-implement auth, rate limiting and TLS. An **API gateway** is a reverse proxy that handles these cross-cutting concerns at the edge.

```
   clients
      |
+------------+
| API gateway|  TLS, auth,
|            |  rate limit,
+------------+  routing, logs
  |    |    |
 svc  svc  svc
```

Typical responsibilities:

- **Routing**: `/orders/*` to the orders service, `/v2/*` to new deployments, canary splits.
- **Authentication**: validate JWTs or API keys, then pass a verified identity downstream.
- **Rate limiting and quotas** per API key or plan.
- **TLS termination**, request size limits, WAF rules.
- **Observability**: request ids, access logs, metrics, tracing headers.
- **Transformation**: header injection, protocol translation (REST to gRPC).

Examples: Kong, AWS API Gateway, Apigee, Azure API Management, Envoy-based gateways. Load balancing itself is covered in the networking module; a gateway is an L7 proxy with API-aware features layered on top.

> [!warning] Don't turn the gateway into a monolith
> Keep business logic out. Once the gateway starts aggregating responses, applying domain rules and knowing about order states, every team's change has to go through it, and it becomes the bottleneck you split your monolith to escape.

Also remember the gateway is on every request's path: it must be horizontally scaled, highly available and fast. A gateway that adds 30 ms to every call becomes a big chunk of your latency budget.

## Backend-for-frontend (BFF)

Different clients need different things. The iOS app wants small payloads tuned for a phone screen. The web app shows richer pages. A partner integration wants stable, generic resources. One general-purpose API ends up serving all of them badly.

The **backend-for-frontend** pattern, popularised by Sam Newman and based on work at SoundCloud, can give each distinct client experience its **own** thin backend, owned by the team that builds that frontend.

```
 iOS     Android    Web
  |        |         |
+----+  +----+   +-----+
|BFF |  |BFF |   | BFF |
|mob |  |mob |   | web |
+----+  +----+   +-----+
   \       |       /
  +----------------+
  |  core services |
  +----------------+
```

What a BFF does:

- **Aggregates** several downstream calls into one response shaped for a specific screen, cutting mobile round trips.
- **Trims** payloads to what that client needs.
- **Handles client-specific concerns**: for browsers, it can hold OAuth tokens server-side and give the browser only an `HttpOnly` session cookie (the "token handler" pattern), keeping tokens out of JavaScript.
- **Evolves with its frontend**, so the mobile team can ship a new screen without waiting for a core-services change.

Trade-offs:

- **Duplication** across BFFs (two mobile BFFs often converge). Share libraries, or merge them if the clients are near-identical.
- **More services to run.**
- Like the gateway, keep **domain logic in core services**. A BFF should orchestrate and shape, not decide business rules.

GraphQL can be an alternative or a complement: clients select response fields through a shared schema. Client-specific authentication, aggregation policy and ownership may still justify BFFs.

## Gateway vs BFF

| | API gateway | BFF |
|---|---|---|
| Count | One (or few) | One per client type |
| Owner | Platform team | Frontend team |
| Focus | Cross-cutting | Client-specific shape |
| Logic | Policy only | Aggregation |

They usually coexist: the gateway handles TLS, auth and rate limits at the edge, then routes to the right BFF.

## Key takeaways
- A **webhook** is an HTTP POST from provider to consumer: an API in reverse. Expect duplicates, gaps and out-of-order delivery unless the provider contract guarantees otherwise.
- **Verify HMAC signatures** over the **raw body**, compare in **constant time**, and include a **signed timestamp** with a short tolerance to reject stale replays; deduplication handles repeats within that window.
- **Acknowledge fast, process asynchronously, dedupe on event id**, and handle out-of-order events with versions or by **re-fetching** current state.
- Providers need durable outboxes, per-endpoint retries with backoff, isolation, auto-disable and an events API for reconciliation.
- An **API gateway** centralises cross-cutting concerns (auth, rate limits, routing, TLS, observability). Keep business logic out.
- A **BFF** gives each client type its own thin backend for aggregation and shaping, owned by the frontend team.

## Further reading
- [Stripe docs: Receive Stripe events in your webhook endpoint](https://docs.stripe.com/webhooks)
- [Stripe docs: Verify webhook signatures](https://docs.stripe.com/webhooks/signature)
- [GitHub docs: Validating webhook deliveries](https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries)
- [GitHub docs: Best practices for using webhooks](https://docs.github.com/en/webhooks/using-webhooks/best-practices-for-using-webhooks)
- [Standard Webhooks specification](https://github.com/standard-webhooks/standard-webhooks/blob/main/spec/standard-webhooks.md)
- [Sam Newman: Backends for frontends](https://samnewman.io/patterns/architectural/bff/)
- [Microsoft Azure Architecture Center: Backends for Frontends pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/backends-for-frontends)
- [Microsoft Azure Architecture Center: API gateways](https://learn.microsoft.com/en-us/azure/architecture/microservices/design/gateway)
