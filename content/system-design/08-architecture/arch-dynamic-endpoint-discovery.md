---
id: arch-dynamic-endpoint-discovery
title: Finding changing service instances
level: intermediate
minutes: 3
summary: Compare registry-aware clients with stable-name routing and diagnose stale discovery caches.
sourceLesson: arch-service-communication
---

Once you have more than one service, two questions appear straight away. **How does Orders find a healthy Payments instance** when instances are created and destroyed every few minutes? And **should Orders wait for Payments to answer**, or send a message and move on?

## Why discovery is needed

Hard-coding an instance IP is fragile when instances change. A stable DNS name such as payments.internal:8080 can still be appropriate when discovery or routing updates its backing endpoints. In a cloud or Kubernetes world:

- Instances autoscale up and down.
- Deploys replace every instance with new IP addresses.
- Failed instances are removed and replaced automatically.

So something must keep an up-to-date list of healthy instances (the **service registry**) and something must use that list to pick one for each call.

Instances get into the registry by **self-registration** (the instance registers itself and sends heartbeats, as with Netflix Eureka or Consul agents) or by **third-party registration** (the platform registers them, as Kubernetes does from pod readiness).

## Client-side discovery

The calling service queries the registry and chooses an instance itself.

```
 [Orders]---1. lookup--->[Registry]
    |    <--2. [ip1,ip2,ip3]
    |
    +--3. call ip2--->[Payments #2]
```

- **Pros:** no extra hop; the client can use smart load balancing (least-requests, zone-aware routing, retries to a different instance).
- **Cons:** every language needs a discovery client library, and logic is duplicated across stacks. Netflix's Ribbon + Eureka is the classic example (Ribbon is now in maintenance mode); gRPC's client-side load balancing is a modern one.

## Server-side discovery

The client calls a stable address; a load balancer or router looks up the registry and forwards the request.

```
 [Orders]--call payments-->[ LB / proxy ]
                              |     |
                       [Pay #1]  [Pay #2]
```

- **Pros:** clients stay simple and language-agnostic; just call a DNS name.
- **Cons:** an extra network hop, and the load balancer must be highly available.

Kubernetes Services are server-side discovery: `payments.default.svc.cluster.local` resolves to a virtual IP, and kube-proxy (iptables, IPVS or nftables rules on each node) forwards to a ready pod. Some network plugins, such as Cilium, replace kube-proxy with eBPF programs that do the same job. EndpointSlices can include unready endpoints with condition flags; normal routing chooses eligible endpoints, with exceptions such as publishNotReadyAddresses. A pod need not have an explicit readiness probe. ALB target groups also use health checks, but their failure policies differ: ALB can fail open when all targets are unhealthy.

> [!warning] DNS caching bites
> Plain DNS-based discovery suffers when clients cache records beyond their TTL. The JVM historically cached DNS lookups indefinitely when a security manager was installed. If you rely on DNS, check your runtime's caching behaviour and keep TTLs short.

## Key takeaways
- A registry tracks service instances; client-side discovery selects in the caller, server-side discovery selects in routing infrastructure.
- Language-specific client libraries trade direct instance choice for duplicated implementation work.
- Normal ClusterIP Services give clients a stable name while platform routing selects eligible endpoints.
- Runtime and connection-pool caching can outlive DNS TTLs, so test actual refresh behaviour.

## Further reading
- [microservices.io: Client-side discovery](https://microservices.io/patterns/client-side-discovery.html)
- [microservices.io: Server-side discovery](https://microservices.io/patterns/server-side-discovery.html)
