---
id: api-stateless-conditional-requests
title: Stateless requests and HTTP validators
level: basic
minutes: 3
summary: Keep servers replaceable and use ETags for cache revalidation and atomic update checks.
sourceLesson: api-rest-fundamentals
---

Interchangeable servers require requests that do not depend on one server’s private conversation history. HTTP validators then make reads and writes cheaper or safer.

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

Fielding's full list also includes client–server separation, a layered system (clients can't tell if they're talking to a proxy), and HATEOAS (responses include links to the next possible actions). The Richardson Maturity Model grades APIs from level 0 (one endpoint, RPC over HTTP) to level 3 (hypermedia). A pragmatic API can use level 2: resources plus proper verbs and status codes. This is useful, although it does not satisfy all of Fielding's REST constraints.

## Key takeaways
- Strict REST carries conversational context in requests; shared application state can still live in a database.
- If-None-Match revalidates a cached representation without resending unchanged content.
- If-Match prevents lost updates only when validator comparison and mutation are atomic.
- REST also includes separation, layering and hypermedia constraints.

## Further reading
- [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110)
- [Fielding's dissertation, chapter 5: REST](https://ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm)
- [Martin Fowler: Richardson Maturity Model](https://martinfowler.com/articles/richardsonMaturityModel.html)
- [MDN: HTTP caching](https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching)
