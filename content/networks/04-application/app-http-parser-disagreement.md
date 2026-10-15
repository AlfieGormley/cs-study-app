---
id: app-http-parser-disagreement
title: "Request smuggling and parser disagreement"
level: basic
minutes: 3
sourceLesson: app-http-wire
summary: "Different framing decisions at successive HTTP hops can leave attacker bytes for the next request."
---

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

The attacker chose `Content-Length: 13` by counting every byte after the blank line, CRLFs included:

```formula
L_CL = 3 B + 2 B + 8 B = 13 B
L_TE = 3 B + 2 B = 5 B
L_left = L_CL − L_TE = 8 B
where
L_CL: the body length the front end uses, from Content-Length: the line "0" plus its CRLF (3 bytes), the empty line's CRLF (2 bytes) and the 8 letters of SMUGGLED
L_TE: the body length the back end uses when it decodes chunked framing: the "0" chunk line and the blank line that ends it
L_left: the bytes the back end has not consumed, which stay in its buffer
B: bytes
In words: the two hops disagree by 8 bytes, and those 8 bytes become the start of whatever the back end reads next.
```

1. The front end reads 13 body bytes (`0\r\n\r\nSMUGGLED`) and forwards everything as one request.
2. The back end decodes chunked: the `0` chunk ends the body after 5 bytes.
3. `SMUGGLED` is left in the back end's buffer on the shared, persistent connection. It becomes the **start of the next request**, which may belong to a different user.

Attackers use this to poison caches, bypass front-end access controls and hijack other users' requests. Defences:

- Reject requests with both framing fields, invalid transfer-coding syntax, repeated chunked coding or a final coding other than chunked. Whitespace permitted by the grammar is not inherently malformed.
- Make every hop use the same parser rules, and close the connection after any framing error.
- Using HTTP/2 end to end removes this HTTP/1.1 delimiter disagreement, but does not excuse validation of header fields and length consistency. Translation to HTTP/1.1 needs particular care.

## Key takeaways
- Different framing decisions at successive HTTP hops can leave attacker bytes for the next request.
- Reject ambiguous framing and close after errors; protocol translation still needs validation.

## Further reading
- [RFC 9112](https://www.rfc-editor.org/rfc/rfc9112)
- [Original request-smuggling research and examples](https://portswigger.net/web-security/request-smuggling)
