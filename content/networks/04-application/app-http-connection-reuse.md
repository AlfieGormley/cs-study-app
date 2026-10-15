---
id: app-http-connection-reuse
title: "HTTP/1.1 reuse, pipelining and upload approval"
level: basic
minutes: 3
sourceLesson: app-http-wire
summary: "Persistent connections save handshakes, while pipelined responses must remain in request order."
---

## Persistent connections and pipelining

Persistent connections are the default in HTTP/1.1; `Connection: close` opts out. Reusing a connection avoids a new TCP (and TLS) handshake per request.

**Pipelining** lets a client send several requests without waiting, but responses must come back **in order**. A slow earlier response can delay later responses. Clients can instead use parallel connections, subject to their own limits.

> [!note] Content omitted after review
> A universal browser connection count, historical default-pipelining claim and typical keep-alive timeout range are omitted because browser/server versions and configurations were not reliably established here.

One more mechanism: a client uploading a large body can send `Expect: 100-continue` and wait for an interim `100 Continue` before sending the body. If the server would reject the upload (too big, unauthorised), it can send a final error such as `413` or `401` before the body. Clients may send after a bounded wait, so Expect does not guarantee that no body bytes are transmitted.

### Trace a reusable connection

Suppose a client pipelines three GETs on one TCP connection. The first response needs two seconds of application work, while the next two are ready almost immediately. Those later responses still wait for the first response to finish: HTTP/1.1 cannot interleave their bodies. Even correct Content-Length values only identify boundaries; they do not relax response ordering. Parallel TCP connections can avoid sharing this particular response queue, but each connection has its own setup and congestion state.

When debugging an apparently idle client, distinguish an application waiting for the earlier response from a parser waiting for EOF. A length-framed response can finish while the connection remains open for reuse. Reading until close discards that distinction. Reusing a connection is safe only when the current message has been fully consumed under the framing rules. A framing error should end reuse rather than leave uncertain bytes for the next request.

## Key takeaways
- Persistent connections save handshakes, while pipelined responses must remain in request order.
- Expect: 100-continue permits early rejection but cannot guarantee that no body bytes are sent.

## Further reading
- [RFC 9112](https://www.rfc-editor.org/rfc/rfc9112)
- [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110)
