---
id: pki-tls-resumption-policy
title: TLS resumption and deployment boundaries
level: intermediate
minutes: 2
sourceLesson: pki-tls
summary: PSK-only resumption loses forward secrecy against later PSK exposure.
---

In a certificate-authenticated TLS 1.3 connection, ephemeral key agreement, signatures, HKDF and AEAD have separate jobs. This unit examines one part of that composition.

## Resumption and its trade-offs

The **resumption master secret** derives a PSK for each ticket. The ticket is an opaque identity: implementations may encrypt resumption state into it or use it to look up server-side state. NewSessionTicket is sent encrypted; a subsequent ordinary ClientHello exposes the ticket identity unless protected by ECH. A resumed handshake can skip the certificate and signature.

- With `psk_dhe_ke` mode, a fresh ECDH exchange is still mixed in, so forward secrecy is kept.
- With `psk_ke`, there is no ECDH. Anyone who later gets the PSK, or a **ticket encryption key** that recovers sufficient resumption state, can decrypt those sessions.

For stateless tickets, compromise of a key that exposes PSKs breaks recorded PSK-only resumed sessions. Fresh DH in `psk_dhe_ke` protects its 1-RTT traffic, but 0-RTT traffic still depends only on the PSK. Limit ticket lifetime and key exposure according to the implementation and threat model.

> [!note] Content gap
> Fleet-wide ticket-key reuse measurements and a universal hourly rotation rule are omitted: no reproducible deployment evidence or universally applicable policy was available for this review.

## Putting it together

```
X25519 share ---------+
                      v
        HKDF key schedule <-- transcript
            |      |            hash
   hs keys  |      | app keys    ^
            v      v             |
  {Cert, CertVerify, Finished}   |
     signature + HMAC over ------+
            |
            v
     AEAD records, seq nonces
```

Each piece protects another: the signature authenticates the ECDH values, transcript-dependent derivations and authentication bind the negotiation, HKDF separates keys by purpose and direction, and AEAD with record-counter nonces protects every byte afterwards.

## Pitfalls in practice

- **Turning off verification.** The cryptography is useless if the client skips certificate or hostname checks; ECDH then happily agrees a key with the attacker.
- **Re-enabling old versions.** TLS 1.0 and 1.1 are deprecated. Enabling them exposes clients that permit those versions; it does not automatically downgrade clients that enforce a newer minimum. Keep TLS 1.2 as the floor and prefer ECDHE with AEAD suites there.
- **Long-lived ticket keys** and **0-RTT without application-level replay safety** both trade away guarantees for speed.
- **Terminating TLS early.** TLS protects only hop to hop. Traffic decrypted at a load balancer and forwarded in plaintext is exposed on that internal hop. A historical intelligence-programme attribution is omitted here because the review did not obtain a reliable primary record supporting the specific claim.

## Key takeaways
- PSK-only resumption loses forward secrecy against later PSK exposure.
- Fresh DH protects resumed 1-RTT traffic, while 0-RTT still depends on the PSK and replay-safe application design.
- Each TLS termination point sees the plaintext at that layer; protect further hops explicitly.

## Further reading
- [TLS 1.3 — RFC 9846](https://www.rfc-editor.org/rfc/rfc9846)
- [TLS example traces — RFC 8448](https://www.rfc-editor.org/rfc/rfc8448)
- [RFC 9846: The Transport Layer Security (TLS) Protocol Version 1.3](https://www.rfc-editor.org/rfc/rfc8446)
- [RFC 8448: Example Handshake Traces for TLS 1.3](https://www.rfc-editor.org/rfc/rfc8448)
- [The Illustrated TLS 1.3 Connection](https://tls13.xargs.org/)
- [RFC 5869: HMAC-based Extract-and-Expand Key Derivation Function (HKDF)](https://www.rfc-editor.org/rfc/rfc5869)
- [The ROBOT Attack](https://robotattack.org/)
- [Chrome transition to ML-KEM](https://security.googleblog.com/2024/09/a-new-path-for-kyber-on-web.html)
