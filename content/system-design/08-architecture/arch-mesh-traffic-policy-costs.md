---
id: arch-mesh-traffic-policy-costs
title: Moving traffic policy into a service mesh
level: intermediate
minutes: 3
summary: Explain what proxies can add and what they cost without assuming they implement application semantics.
sourceLesson: arch-service-communication
---

Discovery chooses a healthy destination. A service mesh can move that choice and other traffic policies into proxies, shared across application languages. Its promises apply to enrolled and intercepted traffic.

## Sidecars and service meshes

A **sidecar** is a helper process deployed next to each service instance (in Kubernetes, a second container in the same pod). It handles cross-cutting concerns so the application doesn't have to.

A **service mesh** manages service-to-service traffic through a data plane and a control plane. In a sidecar deployment (for example Istio or Linkerd), proxies run alongside enrolled workloads; sidecarless designs use a different topology. Istio uses Envoy; Linkerd uses its own lightweight Rust proxy.

```
 Pod A                 Pod B
+--------------+      +--------------+
| [Orders app] |      | [Payments]   |
|     |        |      |     ^        |
|  [proxy] ----+-mTLS-+-> [proxy]    |
+--------------+      +--------------+
        ^   config + certs   ^
        +---[ control plane ]+
```

With transparent interception, the app calls the destination service address as usual; traffic is redirected through the local sidecar. The sidecar adds:

- **Discovery and load balancing** (client-side, but without a per-language library)
- **Mutual TLS** between services, with automatic certificate rotation
- **Retries, timeouts and circuit breaking**, configured centrally
- **Metrics and trace spans** for intercepted supported traffic; sampling and protocol support vary, and end-to-end traces need application context propagation
- **Traffic shifting**: send 5% of calls to v2 for a canary

The costs: an extra proxy hop on each side (latency depends on configuration, load and protocol and can accumulate on deep call chains), extra CPU and memory per pod, and a complex control plane to operate. Newer "sidecarless" modes cut that overhead. Istio's ambient mode (generally available since late 2024) uses a shared per-node proxy for mTLS and basic traffic handling, and adds optional waypoint proxies for Layer 7 policies, enrolled at namespace, service or workload scope as supported by configuration.

### Review the combined policy

Before enabling a mesh retry policy, inspect retries already made by clients and gateways. Independent layers can multiply attempts against the same failing dependency. Check timeouts and cancellation across those layers, too. A proxy sees network requests, not whether an order was charged or a database transaction committed, so transport retries do not establish business-level exactly-once behaviour. Measure the extra CPU, memory and latency for the intended topology rather than using a universal per-proxy figure.

## Key takeaways
- A mesh separates a traffic data plane from a configuration control plane; sidecars are one possible topology.
- Intercepted supported traffic can gain mTLS, routing policy and telemetry; complete traces still need propagated context.
- Proxy resources, added hops, central misconfiguration and duplicate retry policies belong in the cost model.

## Further reading
- [Azure Architecture Center: Sidecar pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/sidecar)
- [Istio architecture](https://istio.io/latest/docs/ops/deployment/architecture/)
