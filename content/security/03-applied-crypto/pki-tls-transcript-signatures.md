---
id: pki-tls-transcript-signatures
title: Authenticating the TLS transcript
level: intermediate
minutes: 3
sourceLesson: pki-tls
summary: A trusted certificate identifies the key; CertificateVerify binds that key to this handshake.
---

Ephemeral Diffie–Hellman agrees a secret, but on its own it cannot tell you who you agreed it with. TLS 1.3 fixes that with one carefully scoped signature.

## Job 2: proving identity with a signature

ECDH gives a secret shared with *someone*. The server proves it is the right someone in two steps:

1. **Certificate**: the chain from the last lesson, binding `shop.example.com` to a public key.
2. **CertificateVerify**: a signature, with that key's private half, over the handshake so far.

What exactly is signed matters. The server signs:

```
64 bytes of 0x20 (spaces)
"TLS 1.3, server CertificateVerify"
0x00
Transcript-Hash(ClientHello ...
                Certificate)
```

The **transcript hash** covers both key shares, the client's random value and the negotiated parameters. So the signature says: "I, the owner of this certificate, took part in *this* handshake, with *these* DH values." An attacker who substitutes their own key share cannot produce a matching signature.

The odd prefix is there for **domain separation**. The 64 spaces and context string separate this signature input from other TLS roles and versions, reducing cross-protocol confusion; arbitrary external protocols must still avoid overlapping signed formats. In TLS 1.2 the server signed only the random values and its DH parameters, not the negotiated cipher suite, and that gap helped make the 2015 Logjam downgrade to 512-bit "export" Diffie–Hellman possible.

> [!analogy] Real-world analogy: Signing the minutes, not the attendance sheet
> After a negotiation, one party signs only the attendance sheet: "I was at this meeting." Someone later edits the minutes to say a much worse deal was agreed, and the signature still looks valid because it never covered the minutes.
>
> **How it maps:** TLS 1.2's server signature covered its own DH values and the two random values, roughly the attendance sheet, so Logjam could change the negotiated cipher suite underneath it. TLS 1.3's CertificateVerify signs a hash of the whole transcript so far: every offer, every choice and both key shares, like signing the complete minutes.
>
> **Where it stops:** Minutes are read by people who can spot odd wording. The transcript hash is checked mechanically: any change to any byte the server saw produces a different hash, and the client verifies against its own record of what was sent.

The signature algorithm is negotiated through the `signature_algorithms` extension. If the server's key is RSA, TLS 1.3 requires RSA-PSS here, even though the CA's signature *on* the certificate may still be PKCS#1 v1.5.

## Key takeaways
- A trusted certificate identifies the key; CertificateVerify binds that key to this handshake.
- TLS 1.3 signatures cover the transcript, including negotiation and key shares.
- Context bytes separate TLS signing roles; RSA handshake signatures use PSS.

## Further reading
- [TLS 1.3 — RFC 9846](https://www.rfc-editor.org/rfc/rfc9846)
- [TLS example traces — RFC 8448](https://www.rfc-editor.org/rfc/rfc8448)
