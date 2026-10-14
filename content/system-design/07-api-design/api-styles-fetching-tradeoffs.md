---
id: api-styles-fetching-tradeoffs
title: API styles and fetching trade-offs
level: intermediate
minutes: 3
summary: Compare resource, graph and RPC contracts, then diagnose over-fetching and under-fetching.
sourceLesson: api-rest-graphql-grpc
---

"Should this be REST, GraphQL or gRPC?" comes up in nearly every design discussion. There's no universal winner. Each style optimises for a different consumer and a different set of pain points.

## The three styles at a glance

| | REST | GraphQL | gRPC |
|---|---|---|---|
| Model | Resources | Typed graph | Procedures |
| Common transport | HTTP/1.1, HTTP/2 or HTTP/3 | Usually HTTP; subscriptions use a chosen transport | Native gRPC commonly HTTP/2 |
| Payload | JSON (usually) | JSON | Protobuf binary |
| Contract | OpenAPI (optional) | GraphQL schema (required) | `.proto` (required) |
| HTTP caching | Native HTTP cache rules | Requires careful query/cache design | No ordinary response-cache contract |
| Browser support | Native HTTP | Native HTTP | Needs compatible protocol |
| Streaming | HTTP streams such as SSE | GraphQL subscriptions | 4 modes, native |

## REST: simple, cacheable, but chatty

REST's strengths are covered in the earlier REST units: universal tooling, CDN caching, easy debugging with `curl`. Its weaknesses show up when one screen needs data from many resources.

Imagine a mobile feed showing 20 posts, each with its author's name and avatar and the first 3 comments.

```
GET /feed              -> 20 post ids
GET /posts/1 ... /20   -> 20 calls
GET /users/a ... /t    -> up to 20
GET /posts/1/comments  -> 20 more
```

Counting them shows where the number comes from:

```formula
R = 1 + P + A + K
R = 1 + 20 + 20 + 20
R = 61
where
R: the total number of HTTP requests the screen needs
P: requests for the posts themselves, one per post, here 20
A: requests for authors, at most one per post (fewer if two posts share an author), here up to 20
K: requests for the comments, one per post, here 20
In words: one request fetches the list, then every post costs up to three more, so 20 posts need up to 61 requests.
```

That's up to 61 requests, not necessarily 61 sequential round trips. On a 4G link at 100 ms RTT, even with HTTP/2 multiplexing it's several dependent waves. And each response contains fields the screen doesn't need.

- **Under-fetching**: one call doesn't return enough, so you make more.
- **Over-fetching**: each call returns more than you need, wasting bandwidth and battery.

The usual REST fixes are compound endpoints (`GET /feed?include=author,comments`) or sparse fieldsets (`?fields=id,title`). They work, but every new screen tends to grow a new bespoke endpoint.

## Key takeaways
- Choose a style around its consumers, transport and contract.
- Under-fetching adds calls; over-fetching sends unused fields.
- Compound endpoints and sparse fieldsets reduce REST chatter; request count is not sequential round-trip count.

## Further reading
- [GraphQL: Introduction to GraphQL](https://graphql.org/learn/)
- [gRPC: Core concepts](https://grpc.io/docs/what-is-grpc/core-concepts/)
