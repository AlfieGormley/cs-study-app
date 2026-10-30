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

The attacker chose `Content-Length: 13` by counting every byte after the blank line, CRLFs included: `0` and its CRLF (3 bytes), the empty line's CRLF (2) and the 8 letters of `SMUGGLED`. A chunked parser stops after the first 5 of those bytes. The two hops therefore disagree by 8 bytes:

1. The front end reads 13 body bytes (`0\r\n\r\nSMUGGLED`) and forwards everything as one request.
2. The back end decodes chunked: the `0` chunk ends the body after 5 bytes.
3. `SMUGGLED` is left in the back end's buffer on the shared, persistent connection. It becomes the **start of the next request**, which may belong to a different user.

> [!analogy] Real-world analogy: Two clerks counting pages differently
> A front desk accepts a bundle labelled "13 pages" and passes it to the back office as one customer's file. The back-office clerk ignores the label and stops at the sheet marked "END", which the customer slipped in after page 5. The last 8 pages stay on the clerk's desk and get stapled to the next customer's file.
>
> **How it maps:** The front desk is a proxy trusting `Content-Length`; the back office is a server using chunked framing, where the `0` chunk is the "END" sheet. The leftover pages are the bytes that become the start of the next request on the shared connection.
>
> **Where it stops:** A clerk might notice odd pages; a parser just carries on, and the attacker can shape the leftover bytes into the start of a request that merges with another user's. Conforming servers avoid the situation altogether by rejecting the ambiguous message or closing the connection.

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
