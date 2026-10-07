---
id: arch-service-communication
title: Service discovery and inter-service communication
level: intermediate
minutes: 13
summary: How services find each other when instances come and go, what sidecars and service meshes add, and when to call synchronously versus send a message.
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

## Synchronous versus asynchronous calls

This choice matters more than which discovery mechanism you pick.

### Synchronous (request/response)

Orders calls Payments over HTTP or gRPC and **waits** for the answer.

- Simple to reason about; the caller gets an immediate result.
- **Temporal coupling**: Payments must be up *right now* for Orders to succeed.
- Latency adds up along the chain, and slow dependencies retain caller resources. Blocking clients hold threads; asynchronous clients can still retain requests, connections and memory.

### Asynchronous (messaging)

Orders publishes `OrderPlaced` to a broker (Kafka, SQS, RabbitMQ) and returns. Payments consumes it when it can.

- The producer doesn't need the consumer to be up; the broker buffers.
- Natural load levelling and fan-out to many consumers.
- **Eventual consistency**: the user may see "processing" for a while.
- Harder to debug, and you must handle duplicates and ordering.

| Need | Prefer |
|---|---|
| User needs answer now | Sync |
| Read data for a page | Sync (or cache) |
| Side effects (email) | Async |
| Many consumers | Async events |
| Spiky workloads | Async queue |

### Commands versus events

Async messages come in two flavours:

- A **command** says "do this" to a specific service: `ChargeCard`. The sender knows who handles it.
- An **event** says "this happened": `OrderPlaced`. The publisher doesn't know or care who listens, which is the loosest coupling.

> [!example] Checkout in practice
> Checkout calls Payments **synchronously** for authorisation, because the user must know whether the card was accepted. It then publishes `OrderPlaced`. Inventory, Email, Analytics and Loyalty consume that event **asynchronously**. If Email is down for an hour, checkout is unaffected and delivery can resume when it recovers, provided durable retention, retries and deduplication cover the outage and the provider accepts the messages.

## Making synchronous calls safe

When you do call synchronously, protect the caller:

1. **Timeouts on every call.** Without one, a hung dependency hangs you. Set them from measured latency (for example p99.9 plus margin), and allocate nested calls and retries within the remaining end-to-end deadline, leaving time for local work and response handling.
2. **Retries with exponential backoff and jitter**, only for idempotent operations, with a retry budget to bound additional load during an outage.
3. **Circuit breakers**: after repeated failures, fail fast for a while instead of piling on.
4. **Bulkheads**: bound in-flight work and queues per dependency, with separate resources where needed. Separate connection pools alone do not guarantee isolation of a shared thread pool.
5. **Fallbacks**: serve cached or default data (generic recommendations instead of personalised ones).

Watch out for **retry amplification**. Retries multiply down a chain. If each of three hops makes up to 3 attempts (1 try + 2 retries), one user request can become 3 × 3 × 3 = 27 calls on the bottom service, exactly when it's already struggling.

```
 attempts per hop: a
 hops in chain:    n
 calls at bottom:  a ** n
 a=3, n=3 -> 27    a=4, n=2 -> 16
```

The usual fix is to retry at **one** layer only (often the one nearest the failing dependency), and to cap retries with a budget, for example retries may add at most 10% to normal traffic.

## Protocols in brief

- **REST/JSON over HTTP**: universal and easy to debug; verbose, and contracts are often informal (OpenAPI helps).
- **gRPC**: Protocol Buffers over HTTP/2; compact, fast, strongly typed contracts and streaming; less friendly to browsers and curl. Common for internal service-to-service calls.
- **Messaging**: Kafka for high-throughput replayable event logs; SQS or RabbitMQ for work queues.

An **API gateway** usually sits at the edge, handling auth, rate limiting and routing for external clients, while internal traffic goes service-to-service (often via the mesh).

## Key takeaways
- Dynamic infrastructure needs a service registry; instances register themselves or the platform registers them.
- Client-side discovery avoids a hop and allows smart balancing but needs a library per language; server-side discovery keeps clients simple at the cost of a hop.
- Sidecars and meshes move discovery, mTLS, retries and telemetry out of application code, at the cost of resources and operational complexity.
- Synchronous calls create temporal coupling; use them when the caller truly needs the answer now, and protect them with timeouts, bounded retries and circuit breakers.
- Asynchronous events decouple services in time and allow fan-out, in exchange for eventual consistency and harder debugging.

## Further reading
- [microservices.io: Client-side discovery](https://microservices.io/patterns/client-side-discovery.html)
- [microservices.io: Server-side discovery](https://microservices.io/patterns/server-side-discovery.html)
- [Azure Architecture Center: Sidecar pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/sidecar)
- [Istio architecture](https://istio.io/latest/docs/ops/deployment/architecture/)
- [gRPC: Introduction](https://grpc.io/docs/what-is-grpc/introduction/)
- [microservices.io: API gateway](https://microservices.io/patterns/apigateway.html)
