---
id: api-rest-graphql-grpc
title: REST vs GraphQL vs gRPC
level: intermediate
minutes: 12
summary: Three API styles compared, including over-fetching, the N+1 problem, protobuf encoding, streaming and how to choose.
---

"Should this be REST, GraphQL or gRPC?" comes up in nearly every design discussion. There's no universal winner. Each style optimises for a different consumer and a different set of pain points.

## The three styles at a glance

| | REST | GraphQL | gRPC |
|---|---|---|---|
| Model | Resources | Typed graph | Procedures |
| Common transport | HTTP/1.1, HTTP/2 or HTTP/3 | Usually HTTP; subscriptions use a chosen transport | Native gRPC commonly HTTP/2 |
| Payload | JSON (usually) | JSON | Protobuf binary |
| Contract | OpenAPI (optional) | Schema (required) | `.proto` (required) |
| HTTP caching | Excellent | Hard | None |
| Browser support | Native | Native | Needs proxy |
| Streaming | Limited (SSE) | Subscriptions | 4 modes, native |

## REST: simple, cacheable, but chatty

REST's strengths are covered in the previous lesson: universal tooling, CDN caching, easy debugging with `curl`. Its weaknesses show up when one screen needs data from many resources.

Imagine a mobile feed showing 20 posts, each with its author's name and avatar and the first 3 comments.

```
GET /feed              -> 20 post ids
GET /posts/1 ... /20   -> 20 calls
GET /users/a ... /t    -> up to 20
GET /posts/1/comments  -> 20 more
```

That's up to 61 requests, not necessarily 61 sequential round trips. On a 4G link at 100 ms RTT, even with HTTP/2 multiplexing it's several dependent waves. And each response contains fields the screen doesn't need.

- **Under-fetching**: one call doesn't return enough, so you make more.
- **Over-fetching**: each call returns more than you need, wasting bandwidth and battery.

The usual REST fixes are compound endpoints (`GET /feed?include=author,comments`) or sparse fieldsets (`?fields=id,title`). They work, but every new screen tends to grow a new bespoke endpoint.

## GraphQL: the client asks for exactly what it needs

GraphQL, open-sourced by Facebook in 2015, exposes a typed schema. Clients send a query that mirrors the shape of the data they want, usually as `POST /graphql`.

```
query {
  feed(first: 20) {
    id
    title
    author { name avatarUrl }
    comments(first: 3) { text }
  }
}
```

One round trip, no unused fields. The response has exactly the same shape as the query. The schema is introspectable, so tools like GraphiQL give autocomplete and type-checking for free.

### The N+1 problem

GraphQL moves the fan-out from the client to the server. Each field is backed by a *resolver* function. Naïve resolvers make the problem worse, not better:

```
feed resolver:   1 query  -> 20 posts
author resolver: called 20 times
  SELECT * FROM users WHERE id = ?
                 -> 20 queries
Total: 1 + N = 21 queries
```

Add comments and it's 1 + 20 + 20. Nest one more level and it multiplies.

The standard fix is **batching with a DataLoader**. Within one tick of the event loop, the loader collects every `author` id requested, then issues a single query:

```
SELECT * FROM users
WHERE id IN (a, b, c, ..., t)
```

With one database batch per relationship level in this example, it is 1 + 1 + 1 = 3 queries. Parameter limits, batch-size caps and per-parent pagination can require additional work as N grows. DataLoader also caches per request, so the same author appearing on five posts is fetched once.

> [!warning] GraphQL's operational costs
> - **Caching**: if operations use `POST /graphql`, ordinary URL-based CDN caching cannot distinguish request bodies. GraphQL queries may also use GET; mutation operations must not execute through GET. Teams use *persisted queries* (send a hash; allow `GET`) to recover some of this.
> - **Abuse**: a client can write a deeply nested query that fans out to millions of rows. You need query depth limits, complexity scoring and timeouts. GitHub's GraphQL API, for example, charges each query "points" based on how many nodes it could return.
> - **Errors**: responses are often `200 OK` with an `errors` array, which breaks status-code-based monitoring.

## gRPC: fast, typed service-to-service calls

gRPC, released by Google in 2015, is an RPC framework. You define services and messages in a `.proto` file, and code generators produce client and server stubs in a dozen languages.

```
syntax = "proto3";

service Inventory {
  rpc GetStock(StockReq)
      returns (StockResp);
  rpc WatchStock(StockReq)
      returns (stream StockResp);
}

message StockReq {
  string sku = 1;
}
message StockResp {
  string sku = 1;
  int32 qty  = 2;
}
```

The numbers (`= 1`, `= 2`) are **field tags**. They, not field names, go on the wire.

### Why protobuf is compact

Protocol Buffers encode a field key (tag number plus wire type) as a varint, followed by the encoded value. Small field keys occupy one byte; larger field numbers need more. Integers use *varints*, where small numbers take fewer bytes.

Take `{"sku": "VAN-1", "qty": 150}`:

| Encoding | Bytes |
|---|---|
| JSON (no spaces) | 25 |
| Protobuf | 10 |

Protobuf: `sku` is 1 tag byte + 1 length byte + 5 characters = 7. `qty` is 1 tag byte + 2 varint bytes (150 > 127) = 3. That's 10 bytes against 25, a 60% saving, before any compression. Parsing cost depends on the message, implementation and workload; the size calculation alone proves no universal CPU speed-up.

> [!note] Benchmark gap
> No comparable JSON/Protobuf parsing benchmark is supplied. Fixed speed-up claims are omitted; the 60% size saving is only for the specific uncompressed message above.

### Schema evolution rules

Because tags identify fields, you can evolve a schema safely if you:

- **Add** new fields with **new** tag numbers. Old readers ignore unknown tags.
- **Never reuse** a removed field's tag. Mark it `reserved 3;`.
- **Never change** a field's type or tag number.

Break these rules and you get silent damage, not an error. If you reuse tag 3 for a new field with the same *wire type* (say, one `string` replaced by another), an old client happily reads the new value as the old field. If the wire types differ, most parsers set the field aside as unknown, so the old client just sees it as missing.

Renaming a field is safe for the binary format, because names never go on the wire. It does break anything that uses protobuf's JSON mapping, which keys by field name.

### Four streaming modes

gRPC runs on HTTP/2, which multiplexes many streams over one TCP connection. That enables:

| Mode | Example |
|---|---|
| Unary | `GetStock` request/response |
| Server streaming | Live price feed |
| Client streaming | Upload telemetry batch |
| Bidirectional | Chat, collaborative edit |

gRPC supports **deadline propagation**. Some language implementations do it automatically; others require enabling it or passing the incoming context/deadline to outgoing calls. With propagation configured, a 300 ms caller budget can shrink at each downstream hop.

### gRPC's downsides

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

Netflix, Shopify and GitHub all expose GraphQL to UIs; Google, Square and many others run gRPC internally; nearly everyone offers REST to third parties because every language and tool already speaks it.

> [!tip] Interview framing
> Don't pick one and defend it to the death. Say who the consumers are, what their latency and payload constraints are, whether you need streaming or CDN caching, and pick accordingly. Mentioning N+1 and how DataLoader fixes it is a strong signal.

## Key takeaways
- **REST** is the best default for public APIs: universal tooling, HTTP caching, easy debugging. It suffers from over- and under-fetching for complex UIs.
- **GraphQL** lets clients fetch exactly the shape they need in one round trip, but brings **N+1** resolver problems (fix with batching via DataLoader), weak HTTP caching and query-cost abuse risks.
- **gRPC** uses compact protobuf over HTTP/2 with generated stubs, deadlines and four streaming modes. Ideal for internal service-to-service traffic; awkward in browsers.
- Protobuf evolution depends on **field tags**: add new tags, never reuse or retype old ones.
- Most large systems combine styles: GraphQL or BFF at the edge, gRPC inside, REST for partners.

## Further reading
- [GraphQL: Introduction to GraphQL](https://graphql.org/learn/)
- [GraphQL: Performance (N+1 and DataLoader)](https://graphql.org/learn/performance/)
- [DataLoader on GitHub](https://github.com/graphql/dataloader)
- [gRPC: Core concepts](https://grpc.io/docs/what-is-grpc/core-concepts/)
- [Protocol Buffers: Language guide (proto3)](https://protobuf.dev/programming-guides/proto3/)
- [gRPC: Performance best practices](https://grpc.io/docs/guides/performance/)
