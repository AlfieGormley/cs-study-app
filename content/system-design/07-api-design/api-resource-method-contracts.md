---
id: api-resource-method-contracts
title: Resources and HTTP method contracts
level: basic
minutes: 5
summary: Model resources and distinguish safe, idempotent and partial-update operations.
sourceLesson: api-rest-fundamentals
---

Almost every system design answer has a box labelled "API". Before you can argue about GraphQL, rate limits or idempotency keys, you need a precise model of what a plain HTTP API promises. REST gives you that model.

REST (Representational State Transfer) was described by Roy Fielding in his 2000 PhD dissertation. It isn't a protocol or a library. It's a set of constraints that, if you follow them, give you an API that caches well, scales horizontally and supports evolvability; application contracts and compatibility still require design.

## Resources, not actions

The central idea is the **resource**: a noun that has an identity and a URL. A customer, an order, a list of orders. Clients manipulate *representations* of resources (usually JSON) using a small, fixed set of verbs.

Compare two designs for the same feature:

```
RPC style         REST style
--------------    ---------------------
POST /getOrder    GET  /orders/42
POST /addOrder    POST /orders
POST /cancel      POST /orders/42/cancel
POST /listOrders  GET  /orders?status=open
```

The RPC style invents a new verb per operation. Every client has to learn each one, and the method alone does not advertise safe/idempotent operation semantics. Explicit response caching metadata can still make certain POST responses cacheable. In the REST style the verb carries meaning that the whole HTTP ecosystem understands.

> [!tip] Nouns in paths, verbs in methods
> Use plural nouns (`/orders`, `/orders/42/items`). When an action genuinely doesn't fit CRUD, such as cancelling or refunding, use a pragmatic action endpoint (`POST /orders/42/cancel`) or as a new resource (`POST /refunds`). Don't contort the domain to avoid it.

Keep nesting shallow. `/customers/7/orders/42` is fine; `/customers/7/orders/42/items/3/options/9` is a sign that `items` deserves its own top-level resource.

## HTTP methods: safe and idempotent

RFC 9110 defines two properties that matter enormously in distributed systems.

- **Safe**: the method is read-only in intent. The client is not asking for any state change. Crawlers, prefetchers and caches may call it freely.
- **Idempotent**: making the same request N times has the same effect on the server as making it once. The *response* may differ (a second `DELETE` may return 404), but the server's state ends up the same.

| Method | Safe | Idempotent | Typical use |
|---|---|---|---|
| GET | Yes | Yes | Read a resource |
| HEAD | Yes | Yes | Headers only |
| OPTIONS | Yes | Yes | CORS preflight |
| PUT | No | Yes | Replace whole resource |
| DELETE | No | Yes | Remove resource |
| PATCH | No | Not by default | Partial update |
| POST | No | No | Create, or run a process |

Every safe method is idempotent, but not the other way round. `DELETE /orders/42` changes state, yet doing it twice leaves the order deleted either way.

## Why idempotency matters

Networks fail in the worst possible place: *after* the server did the work but *before* the client got the response. The client sees a timeout and has no idea whether the request happened.

```
Client            Server
  |--- PUT x=5 ---->|
  |                 | writes x=5
  |    X<-- 200 ----|  (lost)
  | timeout!        |
  |--- PUT x=5 ---->|  retry: x=5
  |<--- 200 --------|  still x=5
```

With `PUT`, the retry is harmless. With `POST /payments`, a retry could charge the customer twice. That's why RFC 9110 lets clients and proxies retry idempotent requests automatically, and why clients need evidence that a non-idempotent operation is safe to retry or that the original was not applied; proxies must not automatically retry non-idempotent requests. Making `POST` safe to retry needs extra machinery (idempotency keys), covered later in this module.

## PUT vs PATCH

`PUT` requests replacement of the target resource state with the supplied representation. The API defines how writable fields map to state; server-managed fields and related resources need not be erased merely because they are absent. Repeating the same replacement has the same intended effect.

```
PUT /users/7
Content-Type: application/json

{"name": "Ada", "email": "ada@example.com"}
```

`PATCH` sends a set of changes. A JSON Merge Patch like `{"email": "new@example.com"}` happens to be idempotent. A patch like "append item to list" or "increment counter" is not. So the HTTP spec doesn't promise `PATCH` is idempotent; your API might.

> [!warning] Don't change state on GET
> A `GET /users/7/delete` link will eventually be followed by a crawler, a link-preview bot or a browser prefetch. Teams have lost data this way. Safe means safe.

## Key takeaways
- Use resource identities and standard methods to make intent visible.
- Safe methods request no state change; incidental logging is allowed. Idempotent methods preserve the intended effect on repetition.
- PUT replaces writable resource state; PATCH idempotency depends on the changes requested.
- A timeout is an unknown outcome. Non-idempotent retries need evidence and an enforced contract.

## Further reading
- [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110)
- [MDN: HTTP request methods](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods)
