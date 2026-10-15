---
id: pki-tls-ephemeral-agreement
title: TLS primitives and ephemeral key agreement
level: intermediate
minutes: 3
sourceLesson: pki-tls
summary: Certificate-authenticated TLS combines key agreement, authentication, derivation and authenticated record encryption.
---

TLS is widely deployed to protect network connections. It takes the primitives from the cryptographic-primitives, signature and certificate units, Diffie–Hellman, signatures, certificates, hashes, HMAC, HKDF and AEAD, and wires them together so each one covers a gap the others leave.

The Networks subject walks through the TLS 1.3 handshake message by message (see *TLS 1.3, certificates, ECH and mTLS*). This lesson takes the opposite view: for each primitive, what job does it do, exactly which bytes does it touch, and what goes wrong without it?

## Four jobs, four primitives

This example uses certificate authentication and X25519. TLS 1.3 also supports other groups and PSK authentication; PSK-only mode does not provide forward secrecy. The example has four jobs:

| Job | Primitive in TLS 1.3 |
|---|---|
| Agree a secret | Ephemeral ECDH (X25519) |
| Prove who the server is | Certificate + signature |
| Turn secrets into keys | HKDF + transcript hash |
| Protect the data | AEAD (AES-GCM, ChaCha20) |

Take any one away and the channel breaks:

- **No key agreement**: nothing to encrypt with.
- **No authentication**: Diffie–Hellman with an unauthenticated peer is Diffie–Hellman with whoever is in the middle. An attacker runs one exchange with you and another with the server and relays.
- **No transcript binding**: an attacker can tamper with negotiation (strip strong options) and nobody notices.
- **No AEAD**: records can be read or modified.

## Job 1: key agreement with ephemeral ECDH

In its first message the client sends a fresh X25519 public key; the server replies with its own. Each side combines its private key with the other's public key and gets the same 32-byte shared secret. Both key pairs are thrown away after the handshake.

That "thrown away" is the point. TLS 1.2 also allowed **RSA key transport**: the client picked a secret, encrypted it with the server's long-term RSA public key, and sent it. Anyone who later obtained that RSA private key, through a breach or a court order, could decrypt every recorded session. RSA decryption on the server was also an oracle: the 2017 ROBOT attack showed many servers still leaked Bleichenbacher-style padding errors, nearly 20 years after the original attack.

TLS 1.3 removed RSA key transport entirely. Certificate-authenticated handshakes use ephemeral (EC)DH, providing **forward secrecy** when ephemeral secrets are securely erased: stealing the certificate key tomorrow does not decrypt today's traffic.

> [!note] Hybrid post-quantum key exchange
> A future quantum computer could solve the discrete-log problem behind X25519, and traffic recorded now could be decrypted then ("harvest now, decrypt later"). Chrome introduced **X25519MLKEM768** in version 131: an X25519 share and an ML-KEM-768 share in one key-share entry (about 1.2 KB from the client). Both shared secrets feed the key schedule. With the specified combiner and correct implementations, either component remaining secure protects the combined exchange. Chrome announced the transition from its earlier Kyber draft to ML-KEM in September 2024.

## Key takeaways
- Certificate-authenticated TLS combines key agreement, authentication, derivation and authenticated record encryption.
- Erased ephemeral secrets protect earlier ECDHE traffic from certificate-key theft alone.
- Hybrid key exchange protects confidentiality under its combiner assumptions; it does not replace certificate signatures.

## Further reading
- [TLS 1.3 — RFC 9846](https://www.rfc-editor.org/rfc/rfc9846)
- [TLS example traces — RFC 8448](https://www.rfc-editor.org/rfc/rfc8448)
