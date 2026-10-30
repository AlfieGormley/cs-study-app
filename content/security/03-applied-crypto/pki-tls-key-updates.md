---
id: pki-tls-key-updates
title: TLS usage limits and key updates
level: intermediate
minutes: 3
sourceLesson: pki-tls
summary: AES-GCM has a record-usage bound well before the sequence counter would wrap.
---

TLS 1.3 protects each record using AEAD and a nonce derived from a static IV plus an implicit sequence counter. A unique nonce is necessary, but the AEAD also imposes an earlier usage limit.

## How much one key may protect

AEAD keys have **usage limits**: the more data one key protects, the closer an attacker gets to the edge of the security analysis. RFC 9846 says that up to 2^24.5 full-size records, about 24 million, may be encrypted under one AES-GCM key while keeping a safety margin of roughly 2^−57 for authenticated-encryption security. At 16 KiB per record that is roughly 390 GB of data. For ChaCha20-Poly1305 the 64-bit sequence number would wrap before its safety limit is reached.

In practice, one long-lived connection streaming 50 MB/s would reach the AES-GCM figure in a little over two hours, so the limit matters for long-lived, high-volume connections such as video streams, database replication and VPN-style tunnels, not for ordinary web pages. The limit is a chosen safety margin rather than a cliff: risk grows gradually with the amount encrypted.

RFC 9846 requires an implementation to either close the connection or perform a key update before reaching these limits, and receivers should not enforce the published numbers themselves because later analysis may change them. Early (0-RTT) data cannot be rekeyed, so it must stay within the limits.

## KeyUpdate

A **KeyUpdate** message advances the sender's application traffic secret with HKDF (the `"traffic upd"` label), derives a new key and IV from it and restarts that direction's sequence number at zero, all inside the existing connection. Each direction is independent: updating what one side sends does not change what the other side sends, although a KeyUpdate can ask the peer to update its own sending keys too. Because each new secret is derived one-way from the previous one, an attacker who steals the current secret cannot work backwards to earlier ones (though they can derive later updates).

Libraries differ in whether they send KeyUpdate automatically, so check the documentation of the one you use for long-lived connections.

## Why TLS 1.3 allows only AEAD

Older TLS suites permitted CBC with a separate HMAC, traditionally MAC-then-encrypt; RFC 7366 later defined an encrypt-then-MAC extension. BEAST targeted predictable IVs in TLS 1.0, Lucky 13 exploited timing in CBC processing, and the original POODLE targeted SSL 3.0 padding. TLS 1.3 allows only AEAD.

## Key takeaways
- AES-GCM has a record-usage bound well before the sequence counter would wrap.
- High-volume, long-lived connections reach the AES-GCM allowance in hours, so they need key updates or new connections.
- KeyUpdate advances one direction's traffic secret and resets its sequence count under a new key.

## Further reading
- [TLS 1.3 — RFC 9846](https://www.rfc-editor.org/rfc/rfc9846)
- [The Illustrated TLS 1.3 Connection](https://tls13.xargs.org/)
