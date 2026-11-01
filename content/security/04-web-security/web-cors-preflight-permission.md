---
id: web-cors-preflight-permission
title: CORS response sharing and preflight
level: basic
minutes: 4
sourceLesson: web-sop-cors
summary: Non-safelisted CORS requests need permission before their method and headers are sent.
---

The previous unit separated *sending* a cross-origin request from *reading* its reply. CORS is how a server lets chosen other origins read its replies.

## CORS: opting in to cross-origin reads

Modern apps legitimately need cross-origin reads. A single-page app on `https://a.test` calls an API on `https://b.test`. **Cross-Origin Resource Sharing** (CORS) lets the *server* tell the browser which other origins may read its responses.

When a page makes a CORS fetch, the browser adds an `Origin` request header saying who is asking. (Not every cross-origin navigation or embed carries one.) The server answers with headers saying what it allows:

```
GET /v1/orders HTTP/1.1
Host: api.example
Origin: https://a.test

HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://a.test
Vary: Origin
```

The browser compares the allow-origin value with the page's origin:

- If it matches (or is `*` for a request without credentials), the page can read the response.
- If not, the page sees only a network error. The response did arrive; the browser just will not hand it over.
- A request sent with credentials needs more: an exact origin and `Access-Control-Allow-Credentials: true` (a later unit).

## Why CORS is not access control

CORS headers are instructions to *browsers* about sharing a reply with a web page. They do not decide who may call the API:

- A simple request (below) reaches the server and runs its handler whether or not the server sends CORS headers.
- `curl`, mobile apps and attackers' servers ignore CORS entirely and read every reply.
- Restricting `Access-Control-Allow-Origin` to your own front end does not stop a stolen token being used from a script.

So the server must still authenticate the caller and check what that caller is allowed to do. CORS only loosens the browser's read restriction; it never adds protection that the server lacked.

### Simple requests and preflights

Some cross-origin requests were always possible from plain HTML, for example a form POST. CORS lets those through without asking first, because holding them back would not stop anything a plain HTML form could already do. They can still change things on the server. A CORS fetch avoids a preflight when, in simplified terms:

- the method is `GET`, `HEAD` or `POST`;
- every header the page sets is on the CORS safelist, and each value meets that header's length and character rules (a safelisted name alone is not enough);
- `Content-Type`, if set, is `application/x-www-form-urlencoded`, `multipart/form-data` or `text/plain`.

Anything else needs permission *before* it is sent. Examples are `PUT` or `DELETE`, an `Authorization` header set by the page, or a JSON content type. Streaming request bodies and XHR upload listeners also trigger it. Unless a matching earlier approval is still cached, the browser first sends an `OPTIONS` **preflight** asking whether the real request is allowed:

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

If the preflight answer does not allow the method and headers, the browser never sends the real `DELETE`. If it does, the real request follows, and its response still needs its own allow-origin check before the page can read it.

> [!analogy] Real-world analogy: phoning ahead before an unusual delivery
> A courier delivers ordinary letters without asking. Before bringing something unusual, such as a sofa that needs a lift booked, it phones the building to check the delivery is accepted.
>
> **How it maps:** The courier is the browser, ordinary letters are simple requests, and the phone call is the `OPTIONS` preflight. The building's yes or no is the `Access-Control-Allow-*` answer; the real request goes only after a yes.
>
> **Where it stops:** The building's answer binds only this courier. Anyone delivering by another route (`curl`, a server) never phones at all. A yes also says nothing about who the sender is: it is not a login.

## Key takeaways
- CORS lets a server share responses with named origins; without it the browser hides the reply, not the request.
- Non-safelisted methods, headers or content types need a successful preflight before the real request is sent.
- CORS is not access control: non-browser clients ignore it, so the server must authenticate and authorise every request.

## Further reading
- [Fetch Standard: CORS protocol](https://fetch.spec.whatwg.org/#http-cors-protocol)
- [MDN: Cross-Origin Resource Sharing](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS)
