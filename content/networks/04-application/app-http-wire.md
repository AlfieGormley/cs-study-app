---
id: app-http-wire
title: HTTP/1.1 on the wire
level: basic
minutes: 14
summary: The exact bytes of an HTTP/1.1 exchange, how a receiver finds the end of a body, chunked transfer encoding, request smuggling, and the cookie attributes covered here and their security limits.
---

HTTP/1.1 is a **text protocol over a TCP byte stream**. TCP carries segments on the network but exposes an ordered byte stream without application-message boundaries. So the most important question in HTTP/1.1 is surprisingly basic: *where does one message end and the next begin?* Get that wrong and you get hung connections, truncated downloads, or a security hole.

This lesson looks at the raw bytes. The rules live in [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110) (semantics, shared by every HTTP version) and [RFC 9112](https://www.rfc-editor.org/rfc/rfc9112) (the HTTP/1.1 wire format). The System Design lessons cover why HTTP/2 and HTTP/3 exist; here we care about mechanics.

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

This bounded wire-inspection example opens a plain HTTP socket. It collects bytes until close; it does not implement a complete response parser, decode transfer codings, or authenticate the server:

```python
import socket

with socket.create_connection(
        ("example.com", 80),
        timeout=3) as s:
    s.sendall(b"GET / HTTP/1.1\r\n"
              b"Host: example.com\r\n"
              b"Connection: close\r\n"
              b"\r\n")
    reply = bytearray()
    while chunk := s.recv(4096):
        reply.extend(chunk)
        if len(reply) > 1_000_000:
            raise ValueError("demo limit")
head, sep, body = bytes(reply).partition(
    b"\r\n\r\n")
if not sep:
    raise ValueError("incomplete headers")
print(head.split(b"\r\n")[0])
# Example: b'HTTP/1.1 200 OK'
# Actual status depends on the server.
```

`Connection: close` asks the server to close the TCP connection after the response, so EOF can end this inspection loop when the peer complies. EOF alone does not establish a valid or complete response. Without it, HTTP/1.1 connections are **persistent** by default, so a read-until-close loop can wait after the response is complete. Timeouts and server policy still apply. That is exactly why message framing matters.

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

## Chunked transfer encoding

`Content-Length` must be known *before* the first body byte is sent. That is a problem for anything generated on the fly: a streamed template, a database export, a proxied upstream, a long-poll. Without a length, the server could only signal the end by closing the connection, losing persistence.

**Chunked encoding** solves this. The body is sent as a sequence of chunks, each prefixed by its size **in hexadecimal**, and a zero-size chunk marks the end:

```
HTTP/1.1 200 OK\r\n
Transfer-Encoding: chunked\r\n
\r\n
7\r\n
Mozilla\r\n
11\r\n
Developer Network\r\n
0\r\n
\r\n
```

`11` is hex, so that chunk is 17 bytes ("Developer Network"). The decoded body is `MozillaDeveloper Network`, 24 bytes. The CRLF after each chunk's data is framing, not content.

A deliberately restricted decoder for an already-buffered, bounded message with **no extensions or trailers**. It rejects those unsupported forms and returns any following bytes separately. Production receivers must handle the full grammar and incremental input.

```python
import re

def read_chunked(buf):
    if len(buf) > 1_000_000:
        raise ValueError("demo limit")
    parts = []
    while True:
        line, sep, buf = buf.partition(
            b"\r\n")
        if not sep or not re.fullmatch(
                rb"[0-9A-Fa-f]+", line):
            raise ValueError("bad size")
        size = int(line, 16)
        if size == 0:
            if not buf.startswith(b"\r\n"):
                raise ValueError(
                    "bad terminator")
            return b"".join(parts), buf[2:]
        if (len(buf) < size + 2
                or buf[size:size + 2]
                != b"\r\n"):
            raise ValueError("bad chunk")
        parts.append(buf[:size])
        buf = buf[size + 2:]
```

Details worth knowing:

- **Trailers.** After the `0` chunk, the sender may add header fields before the final blank line, for example a checksum computed while streaming. gRPC relies on trailers to send its status (lesson 5). Many HTTP/1.1 clients and browsers ignore them.
- **Chunk extensions** (`7;name=value`) can carry per-chunk metadata. A conforming receiver ignores unrecognised extensions after parsing their syntax and imposing suitable limits.
- Chunks have nothing to do with TCP segments. A 7-byte chunk may arrive split across two `recv` calls, and ten chunks may arrive in one. A real parser is a state machine fed arbitrary slices.
- HTTP/2 and HTTP/3 **forbid** `Transfer-Encoding`. Both have length-delimited DATA frames. HTTP/2 signals message completion with END_STREAM; HTTP/3 uses the end of its underlying QUIC stream, not a DATA-frame END_STREAM flag.

## Request smuggling: when framing disagrees

What if a request has **both** `Content-Length` and `Transfer-Encoding: chunked`? RFC 9112 gives transfer coding precedence, recommends treating the combination as an error, and requires connection closure after responding if a server elects to process such a request. But when a front-end proxy and a back-end server pick *different* rules, an attacker can hide one request inside another. This is **HTTP request smuggling**.

The classic **CL.TE** variant below assumes vulnerable hops: the front end trusts Content-Length, the back end parses chunks and improperly keeps the connection reusable. Lines use CRLF, but the final `SMUGGLED` bytes have **no trailing CRLF**. This is a boundary illustration, not a complete valid second request.

```
POST / HTTP/1.1
Host: shop.example
Content-Length: 13
Transfer-Encoding: chunked

0

SMUGGLED
```

1. The front end reads 13 body bytes (`0\r\n\r\nSMUGGLED`) and forwards everything as one request.
2. The back end decodes chunked: the `0` chunk ends the body after 5 bytes.
3. `SMUGGLED` is left in the back end's buffer on the shared, persistent connection. It becomes the **start of the next request**, which may belong to a different user.

Attackers use this to poison caches, bypass front-end access controls and capture other users' requests. Defences:

- Reject requests with both framing fields, invalid transfer-coding syntax, repeated chunked coding or a final coding other than chunked. Whitespace permitted by the grammar is not inherently malformed.
- Make every hop use the same parser rules, and close the connection after any framing error.
- Using HTTP/2 end to end removes this HTTP/1.1 delimiter disagreement, but does not excuse validation of header fields and length consistency. Translation to HTTP/1.1 needs particular care.

## Persistent connections and pipelining

Persistent connections are the default in HTTP/1.1; `Connection: close` opts out. Reusing a connection avoids a new TCP (and TLS) handshake per request.

**Pipelining** lets a client send several requests without waiting, but responses must come back **in order**. A slow earlier response can delay later responses. Clients can instead use parallel connections, subject to their own limits.

> [!note] Content omitted after review
> A universal browser connection count, historical default-pipelining claim and typical keep-alive timeout range are omitted because browser/server versions and configurations were not reliably established here.

One more mechanism: a client uploading a large body can send `Expect: 100-continue` and wait for an interim `100 Continue` before sending the body. If the server would reject the upload (too big, unauthorised), it can send a final error such as `413` or `401` before the body. Clients may send after a bounded wait, so Expect does not guarantee that no body bytes are transmitted.

## Cookies: state on a stateless protocol

HTTP semantics are stateless; applications and connections can still maintain state. **Cookies** ([RFC 6265](https://www.rfc-editor.org/rfc/rfc6265), being revised as "6265bis") add state: the server sets a name/value pair, and the browser sends it back on later requests.

```
HTTP/1.1 200 OK
Set-Cookie: sid=a3f9; Path=/; Secure;
  HttpOnly; SameSite=Lax; Max-Age=3600
```

(Shown wrapped; on the wire it is one line.) Later requests carry only the name/value pairs, never the attributes:

```
Cookie: sid=a3f9; theme=dark
```

One quirk: combining repeated field lines is allowed only when the field definition permits it. `Set-Cookie` **must not be folded into one comma-separated field**, because cookie dates (`Expires=Wed, 21 Oct...`) contain commas. Each cookie needs its own `Set-Cookie` line.

### The attributes

| Attribute | Effect |
|---|---|
| `Expires` / `Max-Age` | Lifetime; none means session cookie |
| `Domain` | Widen scope to subdomains |
| `Path` | Only send under this path |
| `Secure` | Send only over connections the browser considers secure |
| `HttpOnly` | Exclude from non-HTTP cookie APIs such as document.cookie |
| `SameSite` | Control cross-site sending |
| `Partitioned` | Add a top-level-site partition key in supporting browsers; requires Secure |

**Lifetime.** `Max-Age` (seconds) takes precedence over `Expires` (a date) if both appear. With neither, the cookie is a *session cookie*, deleted when the browser session ends (though "restore tabs" features often keep them). To delete a cookie, set it again with `Max-Age=0` and matching name, domain/host-only scope and path, in the same partition if applicable.

**Domain.** If you *omit* `Domain`, the cookie is **host-only**: set by `app.example.com`, it goes only to `app.example.com`. Setting `Domain=example.com` allows host matching for `example.com` *and its subdomains*, subject to path, security, SameSite and browser policy. The setting host must domain-match that Domain value. Counter-intuitively, omitting `Domain` is the stricter choice. Public-suffix rejection prevents a tenant from setting a parent-suffix cookie for other tenants. The algorithm has a host-only exception when the setting host itself equals the suffix; lists and browser policy matter.

**Path** limits which URLs receive the cookie, but it is **not a security boundary**: same-origin script may access a matching-path document, subject to framing policy. Path does not isolate mutually distrustful applications on one origin; HttpOnly separately restricts script cookie access.

**Secure** normally requires HTTPS; browsers may treat localhost as a trusted exception. **HttpOnly** prevents direct access through document.cookie and similar non-HTTP APIs. It does not guarantee that XSS cannot expose a token through another vulnerable application feature, and injected script can still make authenticated requests.

### SameSite and the meaning of "site"

For these ordinary domain URLs, a schemeful **site** is the scheme plus the *registrable domain* (eTLD+1): `https://shop.example.co.uk` and `https://api.example.co.uk` are the **same site**, though different origins.

- `Strict`: sent only on same-site requests. On a cross-site navigation, that cookie is withheld from the initial request; what the user sees depends on application behaviour.
- `Lax`: also sent on **top-level navigations** with safe methods (clicking a link, a GET form). Not sent on cross-site `POST`s, iframes, images or `fetch`.
- `None`: removes the SameSite restriction and requires Secure in supporting browsers. Domain/path rules, partitioning and third-party-cookie policies still apply.

The 6265bis draft specifies Lax-style default enforcement and allows a user-agent-chosen recent-cookie exception for cookies with no explicit SameSite value. Explicit Lax excludes that exception. SameSite helps against cross-site CSRF, but does not cover same-site sibling attacks or all application flows. Use appropriate CSRF protection for state-changing requests; GET should not perform state changes.

### Prefixes

Supporting browsers enforce cookie-name prefixes:

- `__Secure-name`: must be set with `Secure` from an HTTPS page.
- `__Host-name`: must be `Secure`, have `Path=/` and **no** `Domain`. This prevents a sibling from setting a parent-domain cookie under that prefixed name. It does not isolate ports on the same host or authenticate a Cookie header supplied by an arbitrary client.

> [!tip] A good session cookie
> `Set-Cookie: __Host-sid=<random>; Path=/; Secure; HttpOnly; SameSite=Lax`

### Limits

RFC 6265 asks browsers to support **at least** 4096 bytes per cookie, 50 cookies per domain and 3000 in total, as recommended minimum capabilities in that RFC, not universal current limits. Cookie inclusion also depends on path, security, SameSite, credentials mode and browser policy. For 80 actual HTTP/1.1 requests each carrying 3,000 cookie bytes, the repeated values total 240,000 bytes before other overhead. Cache hits can avoid requests; HTTP/2 or HTTP/3 compression savings depend on encoder/table decisions.

> [!note] Content omitted after review
> A current browser-by-browser cookie limit, prefix-support and eviction-policy matrix is absent because those version-specific implementations were not tested here.

## Pitfalls

- **Hand-rolled parsers.** Reading until close, ignoring `HEAD`/`304` rules or trusting chunk boundaries to match `recv` calls are classic bugs.
- **Mixed framing headers.** Any hop that accepts both `Content-Length` and `Transfer-Encoding` is a smuggling risk.
- **`Domain=` by habit.** It widens scope to every subdomain, including the forgotten staging box.
- **Treating cookie attributes as complete XSS protection.** HttpOnly is a real restriction on cookie APIs, but does not prevent injected script from making authenticated requests. Path is not an isolation boundary.

## Key takeaways
- HTTP/1.1 is CRLF-delimited text on a TCP stream; the hard problem is knowing where each message ends.
- Apply the ordered framing and error rules: special bodyless responses and CONNECT tunnels come before transfer coding, valid Content-Length and applicable close-delimiting.
- Chunked encoding sends hex-sized chunks ending in a `0` chunk, allowing streaming on persistent connections, with optional trailers.
- When proxies and servers disagree on framing, request smuggling becomes possible; reject ambiguous requests.
- Omit `Domain` for host-only cookies, use `Secure`, `HttpOnly` and `SameSite`, and prefer the `__Host-` prefix for session cookies.

## Further reading
- [RFC 9112: HTTP/1.1 — IETF](https://www.rfc-editor.org/rfc/rfc9112)
- [Transfer-Encoding — MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Transfer-Encoding)
- [HTTP request smuggling — PortSwigger Web Security Academy](https://portswigger.net/web-security/request-smuggling)
- [Using HTTP cookies — MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies)
- [RFC 6265: HTTP State Management Mechanism — IETF](https://www.rfc-editor.org/rfc/rfc6265)
- [SameSite cookies explained — web.dev](https://web.dev/articles/samesite-cookies-explained)

- [Cookie revision draft: scope, SameSite and prefixes](https://httpwg.org/http-extensions/draft-ietf-httpbis-rfc6265bis.html)
- [CHIPS: partitioned cookies](https://privacysandbox.google.com/cookies/chips)
