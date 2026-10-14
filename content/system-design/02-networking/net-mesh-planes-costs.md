---
id: net-mesh-planes-costs
title: "Mesh planes, sidecars and ambient mode"
level: intermediate
minutes: 3
summary: "Explain mesh traffic features, trace-context limits and the costs of sidecar or ambient deployment."
sourceLesson: net-proxies-gateways-mesh
---
A mesh provides networking policy between services. Compare it with libraries and gateways by the traffic it controls, then budget the resource and operational cost of the chosen data plane.

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
- **Resources:** a sidecar per pod, each with its own CPU and memory; across thousands of pods this adds up.
- **Operational complexity:** the control plane is now critical infrastructure. A bad config push can break every service at once.
- **Debugging:** "is it my app or the mesh?" becomes a common question.

> [!note] Measurement gap
> No reproducible gateway or mesh benchmark is supplied here. Fixed per-hop latency and universal per-client memory/capacity estimates are omitted.

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

## Key takeaways

- The data plane handles enrolled traffic; the control plane distributes certificates, policy and routing.
- L7 retries, routing and telemetry depend on supported visible protocols; end-to-end traces need application context propagation.
- Ambient mode separates per-node L4 transport from optional L7 waypoints; adoption still needs an operational case.

## Further reading

- [What is Istio?](https://istio.io/latest/docs/concepts/what-is-istio/)
- [Ambient mode overview (Istio)](https://istio.io/latest/docs/ambient/overview/)
- [What is a service mesh? (Linkerd)](https://linkerd.io/what-is-a-service-mesh/)
