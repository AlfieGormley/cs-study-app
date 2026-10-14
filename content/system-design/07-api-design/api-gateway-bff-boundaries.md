---
id: api-gateway-bff-boundaries
title: API gateways and backends for frontends
level: advanced
minutes: 4
summary: Separate edge policy from client-specific response shaping and keep business rules in core services.
sourceLesson: api-webhooks-gateways
---

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

GraphQL can be an alternative or a complement: clients select response fields through a shared GraphQL schema. Client-specific authentication, aggregation policy and ownership may still justify BFFs.

## Gateway vs BFF

| | API gateway | BFF |
|---|---|---|
| Count | One (or few) | One per client type |
| Owner | Platform team | Frontend team |
| Focus | Cross-cutting | Client-specific shape |
| Logic | Policy only | Aggregation |

They usually coexist: the gateway handles TLS, auth and rate limits at the edge, then routes to the right BFF.

## Key takeaways
- Gateways centralise routing, identity checks, limits, TLS and observability.
- A BFF is owned with its frontend and aggregates or trims responses for that experience.
- Gateways and BFFs both need operational capacity and clear domain boundaries.
- GraphQL and BFFs can complement each other; neither removes client-specific ownership decisions.

## Further reading
- [Sam Newman: Backends for frontends](https://samnewman.io/patterns/architectural/bff/)
- [Microsoft Azure Architecture Center: Backends for Frontends pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/backends-for-frontends)
- [Microsoft Azure Architecture Center: API gateways](https://learn.microsoft.com/en-us/azure/architecture/microservices/design/gateway)
