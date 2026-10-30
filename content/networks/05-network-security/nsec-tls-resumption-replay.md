---
id: nsec-tls-resumption-replay
title: Session resumption and early-data replay
level: intermediate
minutes: 3
summary: A session ticket identifies a resumption PSK; it is not simply the raw key.
sourceLesson: nsec-tls
---

A full TLS handshake establishes secrets that may support a later resumed connection. The shortcut matters because sending application data before that later handshake finishes changes the security guarantees.

Consider two operations at a shop: viewing a public catalogue and charging a card. Repeating a catalogue read may be acceptable under the application’s stated semantics. Repeating an unprotected charge is not. Naming an endpoint GET or POST does not prove which side of that boundary it belongs on.

## Resumption and 0-RTT

After a handshake, the server can issue a **session ticket**: an opaque identity associated with a resumption PSK. The client derives that PSK from resumption secrets and the ticket nonce; the ticket is not simply the raw key. A resumed handshake skips the certificate.

With a ticket, the client may also send **0-RTT early data** in its very first flight, encrypted with a key derived from the PSK. The catch is serious:

> [!warning] 0-RTT data can be replayed
> An attacker can capture the first flight and send it again. TLS does not inherently guarantee non-replay of early data. Servers can implement anti-replay state, but applications must account for the remaining risk across instances and retries. Early data lacks forward secrecy against later compromise of its PSK. Permit only requests whose actual semantics tolerate replay; an HTTP method label or idempotence alone is not a complete safety argument. A server can answer HTTP `425 Too Early` to make the client retry after the full handshake.

This revisits the earlier threat units’ replay problem, accepted deliberately in exchange for speed.

## Key takeaways
- A session ticket identifies a resumption PSK; it is not simply the raw key.
- 0-RTT early data has replay and forward-secrecy limitations.
- Permit early data only when the actual operation tolerates the remaining replay risk.

## Further reading
- [RFC 9846: TLS 1.3, 0-RTT and anti-replay](https://www.rfc-editor.org/rfc/rfc9846.html)
- [RFC 8470: Using Early Data in HTTP](https://www.rfc-editor.org/rfc/rfc8470)
