---
id: app-http-message-boundaries
title: "HTTP/1.1 messages and body boundaries"
level: basic
minutes: 3
sourceLesson: app-http-wire
summary: "HTTP/1.1 framing follows ordered rules; a TCP read is not an HTTP message."
---

HTTP/1.1 is a text protocol over an ordered TCP byte stream. TCP exposes bytes without application-message boundaries, so the receiver must determine where each message ends. Incorrect framing can hang a client, truncate content or create a security hole. HTTP semantics are shared across versions in RFC 9110; RFC 9112 specifies the HTTP/1.1 wire format.

## Anatomy of a request

The start line and header field lines end with **CRLF** (`\r\n`, bytes `0D 0A`). A blank line separates the headers from the body.

```
GET /search?q=tcp HTTP/1.1\r\n
Host: example.com\r\n
User-Agent: curl/8.5.0\r\n
Accept: */*\r\n
\r\n
```

- The **request line** is method, request target and version, separated by single spaces.
- **Header fields** are `Name: value`. Names are case-insensitive, so `content-length` and `Content-Length` are the same field.
- `Host` is **mandatory** in HTTP/1.1. A server must answer `400 Bad Request` if it is missing. It is what lets one IP address serve thousands of virtual hosts.
- A GET usually has no body, so the message ends at the blank line.

The response has the same shape, with a **status line** instead:

```
HTTP/1.1 200 OK\r\n
Content-Type: text/html\r\n
Content-Length: 1256\r\n
\r\n
<1256 bytes of body>
```

A TCP read returns whatever bytes have arrived: half a header, or the end of one response plus the start of the next. The receiver therefore needs rules that say where a message ends.

A quick inspection tool can send `Connection: close` and read until the server closes the connection. EOF alone still does not prove the response is valid or complete. Without that header, HTTP/1.1 uses **persistent connections** by default, so a read-until-close loop can sit waiting after the response has fully arrived, until a timeout or the server closes. That is exactly why message framing matters.

## Where does the body end?

RFC 9112 gives the receiver an ordered list of rules. Simplified:

1. Responses to `HEAD`, all `1xx`, `204 No Content` and `304 Not Modified` responses **never have a message body**, whatever the headers say. An informational response may precede a final response; a `101` switches protocols.
2. A successful `2xx` response to `CONNECT` starts a tunnel after the headers; ignore framing fields for its length.
3. `Transfer-Encoding` overrides `Content-Length`. Senders must not send both. Reject ambiguous requests; a forwarding intermediary that processes such a message must remove `Content-Length`.
4. If transfer coding ends in `chunked`, decode chunks. If it ends in another coding, a response is close-delimited; a request must receive `400` and the connection must close.
5. With no transfer coding, a valid `Content-Length` gives the exact byte count. Invalid or conflicting lengths are framing errors; identical repeated values have a specified normalisation exception.
6. Otherwise, a **request** has no body and a **response** is close-delimited. Complete header validation and the RFC’s error rules are still required.

Close-delimited responses are supported for compatibility and are fragile: an apparently clean connection close cannot distinguish a complete body from a prematurely ended one without additional information. HTTP/1.0 also supported Content-Length.

> [!note] Why HEAD responses carry Content-Length
> A server should send the fields it would send for GET, but may omit fields calculated only while generating content. If it sends Content-Length on HEAD, that value must describe the content an equivalent GET would send. No body follows; waiting for those bytes can block until a timeout or close.

## Key takeaways
- HTTP/1.1 framing follows ordered rules; a TCP read is not an HTTP message.
- HEAD responses carry no body, even when Content-Length describes an equivalent GET.

## Further reading
- [RFC 9112](https://www.rfc-editor.org/rfc/rfc9112)
- [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110)
