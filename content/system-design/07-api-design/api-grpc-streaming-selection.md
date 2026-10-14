---
id: api-grpc-streaming-selection
title: gRPC streaming, deadlines and API selection
level: intermediate
minutes: 3
summary: Choose streaming modes, propagate deadlines and account for browser and load-balancing constraints.
sourceLesson: api-rest-graphql-grpc
---

A compact message format is only part of a service contract. Consumers also need suitable streaming, cancellation, browser access and routing.

## Four streaming modes

gRPC runs on HTTP/2, which multiplexes many streams over one TCP connection. That enables:

| Mode | Example |
|---|---|
| Unary | `GetStock` request/response |
| Server streaming | Live price feed |
| Client streaming | Upload telemetry batch |
| Bidirectional | Chat, collaborative edit |

gRPC supports **deadline propagation**. Some language implementations do it automatically; others require enabling it or passing the incoming context/deadline to outgoing calls. With propagation configured, a 300 ms caller budget can shrink at each downstream hop.

## gRPC's downsides

- **Browsers** can't speak raw gRPC (they can't control HTTP/2 framing or read trailers). You need gRPC-Web, usually translated by a proxy such as Envoy, or a browser-friendly variant such as Connect.
- **Debugging** binary payloads needs tooling (`grpcurl`), not just `curl`.
- **Load balancing** is trickier. Long-lived HTTP/2 connections mean an L4 load balancer pins all of a client's calls to one backend. You need L7 (request-level) balancing or client-side balancing. The networking module covers this.

## Choosing

```
Who calls the API?
 |
 +- Public / third-party devs
 |    -> REST (+ OpenAPI)
 |
 +- Your own UIs, many screens,
 |  varied data needs
 |    -> GraphQL (or a BFF)
 |
 +- Internal microservices,
    latency-sensitive, polyglot
      -> gRPC
```

Real systems usually mix them. A common pattern:

```
 Mobile/Web         Partners
     |                  |
  GraphQL             REST
  gateway            public API
     \                 /
      +-- gRPC mesh --+
      | svc  svc  svc |
      +---------------+
```

These styles can coexist without requiring every consumer to use the same interface. The decision depends on the documented client contract and measured workload.

> [!tip] Interview framing
> Don't pick one and defend it to the death. Say who the consumers are, what their latency and payload constraints are, whether you need streaming or CDN caching, and pick accordingly. Mentioning N+1 and how DataLoader fixes it is a strong signal.

## Key takeaways
- gRPC supports unary, server, client and bidirectional streaming.
- Deadline propagation needs appropriate implementation configuration and carries a shrinking caller budget.
- Browsers need a compatible protocol, and long-lived HTTP/2 connections complicate L4 balancing.
- A system can combine GraphQL or BFFs for UIs, REST for partners and gRPC internally.

## Further reading
- [gRPC: Core concepts](https://grpc.io/docs/what-is-grpc/core-concepts/)
- [gRPC: Performance best practices](https://grpc.io/docs/guides/performance/)
- [gRPC: Deadlines](https://grpc.io/docs/guides/deadlines/)
- [gRPC-Web: Supported streaming modes](https://github.com/grpc/grpc-web)
