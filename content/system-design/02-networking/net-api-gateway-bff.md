---
id: net-api-gateway-bff
title: "API policy and backends for frontends"
level: intermediate
minutes: 3
summary: "Centralise external API policy and move chatty client calls onto the service network."
sourceLesson: net-proxies-gateways-mesh
---
External clients need a stable API even when many internal services implement it. A gateway handles shared API policy; a backend for frontend adapts the service calls and response to one client experience.

## API gateways

An API gateway is a reverse proxy specialised for **APIs consumed by external clients**. Products include AWS API Gateway, Kong, Apigee, Azure API Management, and Envoy-based gateways.

On top of reverse-proxy features, it adds **API-level concerns**:

- **Authentication and authorisation:** validate JWTs, OAuth tokens or API keys once, at the front door, and pass the identity downstream.
- **Rate limiting and quotas** per API key or customer ("1,000 requests per minute on the free plan").
- **Routing to many services:** `/orders` → order service, `/users` → user service, so clients see one API.
- **Request/response transformation:** protocol translation (REST to gRPC), versioning, field filtering.
- **Developer-facing features:** API keys, usage analytics, billing, documentation portals.

### Backends for frontends

The **BFF** pattern uses a separate gateway (or thin service) per client type: one for the mobile app, one for the web app. Each aggregates and shapes data for its client, for example combining five service calls into one response so a phone on a slow network makes one round trip instead of five.

> [!analogy] Real-world analogy: A reception desk and a personal assistant
> Every visitor to a large office passes one reception desk, which checks identification, signs them in, enforces visiting rules and tells them where to go. A busy executive might instead send a personal assistant, who visits five departments in the building and comes back with one folder.
>
> **How it maps:** reception is the API gateway: one front door applying shared policy (authentication, quotas, routing) before requests reach the services. The assistant is a backend for frontend, making several dependent internal calls on the client's behalf so the slow outside trip happens once.
>
> **Where it stops:** reception checks a visitor once at the door, but a gateway checks every single request, so when it is slow or down every API suffers. A BFF serves every user of one kind of client (all phone users, say), not one person. And unlike a trusted receptionist's badge, passing the gateway does not settle access: each service must still check whether this caller may see this particular resource.

### Gateway pitfalls

- **Business logic creep.** Gateways become a dumping ground for logic that belongs in services, creating a fragile, centrally owned bottleneck. Keep them about *cross-cutting* concerns.
- **Single point of failure.** All external traffic flows through it; it needs redundancy across zones and careful change management.
- **Added latency.** Each hop adds work and can add latency; the amount depends on topology, load, buffering, protocol and enabled plug-ins.

## Key takeaways

- A gateway is a natural place for external authentication, customer quotas and API routing.
- A BFF shapes one response for its client type and moves dependent calls onto the backend network.
- Keep business logic in services and make the gateway resilient; its extra processing also has a cost.

## Further reading

- [API gateway and BFF pattern (microservices.io)](https://microservices.io/patterns/apigateway.html)
- [What is Amazon API Gateway?](https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html)
