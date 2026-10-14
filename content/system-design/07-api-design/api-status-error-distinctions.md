---
id: api-status-error-distinctions
title: Authentication, conflict and quota errors
level: basic
minutes: 2
summary: Distinguish 401 from 403, 409 from 422, and client quotas from temporary unavailability.
sourceLesson: api-rest-fundamentals
---

Clients recover differently from expired credentials, insufficient permissions, conflicting state and rate limits. Choosing the right code lets them respond to the actual condition.

## Pairs people mix up

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

## Key takeaways
- 401 requires a WWW-Authenticate challenge; unchanged credentials are not a general recovery strategy for 403.
- 409 describes conflict with current state; 422 describes well-formed content that cannot be processed semantically.
- 429 identifies a client limit; 503 identifies temporary unavailability for the request.

## Further reading
- [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110)
- [MDN: HTTP response status codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
