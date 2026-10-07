---
id: net-proxies-gateways-mesh
title: Reverse proxies, API gateways and service meshes
level: intermediate
minutes: 13
summary: What reverse proxies, API gateways and service meshes each do, where they sit, how they overlap, and when each one is worth its cost.
---

Reverse proxies, API gateways and service meshes are often built from the same software (Envoy, NGINX, HAProxy) and share many features. The difference is mostly **where they sit** and **whose problems they solve**:

- A **reverse proxy** fronts a set of servers.
- An **API gateway** fronts a set of *APIs* for external clients.
- A **service mesh** handles traffic *between* your services.

```
         Internet
            |
     [CDN / edge proxy]
            |
      [API gateway]      <- north-south
            |
   +--------+--------+
   |                 |
[svc A]+sidecar  [svc B]+sidecar
   |     <---- mesh ---->  |
   |   (east-west, mTLS)   |
```

"North-south" traffic enters and leaves your system; "east-west" traffic flows between services inside it.

## Forward vs reverse proxy

A **forward proxy** acts for *clients*: a corporate proxy that all employees' browsers go through. The server sees the proxy, not the user.

A **reverse proxy** acts for *servers*: clients think they're talking to `example.com`, but they're talking to a proxy that forwards to hidden backends.

## Reverse proxies

A reverse proxy (NGINX, HAProxy, Envoy, Caddy, Traefik) typically handles:

| Job | Why at the proxy |
|---|---|
| TLS termination | One place for certs |
| Load balancing | Hide backend topology |
| Compression | Offload CPU from apps |
| Static files, caching | Fast, no app involved |
| Buffering | Protect slow apps |
| Request limits | Size, timeouts, rate |

**Buffering** deserves a mention. A slow mobile client might take 10 s to upload a request or download a response. If an app server process (say a Python worker) talked to it directly, that worker would be stuck for 10 s. With request/response buffering enabled and enough buffer or temporary-file capacity, NGINX can decouple a synchronous worker from a slow client. The worker remains busy for response generation and transfer to the proxy, not necessarily only milliseconds. Streaming, buffer limits and disabled buffering change this behavior. This is why NGINX in front of Gunicorn or Puma is standard practice.

The proxy also adds headers so the app knows the real client: `X-Forwarded-For` (client IP), `X-Forwarded-Proto` (was it HTTPS?) and the standardised `Forwarded` header (RFC 7239). Each proxy *appends* the address it received the connection from, so after a CDN and a load balancer the header reads `client, CDN`, and the app sees the load balancer as the connection's source address.

> [!warning] Trusting forwarded headers
> Clients can send their own `X-Forwarded-For`. First verify that the direct peer is a trusted proxy, then parse the forwarded chain from the right, skipping only explicitly trusted proxy hops. The first untrusted address is the client boundary; it may itself be an external proxy, not the original person’s device. Ensure attackers cannot bypass the trusted entry path. Otherwise attackers can spoof their IP to bypass rate limits or IP allow-lists.

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

### Gateway pitfalls

- **Business logic creep.** Gateways become a dumping ground for logic that belongs in services, creating a fragile, centrally owned bottleneck. Keep them about *cross-cutting* concerns.
- **Single point of failure.** All external traffic flows through it; it needs redundancy across zones and careful change management.
- **Added latency.** Each hop adds work and can add latency; the amount depends on topology, load, buffering, protocol and enabled plug-ins.

## Service meshes

Inside a microservice system, every service needs the same networking features: retries, timeouts, load balancing, mTLS, metrics and tracing. You can put these in a **library** in each service (Netflix's Hystrix and Ribbon era, or today's gRPC client libraries), but then every language needs its own implementation, and upgrades mean redeploying every service.

A **service mesh** moves them into the infrastructure:

```
[ App A ]          [ App B ]
    |                  ^
    v                  |
[proxy A] ==mTLS==> [proxy B]
    ^                  ^
    |  config, certs   |
    +--[control plane]-+
```

- **Data plane in classic sidecar mode:** a proxy next to each enrolled service instance intercepts configured inbound and outbound traffic; exclusions and unsupported protocols need separate consideration.
- **Control plane:** (Istio's `istiod`, Linkerd's control plane) distributes routing rules, certificates and policies to every proxy.

What you get, without changing app code:

1. **mTLS for enrolled and configured traffic**, with automatic certificate issuance and rotation, plus service identity (e.g. SPIFFE IDs) for authorisation policies like "only `checkout` may call `payments`".
2. **Traffic management:** retries, timeouts, circuit breaking, outlier ejection, and per-request L7 load balancing (which fixes the long-lived HTTP/2 connection imbalance).
3. **Progressive delivery:** send 5% of traffic to `v2`, or route by header for testing.
4. **Uniform observability:** request rates, error rates and latency for service pairs, and proxy tracing spans. End-to-end trace linkage still requires the application to propagate incoming trace context into outgoing calls.

### The costs

- **Latency:** a classic two-sidecar call adds client and server proxy processing; measure its median and tail overhead under your actual load.

> [!note] Measurement gap
> No reproducible gateway or mesh benchmark is supplied here. Fixed per-hop latency and universal per-client memory/capacity estimates are omitted.
- **Resources:** a sidecar per pod, each with its own CPU and memory; across thousands of pods this adds up.
- **Operational complexity:** the control plane is now critical infrastructure. A bad config push can break every service at once.
- **Debugging:** "is it my app or the mesh?" becomes a common question.

Newer designs reduce the overhead: Istio's **ambient mode** replaces per-pod sidecars with a per-node L4 proxy (ztunnel) plus optional shared L7 "waypoint" proxies, and **proxyless gRPC** has the gRPC library receive mesh config directly.

> [!tip] When to adopt a mesh
> A mesh pays off when you have **many services, several languages, and a real need** for mTLS, fine-grained traffic control or uniform telemetry. With five services in one language, a good shared client library and a gateway are usually simpler.

## Comparing the three

| | Reverse proxy | API gateway | Service mesh |
|---|---|---|---|
| Traffic | Into a service | Into the system | Between services |
| Main users | Ops | API consumers | Service teams |
| Typical jobs | TLS, LB, cache | Auth, quotas | mTLS, retries |
| Deployed as | A tier | A tier | Sidecar per pod |

In practice they combine: a CDN at the edge, an API gateway for external APIs (often itself an Envoy deployment, sometimes the mesh's own *ingress gateway*), and a mesh inside.

## Retries: a feature that can hurt

Every layer here can retry, and that's dangerous. If the gateway makes up to 3 attempts, the mesh sidecar makes up to 3 attempts for each of those, and the app's client makes up to 3 for each of *those*, one failing request becomes **3 × 3 × 3 = 27** attempts on the struggling backend: a **retry storm** that turns an overload into an outage. (Careful with wording: "3 retries" usually means 4 attempts, which would make it 4 × 4 × 4 = 64.)

Rules of thumb:

- Retry at **one** layer (usually closest to the caller), and only for idempotent requests.
- Use **retry budgets** (e.g. retries may add at most 10–20% extra load) and exponential backoff with jitter.
- Set **timeouts** that shrink as you go deeper (or propagate a *deadline* with the request, as gRPC does). If the gateway gives up after 2 s but the service behind it waits 5 s for its database, the inner work carries on for a caller that has already left, and any outer retry piles duplicate work on top.

## Key takeaways

- Reverse proxies front servers: TLS, load balancing, buffering, compression, caching.
- API gateways front APIs for external clients: auth, rate limits, routing, transformation, developer features.
- Service meshes manage east-west traffic with sidecars plus a control plane: mTLS, retries, traffic shifting and telemetry without code changes.
- Each layer adds latency and operational cost; adopt a mesh when service count and requirements justify it.
- Keep business logic out of gateways, trust only your own forwarded headers, and retry at one layer with budgets.

## Further reading

- [Reverse proxy (Wikipedia)](https://en.wikipedia.org/wiki/Reverse_proxy)
- [Pattern: API gateway / backends for frontends (microservices.io)](https://microservices.io/patterns/apigateway.html)
- [What is Istio?](https://istio.io/latest/docs/concepts/what-is-istio/)
- [What is a service mesh? (Linkerd)](https://linkerd.io/what-is-a-service-mesh/)
- [What is Envoy?](https://www.envoyproxy.io/docs/envoy/latest/intro/what_is_envoy)
