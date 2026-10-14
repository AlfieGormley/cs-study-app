---
id: api-response-status-contracts
title: Status codes and retry decisions
level: basic
minutes: 3
summary: Use response status codes to describe completion, validation and transient failure.
sourceLesson: api-rest-fundamentals
---

HTTP status codes are part of the API contract. The method semantics from the preceding unit still apply when a response suggests trying again.

## Status codes

Status codes are the first thing a client, a load balancer and your monitoring look at. Use them precisely.

| Range | Meaning | Who should act |
|---|---|---|
| 2xx | Success | Interpret completion and content |
| 3xx | Redirect / not modified | Follow redirect or reuse validated content |
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

"Might work later" still only licenses an automatic retry if the request is idempotent (or the endpoint enforces an applicable idempotency contract). A `500` on a `POST /payments` doesn't tell you whether the charge happened before the crash.

## Key takeaways
- Use 201 for creation and 202 for work accepted but not completed.
- Validation failures and dependency outages need different status codes.
- Retry guidance is only useful alongside the operation’s idempotency contract.

## Further reading
- [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110)
- [MDN: HTTP response status codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
