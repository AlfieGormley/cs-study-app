---
id: api-rest-fundamentals
title: REST fundamentals
level: basic
minutes: 13
summary: Resources, HTTP methods and their safety and idempotency, status codes, and why statelessness lets REST APIs scale.
---

Almost every system design answer has a box labelled "API". Before you can argue about GraphQL, rate limits or idempotency keys, you need a precise model of what a plain HTTP API promises. REST gives you that model.

REST (Representational State Transfer) was described by Roy Fielding in his 2000 PhD dissertation. It isn't a protocol or a library. It's a set of constraints that, if you follow them, give you an API that caches well, scales horizontally and support evolvability; application contracts and compatibility still require design.

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

### Why idempotency matters

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

### PUT vs PATCH

`PUT` requests replacement of the target resource state with the supplied representation. The API defines how writable fields map to state; server-managed fields and related resources need not be erased merely because they are absent. Repeating the same replacement has the same intended effect.

```
PUT /users/7
Content-Type: application/json

{"name": "Ada", "email": "ada@example.com"}
```

`PATCH` sends a set of changes. A JSON Merge Patch like `{"email": "new@example.com"}` happens to be idempotent. A patch like "append item to list" or "increment counter" is not. So the HTTP spec doesn't promise `PATCH` is idempotent; your API might.

> [!warning] Don't change state on GET
> A `GET /users/7/delete` link will eventually be followed by a crawler, a link-preview bot or a browser prefetch. Teams have lost data this way. Safe means safe.

## Status codes

Status codes are the first thing a client, a load balancer and your monitoring look at. Use them precisely.

| Range | Meaning | Who should act |
|---|---|---|
| 2xx | Success | Nobody |
| 3xx | Redirect / not modified | Client follows |
| 4xx | Client-error class | Interpret the specific code; some conditions are transient |
| 5xx | Server error | Server; client may retry |

The ones you'll use most:

| Code | When |
|---|---|
| 200 OK | Successful request; content depends on method (HEAD has no response content) |
| 201 Created | A request created a resource (e.g. POST or PUT); usually identify it with `Location` |
| 202 Accepted | Accepted for processing, not yet completed; completion is not guaranteed |
| 204 No Content | Success, empty body |
| 304 Not Modified | Conditional GET/HEAD validator indicates the selected representation need not be transferred |
| 400 Bad Request | Malformed syntax or invalid input |
| 401 Unauthorized | Missing or bad credentials |
| 403 Forbidden | Understood, but refused |
| 404 Not Found | No such resource |
| 409 Conflict | Clashes with current state |
| 412 Precondition Failed | `If-Match` ETag didn't match |
| 422 Unprocessable Content | Well-formed but semantically invalid |
| 429 Too Many Requests | Rate limited |
| 500 Internal Server Error | Unexpected server condition prevented fulfillment |
| 502 / 504 | Upstream failed / timed out |
| 503 Service Unavailable | Overloaded or in maintenance |

The 4xx/5xx split is a contract about retries. Most 4xx responses require correcting the request, but codes such as 408 and 429 can describe transient conditions. A 5xx may also be transient; the specific status, retry guidance and operation semantics determine whether retrying is appropriate. Returning `500` for a validation error makes clients retry pointlessly; returning `400` for a database outage makes them give up when they shouldn't.

"Might work later" still only licenses an automatic retry if the request is idempotent (or carries an idempotency key). A `500` on a `POST /payments` doesn't tell you whether the charge happened before the crash.

### Pairs people mix up

**401 vs 403.** Despite its name, `401 Unauthorized` means *unauthenticated*: the credentials are missing, expired or invalid. RFC 9110 requires a 401 to carry a `WWW-Authenticate` header telling the client how to authenticate, and the client's natural reaction is to refresh its token and try again. `403 Forbidden` means the server understood the request and refuses it. Repeating unchanged credentials should not be an automatic recovery strategy, although different credentials or changed permissions can sometimes resolve it. A valid token without the right role or scope gets a 403.

**409 vs 422.** `409 Conflict` means the request clashes with the *current state of the resource*: a username that's already taken, or cancelling an order that has already shipped. The same request might succeed once the state changes. `422 Unprocessable Content` means the body is syntactically fine but *semantically* invalid on its own: an end date before the start date, or a negative quantity. Many APIs use plain `400` for validation failures; that's acceptable as long as you're consistent.

**429 and 503.** Both mean "not now", and both should ideally carry a `Retry-After` header (seconds, or an HTTP date). `429 Too Many Requests` is about *this client* exceeding its quota; `503` indicates temporary unavailability for this request; other endpoints or clients may still be served.

A well-formed create looks like this. Note the `201` and the `Location` header pointing at the new resource:

```
POST /orders HTTP/1.1
Content-Type: application/json

{"sku": "VAN-123", "qty": 1}
```

```
HTTP/1.1 201 Created
Location: /orders/9831
Content-Type: application/json

{"id": "9831", "status": "pending"}
```

## Statelessness

REST requires that **each request contains everything the server needs to understand it**. The server doesn't remember anything about the client between requests: no "current page" or "logged-in user" held in a particular server's memory.

```
       +---------+
req -->|   LB    |
       +---------+
       /    |    \
   +---+  +---+  +---+
   |A  |  |B  |  |C  |  any server
   +---+  +---+  +---+  can serve
       \    |    /      any request
      +-----------+
      | shared DB |
      +-----------+
```

This is what makes horizontal scaling easy. If server A dies, B and C carry on, because nothing the client depends on lived only in A. You don't need sticky sessions at the load balancer.

Statelessness doesn't mean the *application* has no state. Orders still live in the database. Strict REST keeps conversational session context in client requests. A shared server-side session store is a common practical HTTP API design that makes application servers replaceable, but it does not by itself satisfy Fielding's strict stateless-session constraint.

The cost is that each request is a little bigger and the server re-validates credentials every time. That's almost always worth paying.

## Caching and conditional requests

Because `GET` is safe and responses are self-describing, HTTP can cache them. The server controls this with headers:

```
HTTP/1.1 200 OK
Cache-Control: max-age=60
ETag: "v7-a1b2"
```

After 60 seconds a client retaining the response can revalidate; when the representation is unchanged:

```
GET /products/5
If-None-Match: "v7-a1b2"

HTTP/1.1 304 Not Modified
```

ETags also prevent **lost updates**. Two admins load product 5 at version `"v7"`. Both edit and `PUT` with `If-Match: "v7"`. The first succeeds and the version becomes `"v8"`. The second gets `412 Precondition Failed` instead of silently overwriting the first admin's change. This is optimistic concurrency control over HTTP, provided validator comparison and mutation are atomic.

## The other constraints, briefly

Fielding's full list also includes client–server separation, a layered system (clients can't tell if they're talking to a proxy), and HATEOAS (responses include links to the next possible actions). The Richardson Maturity Model grades APIs from level 0 (one endpoint, RPC over HTTP) to level 3 (hypermedia). In practice most production "REST" APIs sit at level 2: resources plus proper verbs and status codes. That's a perfectly good place to be.

## Key takeaways
- Model your API as **resources** (nouns with URLs) manipulated by a small set of standard methods.
- **Safe** methods (GET, HEAD, OPTIONS) do not request a state change; incidental logging and similar server side effects are allowed. **Idempotent** methods (those plus PUT, DELETE) can be repeated with the same effect. POST is neither.
- Idempotency is what makes **retries after timeouts** safe; it permits automatic retries of idempotent requests, while non-idempotent retries need additional evidence and an enforced contract.
- Interpret each status code and operation: many 4xx require correction, while transient failures may permit a bounded, semantically safe retry.
- **Statelessness** lets any server handle any request, which is what makes horizontal scaling and failover simple.
- `ETag` with `If-None-Match` saves bandwidth; with `If-Match` it prevents lost updates.

## Further reading
- [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110)
- [MDN: HTTP request methods](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods)
- [MDN: HTTP response status codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- [Fielding's dissertation, chapter 5: REST](https://ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm)
- [Martin Fowler: Richardson Maturity Model](https://martinfowler.com/articles/richardsonMaturityModel.html)
- [MDN: HTTP caching](https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching)
