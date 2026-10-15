---
id: web-cors-preflight-permission
title: CORS response sharing and preflight
level: basic
minutes: 3
sourceLesson: web-sop-cors
summary: Non-safelisted CORS requests need permission before their method and headers are sent.
---

An origin consists of scheme, host and port. The previous unit separated sending a request from reading its response; CORS gives the server a controlled way to allow that read.

## CORS: opting in to cross-origin reads

Modern apps legitimately need cross-origin reads. A single-page app on `https://a.test` calls an API on `https://b.test`. **Cross-Origin Resource Sharing** (CORS) lets the *server* tell the browser which other origins may read its responses.

A browser CORS fetch includes an Origin request header (such as `Origin: https://a.test`); not every cross-origin navigation or embedding request does. The server replies with headers saying what it allows:

```
GET /v1/orders HTTP/1.1
Host: api.example
Origin: https://a.test

HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://a.test
Vary: Origin
```

For a CORS fetch, a matching allow-origin value is necessary to expose the response; `*` works only when credentials mode is not `include`. Credentialed requests also require allow-credentials. CORS failures are exposed as network errors. A required preflight additionally gates sending the actual method/headers. CORS does not replace the server authenticating the caller.

### Simple requests and preflights

The safelist preserves forms of cross-origin traffic historically possible without CORS. A request avoiding preflight still can have harmful side effects. The following is a simplified checklist for a CORS fetch that does not otherwise require preflight:

- Method is `GET`, `HEAD` or `POST`.
- Author-set headers meet the CORS safelist, including header-specific byte, length and syntax restrictions; a safelisted name alone is insufficient.
- `Content-Type`, if set, is `application/x-www-form-urlencoded`, `multipart/form-data` or `text/plain`.

Methods such as `PUT`/`DELETE`, an author-set `Authorization` header or JSON content type require preflight permission in a CORS fetch. Without a matching unexpired preflight-cache entry, the browser sends `OPTIONS` first. Streaming bodies or XHR upload listeners can require preflight too.

```
OPTIONS /v1/orders/7 HTTP/1.1
Origin: https://a.test
Access-Control-Request-Method: DELETE
Access-Control-Request-Headers: x-token

HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://a.test
Access-Control-Allow-Methods: DELETE
Access-Control-Allow-Headers: x-token
Access-Control-Max-Age: 600
```

## Key takeaways
- CORS is browser response-sharing permission, with a preflight gate for some requests.
- Methods, header values and API flags determine whether preflight permission is needed.
- A successful required preflight precedes the actual request; it does not authenticate a user.

## Further reading
- [Fetch Standard: CORS protocol](https://fetch.spec.whatwg.org/#http-cors-protocol)
