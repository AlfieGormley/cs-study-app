---
id: nsec-tls-security-properties
title: TLS protection and forward secrecy
level: intermediate
minutes: 3
summary: TLS protects connection contents, not every observable address, size or timing signal.
sourceLesson: nsec-tls
---

TLS (Transport Layer Security) is the protocol behind the padlock: HTTPS and configured secure SMTP/IMAP use TLS. QUIC version 1 uses the TLS 1.3 handshake for authentication and key establishment, while QUIC applies its own packet protection. The earlier threat units showed that encryption alone does not stop a man-in-the-middle; you also need to know *who* you are talking to. Correctly configured TLS can provide both; peer verification and the negotiated authentication mode matter.

These TLS units take the network engineer's view: what is on the wire, what each message proves, and what goes wrong in production. How the ciphers and key exchanges work mathematically is covered in the Security & Cryptography subject.

## What TLS does and does not protect

TLS gives a connection three properties:

- **Confidentiality**: only the two endpoints can read the data.
- **Integrity**: protected records reject unauthorised changes under the cryptographic assumptions; this does not prevent packet loss, delay or all denial of service.
- **Authentication**: in the certificate-based mode illustrated in the next unit, the client validates the server identity and proof of its private key. PSK modes use a different credential. Client certificate authentication is optional (mTLS, covered later).

It does **not** hide:

- IP addresses and ports (they are in the IP and TCP headers).
- Sizes and timing of records, which can leak which page you visited.
- Traditionally, the hostname, sent in clear in the **SNI** (Server Name Indication) extension so a server hosting many sites knows which certificate to present. ECH can hide the inner SNI; a later unit covers its remaining metadata limits.

## Why TLS 1.3 was needed

The pre-TLS-1.3 ecosystem retained legacy protocol versions, cipher suites and implementations with weaknesses. TLS 1.2 CBC suites were exposed to timing and padding-oracle implementation attacks; original POODLE targeted SSL 3.0. RSA key transport also lacks forward secrecy: later compromise of its decryption key can expose recorded handshakes using that key. A conventional full TLS 1.2 handshake takes two TLS round trips before client application data, excluding TCP setup and False Start.

TLS 1.3 was originally specified by RFC 8446 (2018), now superseded by RFC 9846 (July 2026). Its core redesign took a hard line:

| Removed | Why |
|---|---|
| RSA key transport, static DH | No forward secrecy |
| CBC modes, RC4 | Padding and bias attacks |
| SHA-1, MD5 in signatures | Hash collisions |
| Compression | CRIME attack |
| Renegotiation | Complex, attacked |

What is left is small. RFC 8446 originally defines five cipher suites, all **AEAD** (authenticated encryption), the common ones being `TLS_AES_128_GCM_SHA256`, `TLS_AES_256_GCM_SHA384` and `TLS_CHACHA20_POLY1305_SHA256`. Certificate-authenticated TLS 1.3 uses ephemeral key establishment. RFC 8446 also permits PSK-only `psk_ke`, which lacks forward secrecy against later PSK compromise; PSK with ephemeral DH can provide it for post-handshake traffic. The later resumption unit covers early data’s separate limitations. Secure erasure of ephemeral/session secrets is part of the model.

## Key takeaways
- TLS protects connection contents, not every observable address, size or timing signal.
- TLS 1.3 removed legacy choices and separates record protection from key exchange.
- Forward secrecy depends on the negotiated mode and erasure of temporary secrets.

## Further reading
- [RFC 9846: TLS 1.3 (2026 revision)](https://www.rfc-editor.org/rfc/rfc9846.html)
- [RFC 8446: original TLS 1.3 specification](https://www.rfc-editor.org/rfc/rfc8446)
- [The Illustrated TLS 1.3 Connection](https://tls13.xargs.org/)
- [RFC 9849: TLS Encrypted Client Hello](https://www.rfc-editor.org/rfc/rfc9849.html)
- [Ballot SC081v3: reducing certificate validity periods — CA/Browser Forum](https://cabforum.org/2025/04/11/ballot-sc081v3-introduce-schedule-of-reducing-validity-and-data-reuse-periods/)
- [Certificate Transparency — MDN](https://developer.mozilla.org/en-US/docs/Web/Security/Certificate_Transparency)
- [ssl: TLS/SSL wrapper for socket objects — Python docs](https://docs.python.org/3/library/ssl.html)
